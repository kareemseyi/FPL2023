import requests
resp = requests.get('https://fantasy.premierleague.com/api/fixtures/')
resp2 =  resp.json()

print(resp2[0])