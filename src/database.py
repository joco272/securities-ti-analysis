import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import psycopg2
from config.settings import (
    INFLUXDB_URL,
    INFLUXDB_TOKEN,
    INFLUXDB_ORG,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
)

def get_influxdb_client():
    """Returns an InfluxDB client."""
    return InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

def get_postgres_connection():
    """Returns a PostgreSQL connection."""
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
    )

if __name__ == '__main__':
    # Example usage
    try:
        # Test InfluxDB connection
        influx_client = get_influxdb_client()
        health = influx_client.health()
        if health.status == "pass":
            print("InfluxDB connection successful.")
        else:
            print(f"InfluxDB connection failed. Status: {health.status}")

    except Exception as e:
        print(f"An error occurred while connecting to InfluxDB: {e}")

    try:
        # Test PostgreSQL connection
        pg_conn = get_postgres_connection()
        print("PostgreSQL connection successful.")
        pg_conn.close()

    except Exception as e:
        print(f"An error occurred while connecting to PostgreSQL: {e}")
