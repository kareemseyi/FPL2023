from api.FPL import FPL
import aiohttp
import asyncio
from api import handler


async def fpl_login():
    fpl = FPL(aiohttp.ClientSession(trust_env=True))
    await fpl.login()


async def get_current_fixtures():
    global current_fixtures
    session = aiohttp.ClientSession(trust_env=True)
    fpl = FPL(session)
    await fpl.login()
    if handler.logged_in(session):
        print("Logged in for GW")
        current_fixtures = await handler.get_remaining_fixtures(session)
        print(current_fixtures[0])
    await session.close()
    return len(current_fixtures)

async def get_teams():
    session = aiohttp.ClientSession(trust_env=True)
    fpl = FPL(session)
    await fpl.login()
    if handler.logged_in(session):
        print("Logged in for GW")
        teams = await handler.get_teams(session)
        # print(teams)
        user = await handler.get_current_user(session)
        print(user)
        players = await handler.get_players(session)
        print(players)

        user_obj = await handler.get_user(session)
        print(user_obj.id)

        my_team = await handler.get_users_team(session, user_obj, 24)
        print(handler.get_player(players,my_team[0]['element']))

        print(my_team)

        my_team_cleaned = [handler.get_player(players, x['element'])for x in my_team]
        print(my_team_cleaned)

    await session.close()
    return len(teams)



asyncio.run(get_teams())

