from utils import position_converter, team_converter


class Player:
    """A class representing a player in the Fantasy Premier League."""

    def __init__(self, player_information):
        for k, v in player_information.items():
            if k == "now_cost":  # Fix for cost of player
                v = float(int(v) / 10)
            if k in ("total_points", "minutes"):
                v = int(v)

            setattr(self, k, v)

    def games_played(self):
        """The number of games where the player has played at least 1 minute.

        :rtype: int
        """
        fixtures = getattr(self, "fixtures", [])
        if fixtures:
            return sum([1 for fixture in fixtures if fixture["minutes"] > 0])
        return getattr(self, "starts", 0)

    def points_per_game(self):
        """Points per Gameweek
        :rtype: float
        """
        try:
            return getattr(self, "total_points", 0) / self.games_played()
        except ZeroDivisionError:
            return 0

    def points_per_min(self):
        """Points per Gameweek
        :rtype: float
        """
        mins = getattr(self, "minutes", 0)
        try:
            return getattr(self, "total_points", 0) / mins
        except ZeroDivisionError:
            return 0

    def _position(self):
        if getattr(self, "element_type", None):
            return position_converter(getattr(self, "element_type"))
        if getattr(self, "position", None):
            return getattr(self, "position")
        return "MID"  # Default fallback

    def roi(self):
        cost = getattr(self, "now_cost", 0)
        try:
            return float(getattr(self, "total_points", 0) / cost)
        except ZeroDivisionError:
            return 0

    def roi_per_gw(self):
        try:
            return float(self.roi() / self.games_played())
        except ZeroDivisionError:
            return 0

    def roi_per_min(self):
        mins = getattr(self, "minutes", 0)
        try:
            return float(self.roi() / mins)
        except ZeroDivisionError:
            return 0

    def goal_contributions_per_min(self):
        mins = getattr(self, "minutes", 0)
        if mins <= 0:
            return 0
        goals = getattr(self, "goals_scored", 0)
        assists = getattr(self, "assists", 0)
        return float((goals + assists) / mins)

    def __str__(self):
        if isinstance(getattr(self, "team"), str):
            return (
                f"{(self.first_name)} - "
                f"{self.second_name} - "
                f"{(self.team)}"
                f"{self._position()} - "
            )
        return (
            f"{(self.first_name)} - "
            f"{self.second_name} - "
            f"{self._position()} - "
            f"{team_converter(self.team)}"
        )
