from asyncio import exceptions
import collections
from constants import endpoints, POSITION_MAP
from json import JSONDecodeError
import logging
import tempfile
import requests
import certifi
import ssl
import http
from http import cookies
import secrets
import hashlib
import base64
from google.cloud import secretmanager, storage
import json
import os
import pandas as pd
from pycaret.regression import load_model

logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)",
    "accept-language": "en",
}

cookies = http.cookies.SimpleCookie()
ssl_context = ssl.create_default_context(cafile=certifi.where())


STATIC_BASE_URL = endpoints["STATIC"]["BASE_URL"]
FORM_WINDOW = 6


def headers_access(access_token):
    headers["Authorization"] = "Bearer {}".format(access_token)
    return headers


async def fetch(session, url, headers=None):
    async with session.get(
        url, headers=headers, ssl=ssl_context, cookies=cookies
    ) as response:
        assert response.status == 200
        return await response.json(content_type=None)


def position_converter(position):
    """Converts a player's `element_type` to their actual position."""
    return POSITION_MAP[position]


_team_cache = {}


def team_converter(team_id, team_dict=None):
    if team_dict:
        return team_dict.get(team_id)
    if not _team_cache:
        _team_cache.update(get_teams())
    return _team_cache.get(team_id)


def convert_team_form(form: str):
    score_map = {"W": 3, "D": 1, "L": 0}
    res = sum(score_map.get(c, 0) for c in form)
    return float(res / (len(form) * 3))


def fixture_results(fixtures) -> list[tuple[str, str, int, int]]:
    """Returns (home, away, home_score, away_score) per finished Fixture, by kickoff."""
    finished = sorted(
        (fixture for fixture in fixtures if fixture.finished),
        key=lambda fixture: fixture.kickoff_time,
    )
    return [
        (
            fixture.team_h,
            fixture.team_a,
            int(fixture.team_h_score),
            int(fixture.team_a_score),
        )
        for fixture in finished
    ]


def match_letters(home_score: int, away_score: int) -> tuple[str, str]:
    """Returns the (home, away) result letters for a score."""
    if home_score == away_score:
        return "D", "D"
    if home_score > away_score:
        return "W", "L"
    return "L", "W"


def season_form(results: list[tuple[str, str, int, int]]) -> dict[str, str]:
    """Each team's results in kickoff order, e.g. "WDLW..."."""
    form = collections.defaultdict(list)
    for home, away, home_score, away_score in results:
        home_letter, away_letter = match_letters(home_score, away_score)
        form[home].append(home_letter)
        form[away].append(away_letter)
    return {team: "".join(letters) for team, letters in form.items()}


def fixture_difficulty(results: list[tuple[str, str, int, int]]) -> dict[str, float]:
    """Averages each team's form advantage over its opponents, using pre-match form.

    Form is each side's last FORM_WINDOW results before kickoff. Fixtures where
    either side has no previous result are skipped, so teams with none counted
    are absent from the result.
    """
    history = collections.defaultdict(list)
    totals = collections.defaultdict(float)
    counted = collections.Counter()
    for home, away, home_score, away_score in results:
        home_recent = history[home][-FORM_WINDOW:]
        away_recent = history[away][-FORM_WINDOW:]
        if home_recent and away_recent:
            advantage = convert_team_form(home_recent) - convert_team_form(away_recent)
            totals[home] += advantage
            totals[away] -= advantage
            counted.update((home, away))
        home_letter, away_letter = match_letters(home_score, away_score)
        history[home].append(home_letter)
        history[away].append(away_letter)
    return {team: totals[team] / counted[team] for team in counted}


def get_teams():
    dynamic = requests.get(STATIC_BASE_URL).json()
    return {team["id"]: team["name"] for team in dynamic["teams"]}


def get_team(team_id, team_dict=None):
    if team_dict:
        return team_dict.get(team_id)


def get_headers(referer):
    """Returns the headers needed for the transfer request."""
    return {
        "Content-Type": "application/json;charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": referer,
    }


# def get_transfer_candidates(my_team, player_pool,max=3):
async def post(session, url, payload, headers):
    async with session.post(url, data=payload, headers=headers) as response:
        return await response.json()


async def post_transfer(session, url, payload, headers):
    async with session.post(url, data=payload, headers=headers) as response:
        if response.status == 200:
            return
        try:
            result = await response.json(content_type=None)
        except JSONDecodeError:
            result = await response.text()
            raise Exception(
                f"Unknown error while requesting {response.url}. {response.status} - {result}"
            )

        if result.get("errorCode"):
            message = result.get("error")

            raise Exception(message if message else result)


def generate_code_verifier():
    return secrets.token_urlsafe(64)[:128]


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def get_credentials_from_secret_manager():
    """Fetch credentials from Google Secret Manager.

    Returns:
        tuple: (email, password) retrieved from Secret Manager
    """
    try:
        project_id = os.getenv("GCP_PROJECT_ID", "ardent-quarter-468720-i2")
        secret_id = os.getenv("SECRET_ID", "fpl_2025_credentials")

        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

        response = client.access_secret_version(request={"name": secret_name})
        secret_data = response.payload.data.decode("UTF-8")

        credentials = json.loads(secret_data)
        return credentials.get("email"), credentials.get("password")
    except Exception as e:
        logger.error("Error fetching credentials from Secret Manager: %s", e)
        return None, None


def check_file_exists_google_cloud(bucket_name, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    stats = storage.Blob(bucket=bucket, name=file_name).exists(storage_client)
    return stats


def read_file_from_google_storage(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    logger.info(
        "Downloaded storage object %s from bucket %s to local file %s.",
        source_blob_name,
        bucket_name,
        destination_file_name,
    )


def write_file_to_google_storage(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    logger.info("File %s uploaded to %s.", source_file_name, destination_blob_name)


def load_model_from_google_storage(bucket_name, blob_name, local_fallback_path):
    """Load a PyCaret model from GCS, falling back to a local path.

    PyCaret's load_model() expects a path without the .pkl extension.

    Args:
        bucket_name: GCS bucket name.
        blob_name: Path to .pkl file in the bucket.
        local_fallback_path: Local model path (without .pkl extension).

    Returns:
        Loaded PyCaret model.
    """
    if check_file_exists_google_cloud(bucket_name, blob_name):
        logger.info("Model found in GCS bucket %s/%s", bucket_name, blob_name)
        tmp_dir = tempfile.mkdtemp()
        local_pkl = os.path.join(tmp_dir, os.path.basename(blob_name))
        read_file_from_google_storage(bucket_name, blob_name, local_pkl)
        # load_model expects path without .pkl
        return load_model(local_pkl.removesuffix(".pkl"))

    logger.info("Model not in GCS, loading from local path: %s", local_fallback_path)
    return load_model(local_fallback_path)


PERFORMANCE_COLUMNS = [
    "game_week",
    "my_points",
    "average_points",
    "highest_points",
    "total_points",
    "delta_vs_avg",
    "delta_vs_highest",
    "timestamp",
]


def read_performance_from_gcs(bucket_name, blob_name):
    """Read weekly performance CSV from GCS.

    Args:
        bucket_name: GCS bucket name.
        blob_name: Path to CSV file in the bucket.

    Returns:
        DataFrame with performance data, or empty DataFrame if not found.
    """
    if not check_file_exists_google_cloud(bucket_name, blob_name):
        logger.info("No existing performance file found, starting fresh.")
        return pd.DataFrame(columns=PERFORMANCE_COLUMNS)

    tmp_dir = tempfile.mkdtemp()
    local_file = os.path.join(tmp_dir, "performance.csv")
    read_file_from_google_storage(bucket_name, blob_name, local_file)
    return pd.read_csv(local_file)


def write_performance_to_gcs(df, bucket_name, blob_name):
    """Write performance DataFrame as CSV to GCS.

    Args:
        df: Performance DataFrame.
        bucket_name: GCS bucket name.
        blob_name: Destination path in the bucket.
    """
    tmp_dir = tempfile.mkdtemp()
    local_file = os.path.join(tmp_dir, "performance.csv")
    df.to_csv(local_file, index=False)
    write_file_to_google_storage(bucket_name, local_file, blob_name)
