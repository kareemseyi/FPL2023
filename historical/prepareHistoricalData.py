"""Builds historical/_summary/FPL_data_<season>.csv for model training.

Inputs from https://github.com/vaastav/Fantasy-Premier-League/tree/master/data/<season>:
    teams.csv       -> historical/_teams/teams_<season>.csv
    players_raw.csv -> historical/_summary/players_raw_<season>.csv

Usage (from repo root): python -m historical.prepareHistoricalData 25_26
"""

import argparse
import csv
import pathlib
import sys

from constants import PLAYER_DATA_SCHEMA

_HISTORICAL_DIR = pathlib.Path(__file__).resolve().parent
_TEAMS_DIR = _HISTORICAL_DIR / "_teams"
_SUMMARY_DIR = _HISTORICAL_DIR / "_summary"


def load_team_names(teams_path: pathlib.Path) -> dict[int, str]:
    """Maps team id to team name."""
    with open(teams_path, mode="r", newline="") as teams:
        return {int(team["id"]): team["name"] for team in csv.DictReader(teams)}


def build_player_row(baller: dict[str, str], team_names: dict[int, str]) -> dict:
    """Converts a players_raw.csv row into a PLAYER_DATA_SCHEMA row."""
    goals_scored = int(baller["goals_scored"])
    assists = int(baller["assists"])
    starts = int(baller["starts"])
    roi = float(
        f"{(int(baller['total_points']) / (int(baller['now_cost']) / 10)):0000000.4}"
    )

    row = PLAYER_DATA_SCHEMA.copy()
    row.update(
        {
            "first_name": baller["first_name"],
            "second_name": baller["second_name"],
            "now_cost": round(int(baller["now_cost"]) / 10, 2),
            "starts": starts,
            "goals_scored": goals_scored,
            "assists": assists,
            "goal_contributions": goals_scored + assists,
            "total_points": int(baller["total_points"]),
            "points_per_game": float(baller["points_per_game"]),
            "roi": roi,
            "roi_per_gw": roi / starts if starts > 0 else 0,
            "element_type": baller["element_type"],
            "team": baller["team"],
            "minutes": int(baller["minutes"]),
            "FDR_Average": 0.0,
            "team_name": team_names[int(baller["team"])],
            "id": int(baller["id"]),
        }
    )
    return row


def prepare(season: str) -> pathlib.Path:
    """Writes FPL_data_<season>.csv and returns its path."""
    teams_path = _TEAMS_DIR / f"teams_{season}.csv"
    players_path = _SUMMARY_DIR / f"players_raw_{season}.csv"
    for required in (teams_path, players_path):
        if not required.is_file():
            raise FileNotFoundError(
                f"Missing {required}. Download it from vaastav's "
                "Fantasy-Premier-League repo (see this module's docstring)."
            )

    team_names = load_team_names(teams_path)
    with open(players_path, mode="r", newline="") as players:
        rows = [
            build_player_row(baller, team_names) for baller in csv.DictReader(players)
        ]

    output_path = _SUMMARY_DIR / f"FPL_data_{season}.csv"
    with open(output_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=PLAYER_DATA_SCHEMA.keys())
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("season", help='e.g. "25_26"')
    args = parser.parse_args()
    try:
        output_path = prepare(args.season)
    except FileNotFoundError as error:
        sys.exit(str(error))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
