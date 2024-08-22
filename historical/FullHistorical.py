import sys
import re
import requests as requests
from dataModel.player import Player
from dataModel.fixture import Fixture
import csv

# URL = 'https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/2023-24/cleaned_players.csv'
# res = requests.get(URL)
# print(res.status_code)
# print(res.json()['payload']['blob']['csv'][0])
# print(res.json()['payload']['blob']['csv'][1])
# print(res.json()['payload']['blob']['csv'][2])
# ['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes', 'goals_conceded', 'creativity', 'influence', 'threat', 'bonus', 'bps', 'ict_index', 'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'now_cost', 'element_type']
headers = {'Accept': 'application/json'}
FolderURL = 'https://github.com/vaastav/Fantasy-Premier-League/tree/master/data'
# print(res2.json())
#
# print(lis)
final = []
hist_fixtures = []

# folders.remove(max(folders))
# print(folders)  # Ensure to remove max folder if doing historical
baseURL = 'https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/'
baseURL2 = 'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/'


def getHistoricalPlayers(n=2, minutes=900):
    """
    ** Function should not be used for CURRENT season Data

    :param n: the default number of YEARS of historical players, default is 2 years
                NOTE* it will include a current season if the EPL is already in season
    :param minutes: minimum number of minutes a player is required to meet this threshold.
    :return:
    """
    res2 = requests.get(FolderURL, headers=headers)
    lis = res2.json()['payload']['tree']['items']
    folders = [x['name'] for x in lis if re.match('[0-9]*-[0-9]*', x['name'])]
    print(folders[-n:])
    for i in folders[-n:]:
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

                if int(player['minutes']) >= minutes:  # Only add players who played over 1000 mins
                    final.append(player)

        except Exception as e:
            print(e)
    print(len(final))
    return list(Player(player) for player in final)


def getHistoricalFixtures():
    with open('_fixtures/fixtures21-22.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            fix = Fixture(row)
            hist_fixtures.append(fix)


getHistoricalFixtures()

# def genHistFDR():
#
#