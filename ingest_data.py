import pandas as pd
import sqlite3
import os 


db_path = 'adventureworks.db'

# Check if the database file exists and delete it if it does
if os.path.exists(db_path):
    print(f"Database '{db_path}' exists.")
    os.remove(db_path)
    print(f"Database '{db_path}' deleted.")

# Connect to SQLite database (or create it)
conn = sqlite3.connect('adventureworks.db')

# Specify the directory path
directory_path = 'Data'

# List all files in the directory
files = os.listdir(directory_path)

# Print the list of files
for file in files:
    table_name = file[:-4]

    temp_df = pd.read_csv("Data\\" + file)
    temp_df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    
print("Successfully imported all the CSVs into the DB")
    

# Commit the changes and close the connection
conn.commit()
conn.close()
