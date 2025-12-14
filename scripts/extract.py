#import necessary libraries
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

#set up data directory and path
DATA_DIR = Path(__file__).resolve().parents[1]/"data"/"raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()
nasa_key = os.getenv("api_key") or os.getenv("NASA_API_KEY")

#define function to extract weather data
def extract_nasa_data(api_key=nasa_key):
    if not api_key:
        raise ValueError("NASA API key is missing. Set env var 'api_key' or 'NASA_API_KEY'.")

    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": api_key}

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    filename = DATA_DIR/f"nasa_data.json"
    filename.write_text(json.dumps(data, indent = 2))

    print(f"Nasa data saved to {filename}")
    return data

if __name__ == "__main__":
    extract_nasa_data()