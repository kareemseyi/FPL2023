import asyncio
import aiohttp
import pytest
from endpoints import endpoints
from dataModel.user import User
from dataModel.fixture import Fixture

API_BASE_URL = endpoints['STATIC']['BASE_URL']
API_FIXTURE_URL = endpoints['STATIC']['FIXTURES']

API_MY_TEAM_URL = endpoints['API']['MY_TEAM']
API_MY_TEAM_GW_URL = endpoints['API']['MY_TEAM_GW']
API_ME = endpoints['API']['ME']

API_GW_FIXTURES = endpoints['API']['GW_FIXTURES']


async def fetch(session, url):
    while True:
        try:
            async with session.get(url) as response:
                assert response.status == 200
                return await response.json(content_type=None)
        except Exception as e:
            pass


async def post(session, url, payload, headers):
    async with session.post(url, data=payload, headers=headers) as response:
        return await response.json()


def logged_in(session):
    """Checks that the user is logged in within the session.

    :param session: http session
    :type session: aiohttp.ClientSession
    :return: True if user is logged in else False
    :rtype: bool
    """
    return "csrftoken" in session.cookie_jar.filter_cookies(
        "https://users.premierleague.com/")


async def get_remaining_fixtures(session):
    """Returns the list of fixtures.
    :param aiohttp.ClientSession session: A logged-in user's session.
    :rtype: int
    """
    dynamic = await fetch(
        session, API_FIXTURE_URL)

    matches_not_played = [x for x in dynamic if x['finished'] is False]
    matches_played = [x for x in dynamic if x['finished'] is True]

    return matches_not_played


async def get_user(session, user_id=None, return_json=False):
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
            user = await get_current_user(session)
            user_id = user["player"]["entry"]
        except TypeError:
            raise Exception("You must log in before using `get_user` if "
                            "you do not provide a user ID.")

    url = API_ME.format(user_id)
    user = await fetch(session, url)

    if return_json:
        return user
    return User(user, session)


def position_converter(position):
    """Converts a player's `element_type` to their actual position."""
    position_map = {
        1: "Goalkeeper",
        2: "Defender",
        3: "Midfielder",
        4: "Forward"
    }
    return position_map[position]


async def get_teams(session):
    dynamic = await fetch(session, API_BASE_URL)
    teamname_list = [team["name"] for team in dynamic["teams"]]
    return {dynamic["teams"][i]["id"]: dynamic["teams"][i]["name"] for i in range(len(teamname_list))}


def get_team(team_dict, team_id):
    return team_dict.get(team_id)


async def get_current_user(session):
    user = await fetch(session, API_ME)
    return user


async def get_players(session):
    dynamic = await fetch(session, API_BASE_URL)
    player_id_list = [player["id"] for player in dynamic["elements"]]
    name_list = [str(player["first_name"] + ' ' + player['second_name']) for player in dynamic["elements"]]
    return {player_id_list[i]: name_list[i] for i in range(len(name_list))}


def get_player(player_dict, player_id):
    return player_dict.get(player_id)

async def  get_player(self, player_id, players=None, include_summary=False,
                     return_json=False):
    """Returns the player with the given ``player_id``.

    Information is taken from e.g.:
        https://fantasy.premierleague.com/drf/elements
        https://fantasy.premierleague.com/drf/element-summary/1 (optional)

    :param player_id: A player's ID.
    :type player_id: string or int
    :param list players: (optional) A list of players.
    :param bool include_summary: (optional) Includes a player's summary
        if ``True``.
    :param return_json: (optional) Boolean. If ``True`` returns a ``dict``,
        if ``False`` returns a :class:`Player` object. Defaults to
        ``False``.
    :rtype: :class:`Player` or ``dict``
    :raises ValueError: Player with ``player_id`` not found
    """
    if not players:
        players = await fetch(self.session, API_URLS["players"])

    try:
        player = next(player for player in players
                      if player["id"] == player_id)
    except StopIteration:
        raise ValueError(f"Player with ID {player_id} not found")

    if include_summary:
        player_summary = await self.get_player_summary(
            player["id"], return_json=True)
        player.update(player_summary)

    if return_json:
        return player

    return Player(player)


async def get_users_team(session, User, gw):
    """Returns a logged-in user's current team. Requires the user to have
    logged in using ``fpl.login()``.

    Information is taken from e.g.:
        https://fantasy.premierleague.com/api/my-team/91928/

    :rtype: list
    """
    if not logged_in(session):
        raise Exception("User must be logged in.")

    try:
        response = await fetch(
            session, API_MY_TEAM_GW_URL.format(f=User.entry, gw=gw))
    except aiohttp.client_exceptions.ClientResponseError:
        raise Exception("User ID does not match provided email address!")

    if response.get("detail") == "Not found.":
        raise Exception("Data not found. Please ensure user ID matches provided email address.")

    return response['picks']

async def get_upcoming_gameweek(session):
    if not logged_in(session):
        raise Exception("User must be logged in.")
    try:
        response = await fetch(
            session, API_FIXTURE_URL)
        gw = max([x['event'] for x in response if x['finished'] is True])
        # This is the previous gameweek
    except Exception:
        raise Exception("no Gameweeks have started")

    if len(response) == 0:
        raise Exception("No Active Events yet.... TODO")

    return int(gw) + 1  # Adds one to previous gameweek

async def get_fixtures_for_gameweek(session, gameweek:int):
    """Returns the fixtures for the current gameweek.

    :param aiohttp.ClientSession session: A logged-in user's session.
    :rtype: int
    """
    if not logged_in(session):
        raise Exception("User must be logged in.")
    try:
        response = await fetch(
            session, API_GW_FIXTURES.format(f=gameweek))
    except aiohttp.client_exceptions.ClientResponseError:
        raise Exception("User ID does not match provided email address!")

    team_dict = await get_teams(session)
    fixtures = [x for x in response if x['event'] == gameweek]
    return [Fixture(fixture, team_dict=team_dict) for fixture in fixtures]




# async def transfer(self, players_out, players_in, max_hit=60,wildcard=False, free_hit=False):
#     # Get team players + IDs, and FPL players + IDs.
#     user_team = await self.get_team()
#     team_ids = [player["element"] for player in user_team]
#     players = await fetch( self._session, API_URLS["players"])
#     player_ids = [player["id"] for player in players]
#     if set(player_ids). isdisjoint(players_in):
#         raise Exception( "Player ID in 'players_in' does not exist.")
# # Send POST requests with confirmed set to False; this basically
# # checks if there are any errors from FL's side for this transfer,
# # e.g. too many players from the same team, or not enough money.
# payload = self..
# _get_transfer_payload(
# players_out, players_in, user_team, players, wildcard, free_hit)
# csrf_token = await get_csrf_token( self.
# session)
# headers = get_headers
# csrf_token,
# "https://fantasy.premierleague.com/a/squad/transfers")
# post response = await post
# self._session, API_URLS["transfers"], json. dumps (payload), headers)
# # For example, trying to transfer in a player who costs too much,
# # or trying to transfer in a 4th plaver from the same team will
# # result in an error.
# if "non form errors" in post response:
# raise Exception (post_response [ "non_form_errors"])
# # Check if the point hit is less than the maximum hit the user is
# # willing to take
# if post_response[ "spent_points"] > max_hit:
# raise Exception(
# f"Point hit for transfer (s) [-{post_response[ 'spent_points']}]" f" exceeds max hit [{max hit}].")
# # Everything is okay, so push the transfer through!
# payload[" confirmed" ] = True
# post response = await post!
# self._session, API_URLS["transfers"], json. dumps (payload), headers)
