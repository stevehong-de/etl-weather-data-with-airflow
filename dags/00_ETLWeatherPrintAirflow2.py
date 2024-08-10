# Airflow
from airflow import DAG
from airflow.operators.python import PythonOperator

# Modules
import requests
import json
import datetime as dt
import logging

# Custom
from transformer import transform_weatherAPI

def my_extract(**kwargs):

    # Fetch data from API
    payload = {"Key": "SECRET_KEY", "q": "Seoul", "aqi": "no"}

    # Get json
    r = requests.get("http://api.weatherapi.com/v1/current.json", params=payload)
    r_string = r.json()

    # Dump json result into string
    ex_string = json.dumps(r_string)

    # Push it into xcom variable "api_result"
    task_instance = kwargs["ti"]
    task_instance.xcom_push(key="api_result", value=ex_string)

    return ex_string

def my_transform(**kwargs):

    # Get data from xcom
    task_instance = kwargs["ti"]
    api_data = task_instance.xcom_pull(key="api_result", task_ids="extract")
    
    # Transform
    ex_json = transform_weatherAPI(api_data)

    # Push to xcom
    task_instance.xcom_push(key="transformed_weather", value=ex_json)

def my_load(**kwargs):

    # Get data from xcom
    task_instance = kwargs["ti"]
    weather_json = task_instance.xcom_pull(key="transformed_weather", task_ids="transform")

    # Write into the log
    logger = logging.getLogger("airflow.task")
    logger.info(weather_json)

# Make DAG
with DAG("ETLWeatherPrintAirflow2", description="Airflow2.0 DAG", start_date=dt.datetime(2024, 3, 1), schedule_interval="0 * * * *", catchup=False, tags=["CustomDAG"]) as dag:
    extract = PythonOperator(
        task_id="extract",
        python_callable=my_extract,
        provide_context=True
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=my_transform,
        provide_context=True
    )

    load = PythonOperator(
        task_id="load",
        python_callable=my_load,
        provide_context=True
    )

    extract >> transform >> load