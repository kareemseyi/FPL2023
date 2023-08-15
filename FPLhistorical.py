import csv

import sys
import asyncio
import requests
from prettytable import PrettyTable

players_table_2021 = PrettyTable()
players_table_2021.field_names = ["Player_Name", "Price (Pounds)", "Goals", "Assists", "Direct Goal Contribution",
                                  "Total Points", "ROI", "Position", "Team"]
star_players = []

with open('cleaned_players_2022_23.csv') as f:
    print(f.name)
    reader = csv.reader(f)
    headers = next(reader)
    print(headers)
    for row in reader:
        player_fullname = row[0] + " " + row[1]
        player_name = row[1]
        goals = int(row[2])
        assists = int(row[3])
        goal_contributions = goals + assists
        price = int(row[-2]) / 10
        points = int(row[4])
        roi = f"{points / price:.4}"
        position = row[-1]
        players_table_2021.add_row([player_name, f"£{price}", goals, assists, goal_contributions,
                           points, float(roi), position, None])
        if goal_contributions >= 17 or (
            position == 'DEF' and goal_contributions > 5
        ):
            star_players.append(player_name)
    players_table_2021.reversesort = True
    print(players_table_2021.get_string(sortby='Total Points'))
    print(star_players)


def main():
    print('Hello')

if __name__ == '__main__':
    main()
