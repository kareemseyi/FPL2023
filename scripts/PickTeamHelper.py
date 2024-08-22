# FPL
import matplotlib.pyplot as plt
# plt.style.use('seaborn-whitegrid')
from matplotlib.pyplot import figure
import csv


import aiohttp
import sys
import asyncio
import requests
from prettytable import PrettyTable
import datetime

url = "https://fantasy.premierleague.com/api/bootstrap-static/"
json_general = requests.get(url).json()
print(json_general.keys())
# print(json_general["elements"][15])
# json_general["elements"] -- List of Player information, each item in list is a player with metadata

print(json_general["element_types"])

name_list = [str(player["first_name"] + ' ' + player['second_name']) for player in json_general["elements"]]
# print(name_list)
# print((name_list))
player_id_list = [player["id"] for player in json_general["elements"]]
teamname_list = [team["name"] for team in json_general["teams"]]
teamid_list = [team["id"] for team in json_general["teams"]]
roi_list = []
teamid_list_g = []
pos_list_g = []
data_dict = []

# star_players = ['Grealish', 'Watkins', 'Werner', 'Calvert-Lewin', 'Vardy', 'Bamford', 'Harrison', 'Mané', 'Salah',
#                 'De Bruyne', 'Sterling', 'Borges Fernandes', 'Rashford', 'Wilson', 'Kane', 'Son', 'Pereira']

id_dict = {}
# Dictionary of team_ids and Team
team_dict = {json_general["teams"][i]["id"]: json_general["teams"][i]["name"] for i in range(len(teamname_list))}
player_dict = {player_id_list[i]: name_list[i] for i in range(len(name_list))}
print(name_list)
print(player_dict)


# async def get_element(session, element_id):
#     url = f"https://fantasy.premierleague.com/api/element-summary/{str(element_id)}/"
#     async with session.get(url, headers={"User-Agent": ""}) as response:
#         data = await response.json()
#         return element_id, data["fixtures"]


def get_team(team_id):
    return team_dict.get(team_id)


sorted_players = json_general["elements"]
players_table = PrettyTable()
players_table.field_names = ["Player_Name", "Price (Pounds)", "Games Played", "Goals", "Assists",
                             "Direct Goal Contributions",
                             "Total Points", "Points Per Game", "ROI", "Position", "Team", "Minutes"]
players_table.align = "c"
for baller in sorted_players:
    goals = baller['goals_scored']
    assists = baller['assists']
    goal_contributions = baller['goals_scored'] + baller['assists']
    games_played = baller['starts']
    minutes = baller['minutes']


    teamname = get_team(baller['team'])
    roi = float(f"{(baller['total_points'] / (baller['now_cost'] / 10)):0000000.4}")
    roi_per_gw = roi/games_played if games_played > 0 else 0
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
    pos_list_g.append(pos)

    diction = {
        'name': baller['web_name'],
        'price': f"£{baller['now_cost'] / 10}",
        'team': teamname,
        'goals': int(goals),
        'assists': int(assists),
        'goal_contributions': int(goal_contributions),
        'games_played': int(games_played),
        'minutes': int(minutes),
        'total_points': int(baller['total_points']),
        'points_per_game': float(baller['points_per_game']),
        'roi': float(roi),
        'roi_per_gw': float(roi_per_gw),
        'position': pos
    }

    data_dict.append(diction)

    keys = data_dict[0].keys()
    with open('FPL_data.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_dict)

    players_table.add_row([baller['web_name'], f"£{baller['now_cost'] / 10}", games_played,
                           goals, assists, goal_contributions, baller['total_points'], baller['points_per_game']
                           , float(roi), pos, teamname, minutes])




players_table.reversesort = True
# print(players_table.get_string(sortby='ROI'))
print(players_table.get_string(sortby='ROI'))
figure(num=1, figsize=(10, 6), dpi=80)

# plt.xticks(teamid_list, teamname_list, rotation=90)
# plt.yticks(range(0, 35, 5))
# plt.ylabel('Player Return on Investment')
# plt.title('Player ROI per Team')
# plt.plot(teamid_list_g, roi_list, 'o', color='blue')  # Plot some data on the axes.
# plt.show()
#
# plt.xticks(teamid_list, teamname_list, rotation=90)
# plt.yticks(range(0, 35, 5))
# plt.ylabel('Player Return on Investment > Average(ROI)')
# plt.plot(teamlist_over_avg, roi_list_over_avg, 'o', color='green')  # Plot some data on the axes.
# plt.show()

# plt.xticks(teamid_list, teamname_list, rotation=90)
# plt.yticks(range(0, 35, 5))
# plt.ylabel('Player Return on Investment < Average(ROI)')
# plt.plot(teamlist_under_avg, roi_list_under_avg, 'o', color='red')  # Plot some data on the axes.
# plt.show()

# plt.xticks(teamid_list, teamname_list, rotation=90)
# plt.yticks(range(0, 35, 5))
# plt.ylabel('Player Return on Investment > Average(ROI)')
# plt.plot(teamlist_over_25, roi_list_over_25, 'o', color='purple')  # Plot some data on the axes.
# plt.show()
#
# plt.xticks(range(1, 5, 1), ["GK", "FWD", "MID", "DEF"], rotation=90)
# plt.yticks(range(0, 35, 1))
# plt.ylabel('Player Return on Investment vs Position ')
# plt.plot(pos_list_g, roi_list, 'o', color='orange')  # Plot some data on the axes.
# plt.show()
