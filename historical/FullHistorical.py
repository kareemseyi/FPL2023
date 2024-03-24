import sys
import re
import requests as requests
from dataModel.player import Player


# URL = 'https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/2023-24/cleaned_players.csv'
# res = requests.get(URL)
# print(res.status_code)
# print(res.json()['payload']['blob']['csv'][0])
# print(res.json()['payload']['blob']['csv'][1])
# print(res.json()['payload']['blob']['csv'][2])
# ['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes', 'goals_conceded', 'creativity', 'influence', 'threat', 'bonus', 'bps', 'ict_index', 'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'now_cost', 'element_type']

def getHistoricalPlayers():
    """

    :return: list(<Player>) A list of Historical player objects
    """
    headers = {'Accept': 'application/json'}
    FolderURL = 'https://github.com/vaastav/Fantasy-Premier-League/tree/master/data'
    res2 = requests.get(FolderURL, headers=headers)
    print(res2.json())
    lis = res2.json()['payload']['tree']['items']
    print(lis)
    final = []

    folders = [x['name'] for x in lis if re.match('[0-9]*-[0-9]*', x['name'])]
    folders.remove(max(folders))
    print(folders)  # Ensure to remove max folder if doing historical
    baseURL = 'https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/'

    for i in folders:
        dataURL = baseURL + i + '/cleaned_players.csv'
        try:
            res = requests.get(dataURL, headers=headers)
            assert res.status_code == 200
            data = res.json()['payload']['blob']['csv']
            _keys = data[0]
            print(len(data))
            for j in range(1, len(data)):
                player = dict(zip(_keys, data[j]))
                player['season'] = str(i)

                if int(player['minutes']) > 1000:  # Only add players who played over 1000 mins
                    final.append(player)

                # final.append(Player(player))
        except Exception as e:
            print(e)
    print(len(final))
    return list(Player(player) for player in final)