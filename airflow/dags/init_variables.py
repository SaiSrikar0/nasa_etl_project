"""
Bootstrap Airflow Variables from .env file.
Run this once after Airflow initializes to populate credentials.

Usage:
  docker compose exec airflow-scheduler python /opt/airflow/dags/init_variables.py
"""

import os
from dotenv import load_dotenv
from airflow.models import Variable

# Load .env from mounted location
env_path = "/opt/airflow/.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"⚠ .env not found at {env_path}, reading from environment...")

# Map of .env keys to Airflow Variable names
VARIABLE_MAP = {
    "api_key": "api_key",
    "supabase_url": "supabase_url",
    "supabase_key": "supabase_key",
}

def init_variables():
    """Read .env and populate Airflow Variables."""
    for env_key, var_name in VARIABLE_MAP.items():
        value = os.getenv(env_key)
        if value:
            Variable.set(var_name, value)
            print(f"✓ Set Variable '{var_name}'")
        else:
            print(f"⚠ Skipped '{var_name}': not found in .env")

if __name__ == "__main__":
    init_variables()
    print("\nVariables initialization complete!")
