# Airflow
from airflow.decorators import dag, task

# Modules
import pendulum
import json
import psycopg2
import requests

# Custom
from transformer import transform_weatherAPI

@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2024, 3, 1, tz="UTC"),
    catchup=False,
    tags=["CustomDAG"],
)

def ETLWeatherPostgresAndPrint():

    # Extract
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
    
    # Load : Save data to Postgres DB
    @task()
    def load(weather_data: dict):

        try:
            connection = psycopg2.connect(
                user="airflow",
                password="airflow",
                host="postgres",
                port="5432",
                database="WeatherData"
            )
            cursor = connection.cursor()

            postgres_insert_query = "INSERT INTO temperature (location, temp_c, wind_kph, time) VALUES ( %s , %s, %s, %s);"
            record_to_insert = (weather_data[0]["location"], weather_data[0]["temp_c"], weather_data[0]["wind_kph"], weather_data[0]["timestamp"])
            cursor.execute(postgres_insert_query, record_to_insert)

            connection.commit()
            count = cursor.rowcount
            print(count, "Record inserted successfully into table")

        except (Exception, psycopg2.Error) as error:
            
            print("Failed to insert record", error)

            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL Connection Closed")

            raise Exception(error)
        
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL Connection Closed")

    @task()
    def query_print(weather_data: dict):
        print(weather_data)

    # Define the main flow
    weather_data = extract()
    weather_summary = transform(weather_data)
    load(weather_summary)
    query_print(weather_summary)

weather_dag_postgres = ETLWeatherPostgresAndPrint()