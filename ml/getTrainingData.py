import pandas as pd

season = "24_25"  # HardCoded for now
from historical import historical

csv_file_path = f"../historical/_summary/FPL_data_{season}.csv"
csv_file_path_dest = f"../datastore/training/FPL_data_{season}.csv"

form_dict, r = historical.getFormDict(season=season)
print(r)
FDR = historical.get_FDR(form_dict, season=season)
print(FDR)


# Assumed Ipswich will relegate here lol

FDR["Burnley"] = FDR["Ipswich"]
FDR["Sunderland"] = FDR["Leicester"]
FDR["Leeds"] = FDR["Southampton"]


df = pd.read_csv(csv_file_path)
df = df.drop("roi_per_gw", axis=1)
# df = df.drop('name', axis=1)

df["FDR_Average"] = df.apply(lambda x: FDR[x["team"]], axis=1)


df["price"] = df["price"].str.replace("£", "")
df["price"] = df["price"].astype(float)
df.to_csv(csv_file_path_dest, index=False)
print("done")
