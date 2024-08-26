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

def getHistoricalTeamDict(season):
    teamdict = {}
    with open('_team_dict/teams_{}.csv'.format(season), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            teamdict[row['id']] = row['name']
    return teamdict

def getHistoricalFixtures(season, team_dict):
    hist_fixtures = []
    with open('_fixtures/fixtures_{}.csv'.format(season), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hist_fixtures.append(row)
        return [Fixture(fixture, team_dict=team_dict) for fixture in hist_fixtures]

def getFormDict(season):
    team_dict = getHistoricalTeamDict(season)
    fixtures = getHistoricalFixtures(season, team_dict)

    form_dict = {}

    for i in team_dict:
        form_dict[team_dict[i]] = ''
        for j in fixtures:
            if (team_dict[i] == j.get_away_team() or team_dict[i] == j.get_home_team()):
                if j.get_winner() == team_dict[i]:
                    form_dict[team_dict[i]] += 'W'
                if j.is_draw():
                    form_dict[team_dict[i]] += 'D'
                if not j.is_draw() and j.get_winner() != team_dict[i]:
                    form_dict[team_dict[i]] += 'L'
    return form_dict
def convertTeamForm(form: str):
    res = 0
    for i in form:
        if i == 'W':
            res+=3
        if i == 'D':
            res+=1
        if i == 'L':
            res+=0
    return float(res/38)

def get_FDR(form_dict, season):
    team_dict = getHistoricalTeamDict(season)
    print(team_dict)
    _fixtures = getHistoricalFixtures(season, team_dict)

    fdr_dict = {}

    for i in form_dict:
        fdr_dict[i] = 0
        for j in _fixtures:
            if i == j.get_away_team():
                fdr_dict[i] += (convertTeamForm(form_dict[i]) - convertTeamForm(form_dict[j.get_home_team()]))
            if i == j.get_home_team():
                fdr_dict[i] += (convertTeamForm(form_dict[i]) - convertTeamForm(form_dict[j.get_away_team()]))

    return fdr_dict






season = '23_24'
hist_team_dict = getHistoricalTeamDict(season)
hist_fixtures = getHistoricalFixtures(season, hist_team_dict)
print(len(hist_fixtures))
#
for i in hist_fixtures[0:10]:
    print(vars(i))

form_dict = getFormDict(season)
print(form_dict)

for i in form_dict:
    print(len(form_dict[i]))

FDR = get_FDR(form_dict, season)
print(FDR)

