from sqlalchemy.orm import sessionmaker
from utils.logger import logging,logger
import pandas as pd
from sqlalchemy.sql import text

def read_data(connection, query):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

        return pd.DataFrame(data, columns=columns)
    
    except Exception as e:
        logging()
        return