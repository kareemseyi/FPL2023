from matplotlib.pyplot import figure
import utils
import asyncio
from historical import historical
import csv
from endpoints import endpoints
import requests
from prettytable import PrettyTable
from api.FPL import FPL
import aiohttp

roi_list = []
teamid_list_g = []
data_dict = []
id_dict = {}
url = endpoints['STATIC']['BASE_URL']
json_general = requests.get(url).json()
team_dict = utils.get_teams()
name_list = [str(player["first_name"] + ' ' + player['second_name']) for player in json_general["elements"]]
player_id_list = [player["id"] for player in json_general["elements"]]
teamname_list = [team["name"] for team in json_general["teams"]]
player_dict = {player_id_list[i]: name_list[i] for i in range(len(name_list))}




def get_team(team_id):
    return team_dict.get(team_id)

def prepareData():
    sorted_players = json_general["elements"]
    for baller in sorted_players:
        goals = baller['goals_scored']
        assists = baller['assists']
        goal_contributions = baller['goals_scored'] + baller['assists']
        games_played = baller['starts']
        minutes = baller['minutes']

        teamname = get_team(baller['team'])
        roi = float(f"{(baller['total_points'] / (baller['now_cost'] / 10)):000.4}")
        roi_per_gw = roi / games_played if games_played > 0 else 0
        roi_list.append(roi)  # add all ROIs for all players
        teamid_list_g.append(baller['team'])

        if baller['element_type'] == 1:
            pos = 'GK'
        elif baller['element_type'] == 2:
            pos = 'DEF'
        elif baller['element_type'] == 3:
            pos = 'MID'
        else:
            pos = 'FWD'

        diction = {
            'name': baller['web_name'],
            'price': round(baller['now_cost'] / 10, 2),
            'games_played': int(games_played),
            'goals': int(goals),
            'assists': int(assists),
            'goal_contributions': int(goal_contributions),
            'total_points': int(baller['total_points']),
            'points_per_game': float(baller['points_per_game']),
            'roi': float(roi),
            'position': pos,
            'team': teamname,
            'minutes': int(minutes),
            'FDR_Ave': 0
        }

        data_dict.append(diction)
    return data_dict

def show_table(dict):
    players_table = PrettyTable()
    players_table.field_names = ["Player_Name", "Price (Pounds)", "Games Played", "Goals", "Assists",
                                 "Direct Goal Contributions",
                                 "Total Points", "Points Per Game", "ROI", "Position", "Team", "Minutes", "FDR_Ave"]
    players_table.align = "c"
    players_table.reversesort = True
    for _ in dict:
        players_table.add_row(_.values())
    figure(num=1, figsize=(10, 6), dpi=80)
    return players_table.get_string(sortby='ROI')


async def getData():
    session = aiohttp.ClientSession(trust_env=True)
    fpl = FPL(session)
    await fpl.login()
    next_gw = await fpl.get_upcoming_gameweek()

    fixtures = await fpl.get_all_fixtures(*range(1, next_gw))
    f, s = historical.getFormDict(fixtures=fixtures)
    print(f)
    g = historical.get_FDR(form_dict=f, fixtures=fixtures)

    dict = prepareData()
    print(show_table(dict))

    for _ in dict:
        if _['team'] in g.keys():
            _['FDR_Ave'] = round(g[_['team']], 3)
            _.pop('name')  # Removing Name from Training Data
    keys = dict[0].keys()
    with open(f'../datastore/current/FPL_data_{next_gw}.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dict)
    await session.close()

asyncio.run(getData())


