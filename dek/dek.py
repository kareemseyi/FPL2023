import sys
from collections import Counter
from api.FPL import FPL
import aiohttp
import asyncio
import requests

async def test():
    session = aiohttp.ClientSession(trust_env=True)
    fpl = FPL(session)
    await fpl.login()
    if fpl.logged_in():
        print("Logged in for GW")
        user = await fpl.get_user()
        print(user)

        # try:
        #     my_team = await fpl.get_users_team2(user)
        #     print(my_team)
        # except Exception as err:
        #     pass
        # transfer_status = await fpl.transfer([235, 495, 360], [91, 339, 186]) # Order Matters here
        # print(transfer_status)

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

