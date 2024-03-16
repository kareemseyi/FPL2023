from asyncio import exceptions

from api import handler
from endpoints import endpoints
import requests
API_BASE_URL = endpoints['STATIC']['BASE_URL']

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


def position_converter(position):
    """Converts a player's `element_type` to their actual position."""
    position_map = {
        1: "Goalkeeper",
        2: "Defender",
        3: "Midfielder",
        4: "Forward"
    }
    return position_map[position]


def team_converter(team_id):
    try:
        dynamic = requests.get(API_BASE_URL).json()
    except exceptions.RequestException as e:
        raise e
    teamname_list = [team["name"] for team in dynamic["teams"]]
    teamdict = {dynamic["teams"][i]["id"]: dynamic["teams"][i]["name"] for i in range(len(teamname_list))}
    return teamdict[team_id]