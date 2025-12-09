#import necessary libraries
import json
from pathlib import Path
import requests

#set up data directory and path
DATA_DIR = Path(__file__).resolve().parents[1]/"data"/"raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

nasa_key = "KgWTxDEy8pBqdKKcemZlHP1CJ2DzUnCqQCllB2eU"

#define function to extract weather data
def extract_nasa_data(api_key = nasa_key):
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    params = {
        "api_key": api_key
    }

    response = requests.get(url, params = params)
    response.raise_for_status()
    data = response.json()

    filename = DATA_DIR/f"nasa_data.json"
    filename.write_text(json.dumps(data, indent = 2))

    print(f"Nasa data saved to {filename}")
    return data

if __name__ == "__main__":
    extract_nasa_data()