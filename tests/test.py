import requests
resp = requests.get('https://fantasy.premierleague.com/')
print (resp.content)