import asyncio
import warnings
import itertools

import utils
from endpoints import endpoints
from utils import fetch, get_team
from dataModel.player import Player
from dataModel.team import Team
from dataModel.fixture import Fixture

MAX_DEF = 5
MAX_GK = 2
MAX_MID = 5
MAX_FWD = 3
MAX_BUDGET = 100
MAX_PLAYER_FROM_TEAM = 3

STATIC_BASE_URL = endpoints["STATIC"]["BASE_URL"]
API_GW_FIXTURES = endpoints["API"]["GW_FIXTURES"]
API_ALL_FIXTURES = endpoints["API"]["ALL_FIXTURES"]

is_c = "is_captain"
is_vc = "is_vice_captain"
roi_list = []
teamid_list_g = []
data_dict = []


class FPLHelpers:
    """Helper class for FPL operations that don't require authentication."""

    def __init__(self, session):
        self.session = session

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
            players = data["elements"]
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
            tasks = [
                asyncio.ensure_future(self.get_current_player(player=player))
                for player in players
            ]
            players = await asyncio.gather(*tasks)
            return players

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
        data = await fetch(self.session, STATIC_BASE_URL)
        players = data["elements"]
        if not player and player_id:
            try:
                player = next(player for player in players if player["id"] == player_id)
            except StopIteration:
                raise ValueError(f"Player with ID {player_id} not found")
            if return_json:
                return player
        if player and convert_hist:
            try:
                player = next(
                    x
                    for x in players
                    if (
                        x["first_name"] == player.first_name
                        and x["second_name"] == player.second_name
                    )
                    or x["web_name"] == player.first_name + " " + player.second_name
                )
            except StopIteration:
                warnings.warn(
                    f"Player name {player.first_name} {player.second_name} not found, Might not be in the EPL"
                    f"anymore Dawg"
                )
                pass
        return Player(player)

    async def get_team(self, *team_ids, team_names=None):
        try:
            response = await fetch(self.session, STATIC_BASE_URL)
        except Exception:
            raise Exception("Failed to fetch team data")
        teams = response["teams"]
        if team_ids:
            team = (team for team in teams if team["id"] in team_ids)
        else:
            team = (team for team in teams if team["name"] in team_names)
        return [Team(team, self.session) for team in team]

    async def prepareData(self):
        try:
            response = await fetch(self.session, STATIC_BASE_URL)
            team_dict = utils.get_teams()
        except Exception:
            raise Exception("Failed to fetch team data")
        sorted_players = response["elements"]
        for baller in sorted_players:
            goals = baller["goals_scored"]
            assists = baller["assists"]
            goal_contributions = baller["goals_scored"] + baller["assists"]
            games_played = baller["starts"]
            minutes = baller["minutes"]
            teamname = utils.get_team(baller["team"], team_dict)
            roi = float(f"{(baller['total_points'] / (baller['now_cost'] / 10)):000.4}")

            roi_list.append(roi)  # add all ROIs for all players
            teamid_list_g.append(baller["team"])

            if baller["element_type"] == 1:
                pos = "GK"
            elif baller["element_type"] == 2:
                pos = "DEF"
            elif baller["element_type"] == 3:
                pos = "MID"
            else:
                pos = "FWD"

            diction = {
                "name": baller["web_name"],
                "price": round(baller["now_cost"] / 10, 2),
                "games_played": int(games_played),
                "goals": int(goals),
                "assists": int(assists),
                "goal_contributions": int(goal_contributions),
                "total_points": int(baller["total_points"]),
                "points_per_game": float(baller["points_per_game"]),
                "roi": float(roi),
                "position": pos,
                "team": teamname,
                "minutes": int(minutes),
                "FDR_Average": 0,
            }

            data_dict.append(diction)
        return data_dict

    @staticmethod
    def set_captain(lineup, captain, captain_type, player_ids):
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
        if captain and captain not in player_ids:
            raise ValueError("Cannot (vice) captain player who isn't in user's team.")

        current_captain = next(player for player in lineup if player[captain_type])
        chosen_captain = next(
            player for player in lineup if player["element"] == captain
        )

        # If the chosen captain is already a (vice) captain, then give his previous
        # role to the current (vice) captain.
        if chosen_captain[is_c] or chosen_captain[is_vc]:
            current_captain[is_c], chosen_captain[is_c] = (
                chosen_captain[is_c],
                current_captain[is_c],
            )
            current_captain[is_vc], chosen_captain[is_vc] = (
                chosen_captain[is_vc],
                current_captain[is_vc],
            )

        for player in lineup:
            player[captain_type] = False

            if player["element"] == captain:
                player[captain_type] = True

    async def get_all_fixtures(self, *gameweek):
        """Returns all fixtures for the specified gameweeks.

        :param gameweek: Gameweek numbers to fetch fixtures for
        :rtype: list
        """
        task = asyncio.ensure_future(fetch(self.session, API_ALL_FIXTURES))

        gameweek_fixtures = await asyncio.gather(task)
        fixtures = list(itertools.chain(*gameweek_fixtures))

        team_dict = utils.get_teams()
        return [
            Fixture(fixture, team_dict)
            for fixture in fixtures
            if fixture["event"] in gameweek
        ]

    async def get_upcoming_gameweek(self):
        """Returns the upcoming gameweek number.

        :rtype: int
        """
        try:
            response = await fetch(self.session, API_GW_FIXTURES)
            gw = max([x["event"] for x in response if x["finished"] is True])
            # This is the previous gameweek
        except Exception:
            Warning("Start of the season, gameweek 1")
            return 1
        if len(response) == 0:
            raise Exception("No Active Events yet.... TODO")

        return int(gw) + 1  # Adds one to previous gameweek

    async def get_fixtures_for_gameweek(self, gameweek: int):
        """Returns the fixtures for the current gameweek.

        :param gameweek: The gameweek number
        :type gameweek: int
        :rtype: list
        """
        try:
            response = await fetch(self.session, API_GW_FIXTURES.format(f=gameweek))
        except Exception:
            raise Exception("Failed to fetch fixtures for gameweek")

        team_dict = get_team()
        fixtures = [x for x in response if x["event"] == gameweek]
        return [Fixture(fixture, team_dict=team_dict) for fixture in fixtures]


def get_transfer_in_candidates(team, player_pool):
    """Utility function for getting transfer candidates.

    :param team: Current team
    :param player_pool: Available player pool
    :return: Transfer candidates
    """
    pass


def get_transfer_out_candidates(team, player_pool):
    """Utility function for getting transfer candidates.

    :param team: Current team
    :param player_pool: Available player pool
    :return: Transfer candidates
    """
    pass
