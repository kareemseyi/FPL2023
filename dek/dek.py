import sys
import pandas as pd
from api.FPL import FPL
from api.FPL_helpers import FPLHelpers
from auth.fpl_auth import FPLAuth
import aiohttp
import asyncio
from pycaret.classification import load_model, predict_model
from ml import currentData



game_week = None
fixtures = None
players = None


# async def test():
#     session = aiohttp.ClientSession(trust_env=True)
#     auth = FPLAuth(session)
#     fpl = FPL(session, auth)
#     if fpl.logged_in():
#         print("Logged in for GW")
#         user = await fpl.get_user()
#         print("user:", user)
#         try:
#             my_team = await fpl.get_users_team(user)
#             print("my_team", my_team)
#         except Exception as err:
#             "Cant get users team info from FPL"
#         try:
#             my_players = await fpl.get_users_players(user)
#             print("my_players", my_players)
#
#             for i in my_players:
#                 player = await fpl.get_current_player(player_id=i['element'])
#                 print("player", player)
#
#             all_players = await fpl.get_all_current_players()
#
#             mean_roi = statistics.mean([x.roi() for x in all_players])
#             mean_points_per_min = statistics.mean([x.points_per_Min() for x in all_players])
#             player_pool = [ x for x in all_players if x.roi() > mean_roi and x.points_per_Min() > mean_points_per_min]
#
#             player_pool.sort(key=lambda x: x.roi(), reverse=True)
#
#             roi_model = load_model('ml/Final Lightgbm Model ROI-Target.pkl')
#             print("✅ Model loaded successfully!")
#
#             for i in player_pool:
#                 print(i)
#
#         except Exception as err:
#             "Cant get users players from FPL"
#         try:
#             game_week = await fpl.get_upcoming_gameweek()
#             print("next_gameweek", game_week)
#             fixtures = await fpl.get_fixtures_for_next_GW(int(game_week))
#             for i in fixtures:
#                 print(str(i))
#         except Exception as err:
#             "Cant get next gameweek from FPL"
#
#     await session.close()


async def main():
    try:
        await asyncio.wait_for(currentData.getData(), timeout=60.0)

    except Exception as err:
        "Cant get current data from FPL"

    try:
        print('loading Model')
        roi_model = load_model('../ml/Final Lightgbm Model ROI-Target')
        print("ROI model loaded")
        session = aiohttp.ClientSession(trust_env=True)
        helpers = FPLHelpers(session)
        auth = FPLAuth(session)

        # fpl = FPL(session, auth)

        # if fpl.logged_in():
        #     user = await fpl.get_user()
        #     my_players = await fpl.get_users_players(user)
        #     print("my_players", my_players)
        #     for i in my_players:
        #         player = await fpl.get_current_player(player_id=i['element'])
        #         print("player", player)



        game_week = await helpers.get_upcoming_gameweek()
        print("Game Week: {}".format(game_week))
        unseen_data = pd.read_csv(f'../datastore/current/FPL_data_{game_week}.csv')

        print("\nPredictions on unseen data:")
        predictions = (predict_model(roi_model, data=unseen_data).
                       sort_values('prediction_label', ascending=False))

        predictions = predictions.head(200)


        avg_ppg = predictions['points_per_game'].mean()
        avg_roi = predictions['roi'].mean()
        avg_proi = predictions['prediction_label'].mean()


        #
        predictions = predictions[(predictions['points_per_game'] >= avg_ppg) &
                                  (predictions['roi'] >= avg_roi) &
                                  (predictions['prediction_label'] >= avg_proi)] #Take only top 60 players


        print(predictions.shape[0])
        predicted_players = predictions.to_dict('records')
        print("\nPredicted players: " , predicted_players[-2])


        await session.close()

    except Exception as err:
        "Cant get current data from FPL"








asyncio.run(main())
