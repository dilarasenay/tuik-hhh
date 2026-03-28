from sqlalchemy import create_engine
import pandas as pd
from config.config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_TABLE,
)

def get_engine():
    return create_engine(
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

def load_data():
    engine = get_engine()
    query = f"SELECT * FROM {MYSQL_TABLE}"
    return pd.read_sql(query, engine)