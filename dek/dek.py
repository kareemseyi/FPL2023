import sys

from api.FPL import FPL
import aiohttp
import asyncio
from api import handler
from historical import FullHistorical

async def test():
    session = aiohttp.ClientSession(trust_env=True)
    fpl = FPL(session)
    await fpl.login()
    if fpl.logged_in():
        print("Logged in for GW")
        user = await fpl.get_user()
        print(user)
        players = await fpl.get_all_current_players()
        print(players[0])
        print(players[1])
        print(players[2])

        # try:
        #     my_team = await fpl.get_users_team(user, 1)
        # except Exception as err:
        #     pass

        # a = FullHistorical.getHistoricalPlayers()
        # a.sort(key=lambda x: x.points_per_Min(), reverse=True)
        # top_players = [x for x in a if x.roi_per_Min() > 0.2 and x.season == '']
        # print(len(a))
        # for i in a[0:10]:
        #     print(vars(i))
        #     print(i.roi_per_Min(), i.points_per_Min())

        next_gw = await fpl.get_upcoming_gameweek()
        print(next_gw)
        # fixt_ = await fpl.get_all_fixtures(*range(next_gw, next_gw+3))
        #
        # for i in fixt_:
        #     print(vars(i))

        teams = await fpl.get_team(team_names=['Arsenal', 'Liverpool', 'Chelsea'])
        for i in teams:
            print(vars(i))
        await fpl.pickTeam(next_gw, initial=False)

        # my_team_cleaned = [handler.get_player(players, x['element'])for x in my_team]
        # print(my_team_cleaned)

        # gw = await handler.get_upcoming_gameweek(session)
        # # print(gw)

        #
        # my_team = await handler.get_users_team(session, user_obj, 27)
        # player = await handler.get_player(session,my_team[5]['element'])
        #
        # print(my_team)
        # print(player.roi())
        #
        # fixtures_for_gameweek = await fpl.get_all_fixtures(1,2,3,4,5)
        # for i in fixtures_for_gameweek:
        #     print(vars(i))

    await session.close()
    return 'Mum is here'


asyncio.run(test())

