import sys

import requests as requests

URL = 'https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/2023-24/cleaned_players.csv'
res = requests.get(URL)
print(res.status_code)
print(res.json()['payload']['blob']['csv'][0])
# ['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes', 'goals_conceded', 'creativity', 'influence', 'threat', 'bonus', 'bps', 'ict_index', 'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'now_cost', 'element_type']


dataURL = 'https://github.com/vaastav/Fantasy-Premier-League/tree/master/data'
res2 = requests.get(dataURL)
print(res2)


sys.exit()