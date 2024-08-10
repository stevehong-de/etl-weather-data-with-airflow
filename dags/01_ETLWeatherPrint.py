# Airflow
from airflow.decorators import dag, task

# Modules
import pendulum
import json
import requests

# Custom
from transformer import transform_weatherAPI

@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2024, 3, 1, tz="UTC"),
    catchup=False,
    tags=["CustomDAG"],
)

def ETLWeatherPrint():

    # Extract with TaskFlow
    @task()
    def extract():
        # Fetch data from API
        payload = {"Key": "SECRET_KEY", "q": "Seoul", "aqi": "no"}

        # Get json
        r = requests.get("http://api.weatherapi.com/v1/current.json", params=payload)
        r_string = r.json()

        return r_string
    
    # Transform with TaskFlow
    @task()
    def transform(weather_json: json):

        weather_str = json.dumps(weather_json)
        transformed_str = transform_weatherAPI(weather_str)

        # str to dict
        ex_dict = json.loads(transformed_str)

        return ex_dict
    
    # Load with TaskFlow
    @task()
    def load(ex_dict: dict):
        
        print(ex_dict)

    # Define the main flow
    weather_data = extract()
    weather_summary = transform(weather_data)
    load(weather_summary)

# Start DAG
weather_dag = ETLWeatherPrint()