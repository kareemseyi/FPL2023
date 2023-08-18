import csv

import sys
import asyncio
import requests
# from prettytable import PrettyTable
#
# players_table_2021 = PrettyTable()
# players_table_2021.field_names = ["Player_Name", "Price (Pounds)", "Goals", "Assists", "Direct Goal Contribution",
#                                   "Total Points", "ROI", "Position", "Team"]
# star_players = []
#
# with open('../raw_player_data/cleaned_players_2022_2023.csv') as f:
#     print(f.name)
#     reader = csv.reader(f)
#     headers = next(reader)
#     print(headers)
#     for row in reader:
#         player_fullname = row[0] + " " + row[1]
#         player_name = row[1]
#         goals = int(row[2])
#         assists = int(row[3])
#         goal_contributions = goals + assists
#         price = int(row[-2]) / 10
#         points = int(row[4])
#         roi = f"{points / price:.4}"
#         position = row[-1]
#         players_table_2021.add_row([player_name, f"£{price}", goals, assists, goal_contributions,
#                            points, float(roi), position, None])
#         if goal_contributions >= 17 or (
#             position == 'DEF' and goal_contributions > 5
#         ):
#             star_players.append(player_name)
#     players_table_2021.reversesort = True
#     print(players_table_2021.get_string(sortby='Total Points'))
#     print(star_players)

import os
import pandas as pd
import csv

directory_str = 'raw_player_data'
directory = os.fsencode(directory_str)
player_list = []


def generate_historical():
    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if filename.endswith(".csv"):
            season_year = int(filename[-8:].replace('.csv', ''))
            filename = os.path.join(directory_str, filename)
            df = pd.read_csv(filename)
            avg_points = df['total_points'].mean()
            print(avg_points)
            with open(filename) as f:
                # print(f.name)
                reader = csv.reader(f)
                headers = next(reader)
                # print(headers)
                for row in reader:
                    player_fullname = row[0] + " " + row[1]
                    minutes_played = row[5]
                    clean_sheets = row[-6] if season_year > 2021 else row[-5]
                    season_year = season_year
                    goals = int(row[2])
                    assists = int(row[3])
                    goal_contributions = goals + assists
                    price = f"{float((row[-1])) / 10:.4}" if season_year < 2021 else f"{int((row[-2])) / 10:.4}"
                    points = int(row[4])
                    roi = f"{points / float(price):.4}" if float(price) != 0 else 0
                    position = row[-1] if season_year >= 2021 else None
                    dict = {
                        'player_full_name': player_fullname,
                        'goals': goals,
                        'assists': assists,
                        'season_year': season_year,
                        'goal_contributions': goal_contributions,
                        'points': points,
                        'price': price,
                        'roi': roi,
                        'position': position,
                        'minutes_played': minutes_played,
                        'clean_sheets': clean_sheets,
                        'goal_contributions_pgw': round(float(goal_contributions) / 38, 2),
                        'points_pgw': round(float(points) / 38, 2)

                    }
                    if goal_contributions >= 15 or points >= avg_points * 4:
                        player_list.append(dict)
        else:
            sys.exit(-1)
    return player_list


try:
    player_dict = generate_historical()
    keys = player_dict[0].keys()

    with open('Ballers.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(player_dict)
except Exception as e:
    print(e)
