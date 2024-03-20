from utils import position_converter, team_converter


class Player:
    """A class representing a player in the Fantasy Premier League.

    """
    def __init__(self, player_information):
        for k, v in player_information.items():
            if k == "now_cost":  # Fix for cost of player
                v = float(int(v) / 10)
            if k in ('total_points', 'minutes'):
                v = int(v)

            setattr(self, k, v)

    def games_played(self):
        """The number of games where the player has played at least 1 minute.

        :rtype: int
        """
        return sum([1 for fixture in getattr(self, "fixtures", []) if fixture["minutes"] > 0])

    def points_per_GW(self):
        """Points per Gameweek

        :rtype: float
        """
        games_played = self.games_played()
        if games_played == 0:
            return 0
        return getattr(self, "total_points", 0) / float(games_played)

    def points_per_Min(self):
        """Points per Gameweek

        :rtype: float
        """
        mins = getattr(self, 'minutes', 0)
        if mins == 0:
            return 0
        return getattr(self, "total_points", 0) / mins

    def roi(self):
        cost = getattr(self, "now_cost", 0)
        try:
            return getattr(self, "total_points", 0) / cost
        except ZeroDivisionError:
            return 0

    def roi_per_GW(self):
        try:
            return float(self.roi() / self.games_played())
        except ZeroDivisionError:
            pass

    def roi_per_Min(self):
        mins = getattr(self, 'minutes', 0)
        try:
            return self.roi() / mins
        except ZeroDivisionError:
            return 0

    def goalcontributions_per_Min(self):
        mins = getattr(self, 'minutes', 0)
        try:
            assert mins > 0
            return getattr(self, 'goals') + getattr(self, 'assists') / getattr(self, 'minutes')
        except ZeroDivisionError:
            pass

    def __str__(self):
        if getattr(self, "season", None):
            return (f"{(self.first_name)} - "
                    f"{self.second_name} - "
                    f"{self.season}")
        return (f"{(self.web_name)} - "
                f"{position_converter(self.element_type)} - "
                f"{team_converter(self.team)}")
