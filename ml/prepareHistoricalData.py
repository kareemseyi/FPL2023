import csv
import os
import requests
from prettytable import PrettyTable

url = "https://fantasy.premierleague.com/api/bootstrap-static/"
json_general = requests.get(url).json()
print(json_general.keys())
season = "24_25"

print(json_general["element_types"])

name_list = [
    str(player["first_name"] + " " + player["second_name"])
    for player in json_general["elements"]
]
player_id_list = [player["id"] for player in json_general["elements"]]
teamname_list = [team["name"] for team in json_general["teams"]]
teamid_list = [team["id"] for team in json_general["teams"]]
roi_list = []
teamid_list_g = []
pos_list_g = []
data_dict = []
id_dict = {}
# Dictionary of team_ids and Team
team_dict = {
    json_general["teams"][i]["id"]: json_general["teams"][i]["name"]
    for i in range(len(teamname_list))
}
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
players_table.field_names = [
    "Player_Name",
    "Price (Pounds)",
    "Games Played",
    "Goals",
    "Assists",
    "Direct Goal Contributions",
    "Total Points",
    "Points Per Game",
    "ROI",
    "Position",
    "Team",
    "Minutes",
]
players_table.align = "c"
for baller in sorted_players:
    goals = baller["goals_scored"]
    assists = baller["assists"]
    goal_contributions = baller["goals_scored"] + baller["assists"]
    games_played = baller["starts"]
    minutes = baller["minutes"]

    teamname = get_team(baller["team"])
    roi = float(f"{(baller['total_points'] / (baller['now_cost'] / 10)):0000000.4}")
    roi_per_gw = roi / games_played if games_played > 0 else 0
    roi_list.append(roi)  # add all ROIs for all players
    teamid_list_g.append(baller["team"])

    if baller["element_type"] == 1:
        pos = "GK"
    elif baller["element_type"] == 2:
        pos = "DEF"
    elif baller["element_type"] == 3:
        pos = "MID"
    else:
        pos = "FWD"
    pos_list_g.append(pos)

    diction = {
        "name": baller["web_name"],
        "price": f"£{baller['now_cost'] / 10}",
        "team": teamname,
        "goals": int(goals),
        "assists": int(assists),
        "goal_contributions": int(goal_contributions),
        "games_played": int(games_played),
        "minutes": int(minutes),
        "total_points": int(baller["total_points"]),
        "points_per_game": float(baller["points_per_game"]),
        "roi": float(roi),
        "roi_per_gw": float(roi_per_gw),
        "position": pos,
    }

    data_dict.append(diction)
    csv_filename = f"FPL_data_{season}.csv"

    # Specify the target folder and filename
    target_folder = "../historical/_summary"  # Replace with your desired folder name

    # Create the target folder if it doesn't exist
    os.makedirs(target_folder, exist_ok=True)

    # Construct the full file path
    path = os.path.join(target_folder, csv_filename)

    keys = data_dict[0].keys()
    with open(path, mode="w", newline="") as file:
        dict_writer = csv.DictWriter(file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_dict)
