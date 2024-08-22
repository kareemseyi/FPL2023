import sys
from collections import Counter
from api.FPL import FPL
import aiohttp
import asyncio
import statistics
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
        print('waiting')
        players = await fpl.get_all_current_players()
        current_top_players = []


        # try:
        #     my_team = await fpl.get_users_team2(user)
        #     print(my_team)
        # except Exception as err:
        #     pass
        # transfer_status = await fpl.transfer([235, 495, 360], [91, 339, 186]) # Order Matters here
        # print(transfer_status)

        # a = FullHistorical.getHistoricalPlayers()
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


        winners = set()
        next_gw = await fpl.get_upcoming_gameweek()
        print(next_gw)
        fixt_ = await fpl.get_all_fixtures(*range(next_gw, next_gw+4))
        for i in fixt_:
            print(vars(i))
            if i.team_h_difficulty > i.team_a_difficulty:
                winners.add(i.get_home_team())
            if i.team_h_difficulty < i.team_a_difficulty:
                winners.add(i.get_away_team())
        #     teamlist.append(i.get_home_team())
        #     teamlist.append(i.get_away_team())
        # occ = Counter(teamlist)
        print(winners)
        # teams = await fpl.get_team(team_names=teamlist)
        # for i in teams:
        #     print(vars(i))
        # await fpl.pickTeam(next_gw, initial=False)

        # my_team_cleaned = [handler.get_player(players, x['element'])for x in my_team]
        # print(my_team_cleaned)


        # fixt_ = await fpl.get_all_fixtures(*range(next_gw-4, next_gw-1))

        # my_team = await handler.get_users_team(session, user_obj, 27)
        # player = await handler.get_player(session,my_team[5]['element'])
        #
        # print(my_team)
        # print(player.roi())
        #
        # fixtures_for_gameweek = await fpl.get_all_fixtures(1,2,3,4,5)
        # for i in fixt_:
        #     print(vars(i))
        #     print(i.is_draw())
        #     print(i.get_winner())

    await session.close()
    return 'Mum is here'


asyncio.run(test())

