import os
from dotenv import load_dotenv
import requests
from endpoints import endpoints


load_dotenv()
# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = os.getenv("ODDS_KEY", None)
API_ALL_FIXTURES = endpoints["API"]["ALL_FIXTURES"]

SPORT = "soccer_epl"
REGIONS = "uk"
MARKETS = "h2h"
ODDS_FORMAT = "decimal"

DATE_FORMAT = "iso"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# First get a list of in-season sports
#   The sport 'key' from the response can be used to get odds in the next request
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# sports_response = requests.get(
#     'https://api.the-odds-api.com/v4/sports',
#     params={
#         'api_key': API_KEY
#     }
# )
#
#
# if sports_response.status_code != 200:
#     print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')
#
# else:
#     print('List of in season sports:', sports_response.json())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# This will deduct from the usage quota
# The usage quota cost = [number of markets specified] x [number of regions specified]
# For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

res = requests.get(API_ALL_FIXTURES)
res = res.json()
print(type(res[0]["stats"]))
date = next(
    (x["kickoff_time"] for x in res if not x["stats"]), None
)  # Get the earliest time for next GW, first game where there are
# NO stats
print(date)

odds_response = requests.get(
    f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds",
    params={
        "api_key": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": ODDS_FORMAT,
        "dateFormat": DATE_FORMAT,
        "commenceFromTime": date,
    },
)


if odds_response.status_code != 200:
    print(
        f"Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}"
    )

else:
    odds_json = odds_response.json()
    print("Number of events:", len(odds_json))
    print(odds_json[0]["bookmakers"])  # This is a list
    print(odds_json[0]["home_team"]), print(odds_json[0]["away_team"])
    print(odds_json[1]["home_team"]), print(odds_json[1]["away_team"])

    for i in odds_json:
        print(i)
        # will_hill = [x['bookmakers'] for x in i]
        # print(will_hill)

    # Check the usage quota
    print("Remaining requests", odds_response.headers["x-requests-remaining"])
    print("Used requests", odds_response.headers["x-requests-used"])
