import pandas as pd
import sqlite3
import os 


db_path = 'adventureworks.db'

# Connect to SQLite database (or create it)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the list of all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"Total number of tables present in DB: {len(tables)}")

# Iterate over each table and get the row count
for table in tables:
    table_name = str(table[0])
    query = "SELECT COUNT(*) FROM " + table_name + ";"
    cursor.execute(query)
    row_count = cursor.fetchone()
    print(f"Table: {table_name}, Row count: {row_count}")

# Close the connection
conn.close()

