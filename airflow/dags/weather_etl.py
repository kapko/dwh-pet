from datetime import datetime
import os
import requests
import json

import psycopg2

from airflow import DAG
from airflow.operators.python import PythonOperator

def get_data():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 55.75,
        "longitude": 37.62,
        "hourly": "temperature_2m,relative_humidity_2m",
        "past_days": 7
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code}")

    data = response.json()

    if "error" in data:
        raise Exception(f"API returned error: {data.get('reason')}")

    print("=== Response Status ===")
    print(f"Status code: {response.status_code}")

    print("\n=== Data Structure ===")
    print(f"Keys: {data.keys()}")

    print("\n=== Full Response (formatted) ===")
    print(json.dumps(data, indent=2))

    return data


def load_to_bronze(**context):
    # 1. Получи данные из предыдущего таска
    data = context['ti'].xcom_pull(task_ids='get_data')

    if 'error' in data:
        raise Exception(f"Bad data: {data.get('reason')}")

    # 2. Подключись к PostgreSQL (psycopg2)
    conn = psycopg2.connect(
        host=os.getenv('DWH_HOST', 'dwh-postgres'),
        port=os.getenv('DWH_PORT', '5432'),
        user=os.getenv('DWH_USER', 'dwh'),
        password=os.getenv('DWH_PASSWORD', 'dwh'),
        database=os.getenv('DWH_DB', 'dwh')
    )
    cursor = conn.cursor()

    # 3. Выполни INSERT в bronze.raw_weather
    cursor.execute(
        "INSERT INTO bronze.raw_weather (raw_data) VALUES (%s)",
        (json.dumps(data),)
    )
    conn.commit()

    print(f"Successfully inserted weather data into bronze.raw_weather")

    # 4. Закрой соединение
    cursor.close()
    conn.close()



with DAG(
    dag_id='weather_etl',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['example'],
) as dag:


    load_task = PythonOperator(
        task_id='get_data',
        python_callable=get_data,
    )

    write_task = PythonOperator(
        task_id='load_to_bronze',
        python_callable=load_to_bronze,
    )

    load_task >> write_task
