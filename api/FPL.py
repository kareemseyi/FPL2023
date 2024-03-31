import http
import aiohttp
import asyncio
import os

import utils
import itertools
from endpoints import endpoints
from http import cookies
from utils import fetch
from dataModel.user import User
from dataModel.player import Player
from dataModel.fixture import Fixture

MAX_DEF = 5

# Login Url
LOGIN_URL = endpoints["API"]["LOGIN"]

# Base Url
STATIC_BASE_URL = endpoints['STATIC']['BASE_URL']

API_MY_TEAM_GW_URL = endpoints['API']['MY_TEAM_GW']
API_ME = endpoints['API']['ME']

API_GW_FIXTURES = endpoints['API']['GW_FIXTURES']
API_ALL_FIXTURES = endpoints['API']['ALL_FIXTURES']


async def get_current_user(session):
    user = await fetch(session, API_ME)
    return user


class FPL:
    """The FPL class."""

    def __init__(self, session):
        self.session = session

    async def login(self, email=None, password=None):
        """Returns a requests session with FPL login authentication.

        :param string email: Email address for the user's Fantasy Premier League
            account.
        :param string password: Password for the user's Fantasy Premier League
            account.
        """
        if not email and not password:
            email = os.getenv("FPL_EMAIL", 'okareem@stellaralgo.com')
            password = os.getenv("FPL_PASSWORD", '@Testing123')
        if not email or not password:
            raise ValueError("Email and password must be set")
        print(f"Logging in: {LOGIN_URL}")
        print(f"Logging in: {email}, {password}")

        headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)",
                   'accept-language': 'en'
                   }
        cookies = http.cookies.SimpleCookie()
        payload = {
            "login": email,
            "password": password,
            "app": "plfpl-web",
            "redirect_uri": "https://fantasy.premierleague.com/a/login",
            "Set-Cookie": cookies
        }
        async with self.session.post(LOGIN_URL, data=payload, headers=headers, cookies=cookies) as response:
            print(response)
            assert response.status == 200
            if "state=success" in str(response.url):
                print("Successfully logged In")
            else:
                if "state=fail" in str(response.url):
                    raise ValueError("Incorrect email or password!")
        return self.session

    def logged_in(self):
        """Checks that the user is logged in within the session.


        :return: True if user is logged in else False
        :rtype: bool
        """
        return "csrftoken" in self.session.cookie_jar.filter_cookies(
            "https://users.premierleague.com/")

    async def get_user(self, user_id=None, return_json=False):
        """Returns the user with the given ``user_id``.

        Information is taken from e.g.:
            https://fantasy.premierleague.com/api/entry/91928/

        :param session:
        :param user_id: A user's ID.
        :type user_id: string or int
        :param return_json: (optional) Boolean. If ``True`` returns a ``dict``,
            if ``False`` returns a :class:`User` object. Defaults to ``False``.
        :type return_json: bool
        :rtype: :class:`User` or `dict`
        """
        if user_id:
            assert int(user_id) > 0, "User ID must be a positive number."
        else:
            # If no user ID provided get it from current session
            try:
                user = await get_current_user(self.session)
                user_id = user["player"]["entry"]
            except TypeError:
                raise Exception("You must log in before using `get_user` if "
                                "you do not provide a user ID.")

        url = API_ME.format(user_id)
        user = await fetch(self.session, url)

        if return_json:
            return user
        return User(user, self.session)

    async def get_users_team(self, user, gw):
        """Returns a logged-in user's current team. Requires the user to have
        logged in using ``fpl.login()``.

        :rtype: list
        """
        if not FPL.logged_in(self):
            raise Exception("User must be logged in.")

        try:
            response = await fetch(
                self.session, API_MY_TEAM_GW_URL.format(f=user.entry, gw=gw))
        except Exception as e:
            raise Exception("Client has not set a team for gameweek " + str(gw))
        return response['picks']

    async def get_all_current_players(self, player_ids=None, return_json=False):
        """Returns either a list of *all* players, or a list of players whose
        IDs are in the given ``player_ids`` list.

        Information is taken from e.g.:
            https://fantasy.premierleague.com/api/bootstrap-static/
            https://fantasy.premierleague.com/api/element-summary/1/ (optional)

        :param list player_ids: (optional) A list of player IDs
        :param boolean include_summary: (optional) Includes a player's summary
            if ``True``.
        :param return_json: (optional) Boolean. If ``True`` returns a list of
            ``dict``s, if ``False`` returns a list of  :class:`Player`
            objects. Defaults to ``False``.
        :type return_json: bool
        :rtype: list
        """
        try:
            data = await fetch(self.session, STATIC_BASE_URL)
            players = data['elements']
        except Exception as e:
            print(e)
            raise Exception
        if player_ids:
            players = [player for player in players if player["id"] in player_ids]

            if not return_json:
                return players
            else:
                return [Player(player) for player in players]

        if not player_ids:
            player_ids = [player["id"] for player in players]

        tasks = [asyncio.ensure_future(
            self.get_current_player(
                player_id, players, return_json))
            for player_id in player_ids]
        players = await asyncio.gather(*tasks)

        return players

    # async def get_current_players(self):
    #     dynamic = await fetch(self.session, STATIC_BASE_URL)
    #     player_id_list = [player["id"] for player in dynamic["elements"]]
    #     name_list = [str(player["first_name"] + ' ' + player['second_name']) for player in dynamic["elements"]]
    #     return {player_id_list[i]: name_list[i] for i in range(len(name_list))}

    async def get_current_player(self, player_id, players=None, return_json=False):
        """Returns the player with the given ``player_id``.

        :param player_id: A player's ID.
        :type player_id: string or int
        :rtype: :class:`Player` or ``dict``
        :raises ValueError: Player with ``player_id`` not found
        """
        if not players:
            data = await fetch(self.session, STATIC_BASE_URL)
            players = data['elements']

        try:
            player = next(player for player in players if player["id"] == player_id)
            # print(player)
        except StopIteration:
            raise ValueError(f"Player with ID {player_id} not found")

        if return_json:
            return player
        return Player(player)

    async def get_fixtures_for_next_GW(self, gameweek):
        assert gameweek > 0
        if not FPL.logged_in(self):
            raise Exception("User must be logged in.")
        try:
            response = await fetch(self.session, API_GW_FIXTURES.format(f=gameweek))
        except aiohttp.client_exceptions.ClientResponseError:
            raise Exception("User ID does not match provided email address!")

        team_dict = utils.get_teams()
        fixtures = [x for x in response if x['event'] in gameweek]
        return [Fixture(fixture, team_dict=team_dict) for fixture in fixtures]

    async def get_all_fixtures(self, *gameweek):
        if not FPL.logged_in(self):
            raise Exception("User must be logged in.")

        task = asyncio.ensure_future(fetch(self.session, API_ALL_FIXTURES))

        gameweek_fixtures = await asyncio.gather(task)
        fixtures = list(itertools.chain(*gameweek_fixtures))

        team_dict = utils.get_teams()
        return [Fixture(fixture, team_dict) for fixture in fixtures if fixture['event'] in gameweek]

    def pickTeam(self, user, gw, initial=False):
        if not FPL.logged_in(self):
            raise Exception("User must be logged in.")
        if initial:
            gw = 1
        try:
            fixtures = self.get_all_fixtures(list(range(gw,gw+5)))
        except Exception as e:
            raise(e)



