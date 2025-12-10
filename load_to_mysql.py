import pandas as pd
import mysql.connector

# 1️⃣ Read the CSV file
df = pd.read_csv("armut_data.csv")

# 2️⃣ Connect to MySQL (Change credentials if needed)
conn = mysql.connector.connect(
    host="localhost",
    user="root",            # your MySQL username
    password="Vardhan@5",  # your MySQL password
    database="service_recommender_dw"  # your new database
)

cursor = conn.cursor()

# 3️⃣ Define the INSERT query
insert_query = """
INSERT INTO service_transactions (user_id, service_id, category_id, create_date)
VALUES (%s, %s, %s, %s)
"""

# 4️⃣ Convert dataframe rows to tuples
data = df[['UserId', 'ServiceId', 'CategoryId', 'CreateDate']].values.tolist()

# 5️⃣ Insert all rows into MySQL
cursor.executemany(insert_query, data)
conn.commit()

print(f"✅ Successfully inserted {cursor.rowcount} rows into MySQL!")

# 6️⃣ Close connection
cursor.close()
conn.close()
