"""
Constants for FPL analysis.
"""

# API Endpoints
endpoints = {
    "STATIC": {"BASE_URL": "https://fantasy.premierleague.com/api/bootstrap-static/"},
    "API": {
        "BASE_URL": "https://fantasy.premierleague.com/",
        "AUTH": "https://account.premierleague.com/as/authorize",
        "LOGIN": "https://users.premierleague.com/accounts/login/",
        "MY_TEAM": "https://fantasy.premierleague.com/api/entry/{f}/",
        "USER_TEAM": "https://fantasy.premierleague.com/api/my-team/{f}/",
        "GET_PLAYER": "https://fantasy.premierleague.com/api/element-summary/{f}/",
        "MY_TEAM_GW": "https://fantasy.premierleague.com/api/entry/{f}/event/{gw}/picks",
        "GW_FIXTURES": "https://fantasy.premierleague.com/api/fixtures/?events={{f}}",
        "ALL_FIXTURES": "https://fantasy.premierleague.com/api/fixtures/",
        "ME": "https://fantasy.premierleague.com/api/me",
        "TRANSFERS": "https://fantasy.premierleague.com/api/transfers/",
        "REDIRECT_URI": "https://fantasy.premierleague.com/",
        "DAVINCI_POLICY_START": "https://account.premierleague.com/davinci/policy/262ce4b01d19dd9d385d26bddb4297b6/start",
        "DAVINCI_CONNECTIONS": "https://account.premierleague.com/davinci/connections/{}/capabilities/customHTMLTemplate",
        "AS_RESUME": "https://account.premierleague.com/as/resume",
        "AS_TOKEN": "https://account.premierleague.com/as/token",
    },
    "DATA_GITHUB": {
        "BASE_URL": "https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/",
        "FOLDER_URL": "https://github.com/vaastav/Fantasy-Premier-League/tree/master/data",
    },
}

# Team constraints
MAX_DEF = 5
MAX_GK = 2
MAX_MID = 5
MAX_FWD = 3
MAX_BUDGET = 100
MAX_PLAYER_FROM_TEAM = 3

# Standardized Player Data Schema
PLAYER_DATA_SCHEMA = {
    "first_name": "",  # str: Player's first name
    "second_name": "",  # str: Player's last name
    "now_cost": 0.0,  # float: Current price in millions (e.g., 8.5 not 85)
    "starts": 0,  # int: Number of games started
    "goals_scored": 0,  # int: Goals scored this season
    "assists": 0,  # int: Assists this season
    "goal_contributions": 0,  # int: Goals + assists (calculated)
    "total_points": 0,  # int: Total FPL points
    "points_per_game": 0.0,  # float: Points per game average
    "roi": 0.0,  # float: Return on investment (points/price)
    "roi_per_gw": 0.0,  # float: ROI per gameweek started
    "element_type": "",  # str: Element_type 1:GK, 2:DEF, 3:MID, 4:FWD)
    "team_name": "",  # str: Team name
    "minutes": 0,  # int: Total minutes played
    "FDR_Average": 0.0,  # float: Fixture Difficulty Rating average
    "team": 0,  # int: team code
}

# Position mapping
POSITION_MAP = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
