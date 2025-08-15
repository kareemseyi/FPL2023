import sys
import re
import requests as requests
from dataModel.player import Player
from dataModel.fixture import Fixture
import csv
import utils
from endpoints import endpoints

# URL = 'https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/2023-24/cleaned_players.csv'
# res = requests.get(URL)
# print(res.status_code)
# print(res.json()['payload']['blob']['csv'][0])
# print(res.json()['payload']['blob']['csv'][1])
# print(res.json()['payload']['blob']['csv'][2])
# ['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes', 'goals_conceded', 'creativity',
# 'influence', 'threat', 'bonus', 'bps', 'ict_index', 'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent'
# , 'now_cost', 'element_type']
headers = utils.headers
FolderURL = endpoints['DATA_GITHUB']['FOLDER_URL']
baseURL = endpoints['DATA_GITHUB']['BASE_URL']
staticURL = endpoints['STATIC']['BASE_URL']
# print(res2.json())
#
# print(lis)
final = []
data_dict = []


# folders.remove(max(folders))
# print(folders)  # Ensure to remove max folder if doing historical


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
    with open('../historical/_teams/teams_{}.csv'.format(season), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            teamdict[row['id']] = row['name']
    return teamdict


def getHistoricalFixtures(season, team_dict):
    hist_fixtures = []
    with open('../historical/_fixtures/fixtures_{}.csv'.format(season), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hist_fixtures.append(row)
        return [Fixture(fixture, team_dict=team_dict) for fixture in hist_fixtures]


def getFormDict(season=None, fixtures=None):
    if season:
        team_dict = getHistoricalTeamDict(season)
        fixtures = getHistoricalFixtures(season, team_dict)

    else:
        team_dict = utils.get_teams()
        fixtures = fixtures

    form_dict = {}
    score_strength_dict = {}

    for i in team_dict:
        form_dict[team_dict[i]] = ''
        score_strength_dict[team_dict[i]] = 0
        for j in fixtures:
            if (team_dict[i] == j.get_away_team() or team_dict[i] == j.get_home_team()):
                if j.get_winner() == team_dict[i]:
                    form_dict[team_dict[i]] += 'W'
                    if abs(int(j.team_h_score) - int(j.team_a_score)) >= 3:
                        score_strength_dict[team_dict[i]] += 1
                if j.is_draw():
                    form_dict[team_dict[i]] += 'D'
                if not j.is_draw() and j.get_winner() != team_dict[i]:
                    form_dict[team_dict[i]] += 'L'
                    if abs(int(j.team_h_score) - int(j.team_a_score)) >= 3:
                        score_strength_dict[team_dict[i]] -= 1
    return form_dict, score_strength_dict


def convertTeamForm(form: str):
    res = 0
    for i in form:
        if i == 'W':
            res += 3
        if i == 'D':
            res += 1
        if i == 'L':
            res += 0
    return float(res / (38 * 3))  # Normalize for max scenario where team won all its games? lol


def get_FDR(form_dict, fixtures=None, season=None):
    if season:
        team_dict = getHistoricalTeamDict(season)
        fixtures = getHistoricalFixtures(season, team_dict)
    else:
        fixtures = fixtures
    fdr_dict = {}
    for i in form_dict:
        fdr_dict[i] = 0
        for j in fixtures:
            if i == j.get_away_team():
                fdr_dict[i] += (convertTeamForm(form_dict[i]) - convertTeamForm(form_dict[j.get_home_team()]))
            if i == j.get_home_team():
                fdr_dict[i] += (convertTeamForm(form_dict[i]) - convertTeamForm(form_dict[j.get_away_team()]))

    return fdr_dict