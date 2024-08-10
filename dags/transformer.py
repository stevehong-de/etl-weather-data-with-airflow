import json
from pandas import DataFrame, json_normalize
import datetime as dt

def transform_weatherAPI(im_json : str):
    
    print(im_json)

    # Load string into json object
    api_json = json.loads(im_json)

    # Normalize
    normalized = json_normalize(api_json)

    # Create timestamp
    normalized["timestamp"] = normalized["location.localtime_epoch"].apply(lambda s : dt.datetime.fromtimestamp(s).strftime("%Y-%m-%dT%H:%M:%S+09:00"))

    # Rename columns
    normalized.rename(columns={
        "location.name": "location",
        "location.region": "region",
        "current.temp_c": "temp_c",
        "current.wind_kph": "wind_kph"
    }, inplace=True)

    # Filter out only we need
    ex_df = normalized.filter(["location", "temp_c", "wind_kph", "timestamp"])

    # To json
    ex_json = DataFrame.to_json(ex_df, orient="records")

    return ex_json