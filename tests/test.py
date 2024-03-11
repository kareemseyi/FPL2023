import requests
resp = requests.get('https://fantasy.premierleague.com/api/fixtures/?events={26}')
resp2 = resp.json()

# print(len(resp2))

game_weeks = [x for x in resp2 if x['finished'] is True and x['event'] == 3]
print(game_weeks[0])