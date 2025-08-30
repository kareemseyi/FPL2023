import sys
from collections import Counter
from api.FPL import FPL
from auth.fpl_auth import FPLAuth
import aiohttp
import asyncio
import requests


game_week = None
fixtures = None
players = None




async def test():
    session = aiohttp.ClientSession(trust_env=True)
    auth = FPLAuth(session)
    fpl = FPL(session, auth)
    token = await fpl.login()


    if fpl.logged_in():
        print("Logged in for GW")
        user = await fpl.get_user()
        print("user:", user)
        try:
            my_team = await fpl.get_users_team(user)
            print('my_team', my_team)
        except Exception as err:
            'Cant get users team info from FPL'
        try:
            my_players = await fpl.get_users_players(user)
            print('my_players', my_players)
        except Exception as err:
            'Cant get users players from FPL'
        try:
            game_week = await fpl.get_upcoming_gameweek()
            print('next_gameweek', game_week)
            fixtures = await fpl.get_fixtures_for_next_GW(int(game_week))
            for i in fixtures:
                print(str(i))
        except Exception as err:
            'Cant get next gameweek from FPL'


        # a = FullHistorical.getHistoricalPlayers(n=2)
        # a.sort(key=lambda x: x.points_per_Min(), reverse=True)
        # mean_roi = statistics.mean([x.roi_per_Min() for x in a if x.season == '2023-24'])
        # print(mean_roi)
        # top_players = [x for x in a if x.roi_per_Min() > mean_roi and x.season == '2023-24']
        # for i in top_players:
        #     top_current_player = await fpl.get_current_player(player=i, convert_hist=True)
        #     current_top_players.append(top_current_player)
        #
        # print(len(current_top_players))
        #
        # for i in current_top_players[0:10]:
        #     print(i)
    await session.close()
    return 'Mum is here'






asyncio.run(test())

