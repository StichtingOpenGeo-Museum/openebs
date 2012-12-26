import psycopg2
from settings.const import kv15_database_connect

def connect():
    conn = psycopg2.connect(kv15_database_connect)
    return conn.cursor()
