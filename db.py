import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("database_url"))
cursor = conn.cursor()

def execute(sql, values=None, commit=False):
    cursor.execute(sql, values or ())
    if commit:
        conn.commit()

def fetchall(sql, values=None):
    cursor.execute(sql, values or ())
    return cursor.fetchall()
