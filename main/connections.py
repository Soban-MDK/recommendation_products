from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
from utils.logger import logger, logging
import numpy as np

load_dotenv()

DB_POS_HOST = os.getenv("DB_HOST")
DB_POS_PORT = os.getenv("DB_PORT")
DB_POS_NAME = os.getenv("DB_DATABASE")
DB_POS_USER = os.getenv("DB_USERNAME")
DB_POS_PASS = os.getenv("DB_PASSWORD")

# DB_WMS_HOST = os.getenv("DB_WMS_HOST")
# DB_WMS_PORT = os.getenv("DB_WMS_PORT")
# DB_WMS_NAME = os.getenv("DB_WMS_DATABASE")
# DB_WMS_USER = os.getenv("DB_WMS_USERNAME")
# DB_WMS_PASS = os.getenv("DB_WMS_PASSWORD")

def connection_pos():
    HOST = DB_POS_HOST
    DB_NAME = DB_POS_NAME
    USER = DB_POS_USER
    PASSWORD = DB_POS_PASS
    PORT = DB_POS_PORT


    conn = psycopg2.connect(
        host=HOST,
        database=DB_NAME,
        user=USER,
        password=PASSWORD,
        port=PORT)
    
    return conn


def conn_string_pos():
    return f"postgresql://{DB_POS_USER}:{DB_POS_PASS}@{DB_POS_HOST}/{DB_POS_NAME}"
