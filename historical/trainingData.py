"""Adds FDR_Average to FPL_data_<season>.csv and writes the model training file.

Run prepareHistoricalData first. Also needs fixtures.csv from
https://github.com/vaastav/Fantasy-Premier-League/tree/master/data/<season>
saved as historical/_fixtures/fixtures_<season>.csv.

Usage (from repo root): python -m historical.trainingData 25_26
"""

import argparse
import csv
import pathlib
import sys

import utils

_REPO_DIR = pathlib.Path(__file__).resolve().parents[1]
_HISTORICAL_DIR = _REPO_DIR / "historical"
_TRAINING_DIR = _REPO_DIR / "docker" / "datastore" / "training"


def load_team_names(teams_path: pathlib.Path) -> dict[int, str]:
    """Maps team id to team name."""
    with open(teams_path, mode="r", newline="") as teams:
        return {int(team["id"]): team["name"] for team in csv.DictReader(teams)}


def load_results(
    fixtures_path: pathlib.Path, team_names: dict[int, str]
) -> list[tuple[str, str, int, int]]:
    """Returns (home, away, home_score, away_score) per finished fixture, by kickoff."""
    with open(fixtures_path, mode="r", newline="") as fixtures:
        finished = [
            row for row in csv.DictReader(fixtures) if row["finished"] == "True"
        ]
    # Fixture ids follow the original schedule, so postponed games are out of order.
    finished.sort(key=lambda row: row["kickoff_time"])
    return [
        (
            team_names[int(row["team_h"])],
            team_names[int(row["team_a"])],
            int(row["team_h_score"]),
            int(row["team_a_score"]),
        )
        for row in finished
    ]


def build_training_data(season: str) -> pathlib.Path:
    """Writes the training CSV with FDR_Average filled and returns its path."""
    teams_path = _HISTORICAL_DIR / "_teams" / f"teams_{season}.csv"
    fixtures_path = _HISTORICAL_DIR / "_fixtures" / f"fixtures_{season}.csv"
    players_path = _HISTORICAL_DIR / "_summary" / f"FPL_data_{season}.csv"
    for required in (teams_path, fixtures_path, players_path):
        if not required.is_file():
            raise FileNotFoundError(
                f"Missing {required}. See this module's docstring for its source."
            )

    results = load_results(fixtures_path, load_team_names(teams_path))
    form = utils.season_form(results)
    fdr = utils.fixture_difficulty(results)
    for team in sorted(form):
        print(
            f"{team:<14} {form[team]}  form={utils.convert_team_form(form[team]):.3f}"
            f"  FDR={fdr[team]:.3f}"
        )

    with open(players_path, mode="r", newline="") as players:
        reader = csv.DictReader(players)
        fieldnames = reader.fieldnames
        rows = list(reader)
    missing = {row["team_name"] for row in rows} - fdr.keys()
    if missing:
        raise ValueError(f"No finished fixtures for: {', '.join(sorted(missing))}")
    for row in rows:
        row["FDR_Average"] = fdr[row["team_name"]]

    _TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    output_path = _TRAINING_DIR / f"FPL_data_{season}.csv"
    with open(output_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("season", help='e.g. "25_26"')
    args = parser.parse_args()
    try:
        output_path = build_training_data(args.season)
    except (FileNotFoundError, ValueError) as error:
        sys.exit(str(error))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
