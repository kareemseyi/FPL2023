import requests
resp = requests.get('https://fantasy.premierleague.com/api/fixtures')
resp2 = resp.json()



game_weeks = [x['event'] for x in resp2 if x['finished'] is True]
print(game_weeks)