import pandas as pd
import pyarrow
import fastparquet
import datetime as datetime
import numpy as np

# making dataframe
df = pd.read_csv("../seat_Manifest_Fishercats.csv")
manifest_cols = [x.upper() for x in  ['seat_id', 'price_scale_group_description', 'price_scale_code', 'section_code', 'row', 'seat_number',
                 'buyer_type_description', 'buyer_type_group_code', 'buyer_type_group_description']]

# 'season_id', 'ingestion_property', 'ingestion_datetime'

# manifest_cols = ['SEAT_ID', 'PRICE_SCALE_GROUP_DESCRIPTION']

manifest_df = df[manifest_cols]
manifest_df['SEASON_ID'] = 1000
manifest_df['INGESTION_PROPERTY'] = 'milb_fishercats'
manifest_df['INGESTION_DATETIME'] = str(datetime.datetime.now())

manifest_df.columns = map(str.lower, manifest_df.columns)
final_cols = list(manifest_df)
# manifest_df = manifest_df[final_cols].astype(str)


manifest_df = manifest_df.replace(np.nan, None)
manifest_df = manifest_df[final_cols].astype(str)

print(manifest_df['price_scale_group_description'])

manifest_df.to_parquet(
    'seatManifest_FisherCats_2024.parquet'
)


