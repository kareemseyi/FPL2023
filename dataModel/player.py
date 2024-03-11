class Player():
    """A class representing a player in the Fantasy Premier League.

    """
    def __init__(self, player_information):
        for k, v in player_information.items():
            setattr(self, k, v)

    def games_played(self):
        """The number of games where the player has played at least 1 minute.

        :rtype: int
        """
        return sum([1 for fixture in getattr(self, "fixtures", []) if fixture["minutes"] > 0])

    def pp90(self):
        """Points per 90 minutes.

        :rtype: float
        """
        minutes = getattr(self, "minutes", 0)
        if minutes == 0:
            return 0
        return getattr(self, "total_points", 0) / float(minutes)

    def roi(self):
        return float(getattr(self, "total_points", 0) / getattr(self, "now_cost", 0) / 10)


    def __str__(self):
        return (f"{self.web_name} - "
                f"{(self.element_type)} - "
                f"{(self.team)}")