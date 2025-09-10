import aiohttp
import asyncio
import utils
import itertools
from endpoints import endpoints
import json
from utils import fetch, post_transfer, post
from dataModel.user import User
from dataModel.player import Player
from dataModel.fixture import Fixture
from dataModel.team import Team
from auth.fpl_auth import FPLAuth
from api.FPL_helpers import FPLHelpers

API_MY_TEAM_GW_URL = endpoints["API"]["MY_TEAM_GW"]
API_MY_TEAM = endpoints["API"]["MY_TEAM"]
API_USER_TEAM = endpoints["API"]["USER_TEAM"]
API_TRANSFERS = endpoints["API"]["TRANSFERS"]

API_GW_FIXTURES = endpoints["API"]["GW_FIXTURES"]
API_ALL_FIXTURES = endpoints["API"]["ALL_FIXTURES"]


is_c = "is_captain"
is_vc = "is_vice_captain"


class FPL:
    """The FPL class."""

    def __init__(self, session, auth=None):
        self.session = session
        self.auth = auth or FPLAuth(session)
        self.helpers = FPLHelpers(session)

    async def login(self, email=None, password=None):
        """Login using the auth module.

        :param string email: Email address for the user's Fantasy Premier League
            account.
        :param string password: Password for the user's Fantasy Premier League
            account.
        """
        return await self.auth.login(email, password)

    def logged_in(self):
        """Checks that the user is logged in within the session.

        :return: True if user is logged in else False
        :rtype: bool
        """
        return self.auth.logged_in()

    async def get_current_user(self):
        return await self.auth.get_current_user()

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
                user = await self.get_current_user()
                user_id = user["player"]["entry"]
            except TypeError:
                raise Exception(
                    "You must log in before using `get_user` if "
                    "you do not provide a user ID."
                )

            if return_json:
                return user
            return User(user, self.session)

    async def get_users_team_for_gw(self, user, gw):
        """Returns a logged-in user's current team. Requires the user to have
        logged in using ``fpl.login()``.

        :rtype: list
        """
        if not self.logged_in():
            raise Exception("User must be logged in.")

        try:
            response = await fetch(
                self.session, API_MY_TEAM_GW_URL.format(f=user.entry, gw=gw)
            )
        except Exception as e:
            raise Exception("Client has not set a team for gameweek " + str(gw))
        return response["picks"]

    async def get_users_players(self, user):
        """Returns a logged-in user's current team. Requires the user to have
        logged in using ``fpl.login()``.

        :rtype: list
        """
        if not self.logged_in():
            raise Exception("User must be logged in.")

        try:
            response = await fetch(
                self.session,
                API_USER_TEAM.format(f=user.entry),
                headers=utils.headers_access(self.auth.access_token),
            )
        except Exception as e:
            raise Exception("Client has not set a team for gameweek ")
        return response["picks"]

    async def get_users_team(self, user):
        """Returns a logged-in user's current team. Requires the user to have
        logged in using ``fpl.login()``.

        :rtype: list
        """
        if not self.logged_in():
            raise Exception("User must be logged in.")

        try:
            response = await fetch(self.session, API_MY_TEAM.format(f=user.entry))
        except Exception as e:
            raise Exception("Client has not set a team for gameweek ")
        return response

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
        return await self.helpers.get_all_current_players(player_ids, return_json)

    async def get_current_player(
        self, player_id=None, player=None, return_json=False, convert_hist=False
    ):
        """Returns the player with the given ``player_id``.

        :param player:
        :param return_json:
        :param convert_hist:
        :param player_id: A player's ID.
        :type player_id: string or int
        :rtype: :class:`Player` or ``dict``
        :raises ValueError: Player with ``player_id`` not found
        """
        return await self.helpers.get_current_player(
            player_id, player, return_json, convert_hist
        )

    async def get_fixtures_for_next_GW(self, gameweek):
        assert gameweek > 0
        try:
            response = await fetch(
                self.session,
                API_GW_FIXTURES.format(f=gameweek),
                headers=utils.headers_access(self.auth.access_token),
            )
        except aiohttp.client_exceptions.ClientResponseError:
            raise Exception("User ID does not match provided email address!")

        team_dict = utils.get_teams()
        fixtures = [x for x in response if x["event"] == gameweek]
        return [Fixture(fixture, team_dict=team_dict) for fixture in fixtures]

    async def get_all_fixtures(self, *gameweek):
        """Returns all fixtures for the specified gameweeks.

        :param gameweek: Gameweek numbers to fetch fixtures for
        :rtype: list
        """
        return await self.helpers.get_all_fixtures(*gameweek)

    async def get_upcoming_gameweek(self):
        """Returns the upcoming gameweek number.

        :rtype: int
        """
        return await self.helpers.get_upcoming_gameweek()

    async def get_fixtures_for_gameweek(self, gameweek: int):
        """Returns the fixtures for the current gameweek.

        :param gameweek: The gameweek number
        :type gameweek: int
        :rtype: list
        """
        return await self.helpers.get_fixtures_for_gameweek(gameweek)

    async def get_team(self, *team_ids, team_names=None):
        return await self.helpers.get_team(*team_ids, team_names=team_names)

    async def pickTeam(self, gw, initial=False):
        if not self.logged_in():
            raise Exception("User must be logged in.")
        try:
            fixtures = await self.get_all_fixtures(*range(gw, gw + 5))
        except Exception as e:
            raise (e)
        home_teams, away_teams = {x.get_home_team() for x in fixtures}, {
            x.get_away_team() for x in fixtures
        }
        teams = await self.get_team(team_names=away_teams.union(home_teams))

        # this is where historical might come in? Current Player pool vs historical player pool when picking teams
        # Also which players are we going to filter out from the player pool,
        # players that have played over certain minutes?
        # This could also be a rolling target across the season

        player_pool = [
            x
            for sub in teams
            for x in await sub.get_players_for_team()
            if x.minutes > 180
        ]
        # 180 minutes currently
        player_pool.sort(key=lambda x: x.points_per_Min(), reverse=True)

        for i in player_pool:
            print(str(i), i.points_per_Min())

    def _set_captain(self, lineup, captain, captain_type, player_ids):
        """Sets the given captain's captain_type to True.

        :param lineup: List of players.
        :type lineup: list
        :param captain: ID of the captain.
        :type captain: int or str
        :param captain_type: The captain type: 'is_captain' or 'is_vice_captain'.
        :type captain_type: string
        :param player_ids: List of the team's players' IDs.
        :type player_ids: list
        """
        return FPLHelpers.set_captain(lineup, captain, captain_type, player_ids)

    # Moved to FPL_helpers.py
    # def get_transfer_candidates(team, player_pool):

    # async def get_transfers_status(self):
    #     """Returns a logged in user's transfer status, which is a dictionary
    #     containing their bank value, how many free transfers they have left
    #     and so on. Requires the user to have logged in using ``fpl.login()``.
    #
    #     Information is taken from e.g.:
    #         https://fantasy.premierleague.com/api/my-team/81629336/
    #
    #     :rtype: dict
    #     """
    #     if not FPL.logged_in(self):
    #         raise Exception("User must be logged in.")
    #
    #     try:
    #         user = await FPL.get_user(self)
    #         print(user.id)
    #         response = await fetch(self.session, API_MY_TEAM.format(f=user.id))
    #     except aiohttp.client_exceptions.ClientResponseError:
    #         raise Exception("User ID does not match provided email address!")
    #
    #     return response["transfers"]

    async def _get_transfer_payload(
        self, players_out, players_in, user_team, players, wildcard, free_hit
    ):
        """Returns the payload needed to make the desired transfers."""
        if not self.logged_in():
            raise Exception("User must be logged in.")

        try:
            user = await FPL.get_user(self)
            print(vars(user))
            users_team = await FPL.get_users_team(self, user)
            event = 0
            print(users_team)

            event = users_team["current_event"] if users_team["current_event"] else 0
            payload = {
                "confirmed": False,
                "entry": users_team["id"],
                "event": event + 1,
                "transfers": [],
                "wildcard": wildcard,
                "freehit": free_hit,
            }
            print("payload: ", payload)

            for player_out_id, player_in_id in zip(players_out, players_in):
                player_out = next(
                    player for player in user_team if player["element"] == player_out_id
                )
                player_in = next(
                    player for player in players if player["id"] == player_in_id
                )
                payload["transfers"].append(
                    {
                        "element_in": player_in["id"],
                        "element_out": player_out["element"],
                        "purchase_price": player_in["now_cost"],
                        "selling_price": player_out["selling_price"],
                    }
                )
                print("payload: ", payload)
            return payload
        except aiohttp.client_exceptions.ClientResponseError:
            raise Exception("User ID does not match provided email address!")

    async def transfer(
        self, players_out, players_in, max_hit=60, wildcard=False, free_hit=False
    ):
        """Transfers given players out and transfers given players in.

        :param players_out: List of IDs of players who will be transferred out.
        :type players_out: list
        :param players_in: List of IDs of players who will be transferred in.
        :type players_in: list
        :param max_hit: Maximum hit that should be taken by making the
            transfer(s), defaults to 60
        :param max_hit: int, optional
        :param wildcard: Boolean for playing wildcard, defaults to False
        :param wildcard: bool, optional
        :param free_hit: Boolean for playing free hit, defaults to False
        :param free_hit: bool, optional
        :return: Returns the response given by a succesful transfer.
        :rtype: dict
        """

        if not self.logged_in():
            raise Exception("User must be logged in.")

        user = await FPL.get_user(self)

        if wildcard and free_hit:
            raise Exception("Can only use 1 of wildcard and free hit.")

        if not self.logged_in():
            raise Exception("User must be logged in.")

        if not players_in:
            raise Exception("Must at Least Transfer players In")

        if len(players_out) != len(players_in):
            raise Exception(
                "Number of players transferred in must be same as "
                "number transferred out."
            )

        if not set(players_in).isdisjoint(players_out):
            raise Exception("Player ID can't be in both lists.")

        user_players = await FPL.get_users_players(self, user)
        print(user_players)
        team_ids = [player["element"] for player in user_players]

        if not set(team_ids).isdisjoint(players_in):
            raise Exception(
                "Cannot transfer a player in who is already in the user's team."
            )

        if set(team_ids).isdisjoint(players_out):
            raise Exception(
                "Cannot transfer a player out who is not in the user's team."
            )

        players = await FPL.get_all_current_players(self, return_json=True)

        # fl = [player.web_name for player in players if player.id == 91]

        player_ids = [player["id"] for player in players]

        if set(player_ids).isdisjoint(players_in):
            raise Exception("Player ID in `players_in` does not exist.")

        # Send POST requests with `confirmed` set to False; this basically
        # checks if there are any errors from FPL's side for this transfer,
        # e.g. too many players from the same team, or not enough money.
        print(players_out)
        print(players_in)
        print(user_players)
        print(players)
        payload = await self._get_transfer_payload(
            players_out, players_in, user_players, players, wildcard, free_hit
        )
        headers = utils.get_headers(
            "https://fantasy.premierleague.com/a/squad/transfers"
        )
        post_response = await post_transfer(
            self.session,
            endpoints["API"]["TRANSFERS"].format(),
            json.dumps(payload),
            headers,
        )

        if post_response is None:
            print("EUREKA BABY")
            payload["confirmed"] = True
            post_response = await post(
                self.session,
                endpoints["API"]["TRANSFERS"],
                json.dumps(payload),
                headers,
            )
            return post_response

        if "non_form_errors" in post_response:
            raise Exception(post_response["non_form_errors"])

        if post_response["spent_points"] > max_hit:
            raise Exception(
                f"Point hit for transfer(s) [-{post_response['spent_points']}]"
                f" exceeds max_hit [{max_hit}]."
            )

    # async def substitute(self, players_in, players_out, captain=None,
    #                      vice_captain=None):
    #     """Substitute players on the bench for players in the starting eleven.
    #     Also allows the user to simultaneously set the new (vice) captain(s).
    #     A maximum of 4 substitutes is set to force proper usage.
    #
    #     :param players_in: List of IDs of players who will be substituted in.
    #     :type players_in: list
    #     :param players_out: List of IDS of players who will be substituted out.
    #     :type players_out: list
    #     :param captain: ID of the captain, defaults to None.
    #     :param captain: int, optional
    #     :param vice_captain: ID of the vice captain, defaults to None.
    #     :param vice_captain: int, optional
    #     """
    #     if not logged_in(self._session):
    #         raise Exception("User must be logged in.")
    #
    #     if len(players_out) > 4 or len(players_in) > 4:
    #         raise Exception("Can only substitute a maximum of 4 players.")
    #
    #     if len(players_out) != len(players_in):
    #         raise Exception("Number of players substituted in must be same as "
    #                         "number substituted out.")
    #
    #     if not set(players_in).isdisjoint(players_out):
    #         raise Exception("Player ID can't be in both lists.")
    #
    #     user_team = await self.get_team()
    #     team_ids = [player["element"] for player in user_team]
    #     substitution_ids = players_out + players_in
    #
    #     if not set(substitution_ids).issubset(team_ids):
    #         raise Exception(
    #             "Cannot substitute players who aren't in the user's team.")
    #
    #     # Set new captain or vice captain if applicable
    #     if captain:
    #         _set_captain(user_team, captain, is_c, team_ids)
    #
    #     if vice_captain:
    #         _set_captain(user_team, vice_captain, is_vc, team_ids)
    #
    #     lineup = await self._create_new_lineup(
    #         players_in, players_out, user_team)
    #
    #     await self._post_substitutions(lineup)
