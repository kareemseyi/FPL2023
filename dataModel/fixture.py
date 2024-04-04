from api import handler


class Fixture:
    """A class representing a fixture in Fantasy Premier League."""

    def __init__(self, fixture_information, team_dict):
        for k, v in fixture_information.items():
            if k == "team_a":
                v = handler.get_team(team_dict=team_dict, team_id=v)
            if k == "team_h":
                v = handler.get_team(team_dict=team_dict, team_id=v)
            if k == "stats":
                v = {w["identifier"]: {"a": w["a"], "h": w["h"]} for w in v}
            setattr(self, k, v)

    def get_home_team(self):
        return getattr(self, "team_h")

    def get_away_team(self):
        return getattr(self, "team_a")

    def __str__(self):
        return (f"{self.team_h} vs. "
                f"{self.team_a} - "
                f"{self.kickoff_time}")
