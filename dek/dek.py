import sys

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
    if fpl.logged_in():
        print("Logged in for GW")
        current_fixtures = await handler.get_remaining_fixtures(session)
        print(current_fixtures[0])
    await session.close()
    return len(current_fixtures)


async def test():
    session = aiohttp.ClientSession(trust_env=True)
    fpl = FPL(session)
    await fpl.login()
    if fpl.logged_in():
        print("Logged in for GW")
        teams = await handler.get_teams(fpl)
        print(teams)
        user = await fpl.get_user()
        # print(user)
        # players = await handler.get_players(session)
        # print(players)
        try:
            my_team = await fpl.get_users_team(user, 1)
            print(my_team)
        except Exception as err:
            print(err)
            sys.exit()
            pass


        # print(my_team)

        # my_team_cleaned = [handler.get_player(players, x['element'])for x in my_team]
        # print(my_team_cleaned)

        # gw = await handler.get_upcoming_gameweek(session)
        # print(gw)

        #
        # my_team = await handler.get_users_team(session, user_obj, 27)
        # player = await handler.get_player(session,my_team[5]['element'])
        #
        # print(my_team)
        # print(player.roi())
        #
        # fixtures_for_gameweek = await handler.get_fixtures_for_gameweek(session, gw)
        # print(fixtures_for_gameweek[0].stats["goals_scored"])
        # print(fixtures_for_gameweek[0].team_a)
        # print(fixtures_for_gameweek[0].team_h)

        # for i in fixtures_for_gameweek:
        #     print(str(i))

    await session.close()
    return len(teams)


asyncio.run(test())

