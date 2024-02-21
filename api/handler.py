import asyncio
import pytest


async def fetch(session, url):
    while True:
        try:
            async with session.get(url) as response:
                assert response.status == 200
                return await response.json()
        except Exception as e:
            pass


async def post(session, url, payload, headers):
    async with session.post(url, data=payload, headers=headers) as response:
        return await response.json()


def logged_in(session):
    """Checks that the user is logged in within the session.

    :param session: http session
    :type session: aiohttp.ClientSession
    :return: True if user is logged in else False
    :rtype: bool
    """
    return "csrftoken" in session.cookie_jar.filter_cookies(
        "https://users.premierleague.com/")


async def get_current_gameweek(session):
    """Returns the current gameweek.

    :param aiohttp.ClientSession session: A logged in user's session.
    :rtype: int
    """
    dynamic = await fetch(
        session, "https://fantasy.premierleague.com/drf/bootstrap-dynamic")

    return dynamic["entry"]["current_event"]




async def get_fixtures(session):
    """Returns the current gameweek.

    :param aiohttp.ClientSession session: A logged in user's session.
    :rtype: int
    """
    dynamic = await fetch(
        session, "https://fantasy.premierleague.com/drf/bootstrap-dynamic")

    return dynamic["entry"]["current_event"]
