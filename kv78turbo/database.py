import psycopg2
from settings.const import kv78_database_connect

def connect():
    conn = psycopg2.connect(kv78_database_connect)
    return conn.cursor()
