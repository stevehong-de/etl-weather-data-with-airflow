# Airflow
from airflow.decorators import dag, task
from airflow.providers.http.operators.http import SimpleHttpOperator

# Modules
import json
import pendulum

# Custom
from transformer import transform_weatherAPI

@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2024, 3, 1, tz="UTC"),
    catchup=False,
    tags=["CustomDAG"],
)

def SimpleHttpTest():

    # Extract
    extract_task = SimpleHttpOperator(
        task_id="extract_data",
        http_conn_id="WeatherAPI",
        method="GET",
        endpoint="/v1/current.json",
        data={"Key": "SECRET_KEY", "q": "Seoul", "aqi": "no"},
        response_filter=lambda response: response.json(),
    )

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
    weather_data = extract_task.output
    weather_summary = transform(weather_data)
    load(weather_summary)

# Start DAG
weather_dag = SimpleHttpTest()