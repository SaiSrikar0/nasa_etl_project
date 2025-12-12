#import necessary libraries
import os
import time
import pandas as pd
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

#initialize supabase
load_dotenv()
supabase = create_client(os.getenv("supabase_url"), os.getenv("supabase_key"))

#function to load weather data into supabase
def load_to_supabase():

    #load cleaned csv
    csv_path = Path(__file__).resolve().parents[1] / "data" / "staged" / "nasa_data_staged.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} does not exist.")
    
    df = pd.read_csv(csv_path)  

    #convert timestamps to strings
    df["date"] = pd.to_datetime(df["date"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    batch_size = 20
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i + batch_size]
        batch = batch_df.where(pd.notnull(batch_df), None).to_dict("records")
        
        # Build SQL values without f-strings to avoid backslash issues
        values = []
        for r in batch:
            date_val = r['date']
            title_val = r['title'].replace("'", "''")
            explanation_val = r['explanation'].replace("'", "''")
            media_type_val = r['media_type']
            image_url_val = r.get('image_url', '')
            values.append(f"('{date_val}', '{title_val}', '{explanation_val}', '{media_type_val}', '{image_url_val}')")
        
        insert_sql = f"""
        INSERT INTO nasa_apod (date, title, explanation, media_type, image_url) VALUES {', '.join(values)};
        """

        # REMOTE PROCEDURE CALL = to run SQL code inside the database from the python Script
        supabase.rpc("execute_sql", {"query": insert_sql}).execute()
        print(f"Inserted rows {i+1} to {min(i + batch_size, len(df))}")
        time.sleep(0.5)

    print("Data loading complete.")

if __name__ == "__main__":
    load_to_supabase()