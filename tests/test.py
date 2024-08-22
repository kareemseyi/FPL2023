from popcorn import utils
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    GetMetadataRequest
)
import json
import os
import pandas as pd

secret_json = utils.get_secret_value("mp_oseg_cfl_redblacks_google_analytics_ingestion_credentials")
# secret_json = utils.get_secret_value("mp_bse_nba_nets_google_analytics_ingestion_credentials")

property_ids = (
            secret_json["property_id"].replace(" ", "").split(",")
            if "," in secret_json["property_id"]
            else [secret_json["property_id"]]
        )

print(f'Property IDs: {property_ids}')

property_id = property_ids[0]
# account_key = json.loads(json.dumps(account_key))
account_key = json.loads(secret_json['account_key'])

with open('account_key.json', 'w') as f:
    json.dump(account_key, f)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "account_key.json"

GA_CUSTOM_USER_ID = "said"

client = BetaAnalyticsDataClient()
request = GetMetadataRequest(
    name=f"properties/{property_id}/metadata",
)

WEB_ACTIVITIES_DIMENSION = [
    'dateHour',
    'hostName',
    'pagePath',
    'pageReferrer',
    'newVsReturning',
    'country',
    'region' ,
    'customEvent:client_id',
    'customEvent:sa_id'
    ]
USER_MAPPING_DIMENSION = [
    'dateHour',
    'pagePath',
    'newVsReturning',
    'country',
    'region',
    'city',
    'customUser:client_id',
    f'customUser:{GA_CUSTOM_USER_ID}'
    ]
METRICS = ['sessions', 'screenPageViews']

request = RunReportRequest(
            property=f"properties/{property_id}",
            # property=f"properties/372697247",
            # max 9 dimensions per report
            dimensions=[Dimension(name=d) for d in WEB_ACTIVITIES_DIMENSION],
            metrics=[Metric(name=m) for m in METRICS],
            # date_ranges=[DateRange(start_date='yesterday', end_date='today')],
            date_ranges=[DateRange(start_date='2024-06-01', end_date='2024-06-19')],
            limit=100000,
            offset=0,  # use for pagination
        )

response = client.run_report(request)

df_values = []
for row in response.rows:
    values = [value.value for value in row.dimension_values]
    values.extend([value.value for value in row.metric_values])
    df_values.append(values)

df = pd.DataFrame(df_values, columns=WEB_ACTIVITIES_DIMENSION + METRICS)
print(df.head())

# web_activities
column_mapping = {
            "dateHour": "date_hour",
            "hostName": "host_name",
            "pagePath": "page_path",
            "pageReferrer": "full_referrer",
            "newVsReturning": "user_type",
            "country": "country",
            "region": "region",
            "customEvent:client_id": "ga_cookie_id",
            "customEvent:name": "name",
            "sessions": "sessions",
            "screenPageViews": "page_views"
        }

df.rename(columns=column_mapping, inplace=True)

print(df.head())

