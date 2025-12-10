import mysql.connector
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vardhan@5",  # change this
        database="service_recommender_dw"
    )

def load_transactions():
    conn = get_connection()
    query = "SELECT user_id, service_id, category_id, create_date FROM service_transactions"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
