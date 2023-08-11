# FPL
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
from matplotlib.pyplot import figure

from fpl import FPL
import aiohttp
import sys
import asyncio
import requests
from prettytable import PrettyTable

url = "https://fantasy.premierleague.com/api/bootstrap-static/"
json_general = requests.get(url).json()
print(json_general)
name_list = [player["web_name"] for player in json_general["elements"] if player['news'] != ""]
name_list = [player["news"] for player in json_general["elements"] if player['news'] != ""]
print(name_list)
id_list = [player["id"] for player in json_general["elements"]]
teamname_list = [team["name"] for team in json_general["teams"]]
teamid_list = [team["id"] for team in json_general["teams"]]
roi_list = []
roi_list_over_15, teamlist_over_15 = [], []
roi_list_over_avg, teamlist_over_avg = [], []
roi_list_under_avg, teamlist_under_avg = [], []
roi_list_over_25, teamlist_over_25 = [], []
teamid_list_g = []
pos_list_g = []

star_players = ['Grealish', 'Watkins', 'Werner', 'Calvert-Lewin', 'Vardy', 'Bamford', 'Harrison', 'Mané', 'Salah',
                'De Bruyne', 'Sterling', 'Borges Fernandes', 'Rashford', 'Wilson', 'Kane', 'Son', 'Pereira']

id_dict = {}
# Dictionary of team_ids and Team
team_dict = {json_general["teams"][i]["id"]: json_general["teams"][i]["name"] for i in range(len(teamname_list))}


# async def get_element(session, element_id):
#     url = f"https://fantasy.premierleague.com/api/element-summary/{str(element_id)}/"
#     async with session.get(url, headers={"User-Agent": ""}) as response:
#         data = await response.json()
#         return element_id, data["fixtures"]


def get_team(team_id):
    return team_dict.get(team_id)


async def main():
    session = aiohttp.ClientSession()
    fpl = FPL(session)
    players = await fpl.get_players()
    # print(players)
    sorted_players = sorted(players, key=lambda x: x.goals_scored + x.assists, reverse=True)
    players_table = PrettyTable()
    players_table.field_names = ["Player_Name", "Price (Pounds)", "Games Played", "Goals", "Assists",
                                 "Direct Goal Contributions",
                                 "Total Points", "Points Per Game", "ROI", "Position", "Team"]
    players_table.align = "c"
    for baller in sorted_players:
        goals = baller.goals_scored
        assists = baller.assists
        goal_contributions = baller.goals_scored + baller.assists
        games_played = 0

        teamname = get_team(baller.team)
        roi = float(f"{(baller.total_points / (baller.now_cost / 10)):0000000.4}")
        roi_list.append(roi)  # add all ROIs for all players
        teamid_list_g.append(baller.team)

        if baller.element_type == 1:
            pos = 'GK'
        elif baller.element_type == 2:
            pos = 'DEF'
        elif baller.element_type == 2:
            pos = 'MID'
        else:
            pos = 'FWD'
        pos_list_g.append(pos)

        if 15 < roi < 25:
            roi_list_over_15.append(roi)
            teamlist_over_15.append(baller.team)
        if roi > 25:
            roi_list_over_25.append(roi)
            teamlist_over_25.append(baller.team)
        if roi > 12.66:  # Calculated ROI average where ROI > 0
            roi_list_over_avg.append(roi)
            teamlist_over_avg.append(baller.team)
        if roi < 12.66:
            roi_list_under_avg.append(roi)
            teamlist_under_avg.append(baller.team)

        players_table.add_row([baller.web_name, f"£{baller.now_cost / 10}", games_played,
                               goals, assists, goal_contributions, baller.points_per_game,
                               baller.total_points, float(roi), pos, teamname])

    # roi_list_over_zero = list(filter(lambda x: x > 0, roi_list))
    # roi_avg_over_zero = sum(roi_list_over_zero) / len(roi_list_over_zero)
    # print(roi_avg_over_zero)

    # roi_avg = sum(roi_list) / len(roi_list)
    # print(roi_avg)

    players_table.reversesort = True
    # print(players_table.get_string(sortby='ROI'))
    await session.close()
    print(players_table.get_string(sortby='ROI'))
    figure(num=1, figsize=(8, 6), dpi=80)

    plt.xticks(teamid_list, teamname_list, rotation=90)
    plt.yticks(range(0, 35, 5))
    plt.ylabel('Player Return on Investment')
    plt.title('Player ROI per Team')
    plt.plot(teamid_list_g, roi_list, 'o', color='blue')  # Plot some data on the axes.
    plt.show()
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
    plt.xticks(range(1, 5, 1), ["GK", "FWD", "MID", "DEF"], rotation=90)
    plt.yticks(range(0, 35, 1))
    plt.ylabel('Player Return on Investment vs Position ')
    plt.plot(pos_list_g, roi_list, 'o', color='orange')  # Plot some data on the axes.
    plt.show()


if sys.version_info >= (3, 7):
    # Python 3.7+
    asyncio.run(main())
# else:
#     # Python 3.6
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
