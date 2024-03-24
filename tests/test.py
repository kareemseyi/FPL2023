import requests
import json

headers = {'Accept': 'application/json'}
resp = requests.get('https://github.com/vaastav/Fantasy-Premier-League/raw/master/data', headers=headers)
if resp.status_code == 200:
    print(resp.json())
