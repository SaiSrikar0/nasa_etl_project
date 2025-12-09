#import necessary libraries
import json
import glob
import os
import pandas as pd

#Define function to transform NASA data
def transform_nasa_data():
    os.makedirs("../data/staged",exist_ok=True)
    latest_file = sorted(glob.glob("../data/raw/nasa_data.json"))[-1]
    with open(latest_file,"r") as f:
        data=json.load(f)
    df=pd.DataFrame([{
        "date":data['date'],
        "title":data["title"],
        "explanation":data['explanation'],
        "media_type":data['media_type'],
        "image_url":data["url"]
    }])
    output_path = "../data/staged/nasa_data_staged.csv"
    df.to_csv(output_path, index=False)
    print(f"Transformed {len(df)} NASA records saved to {output_path}")
    return df

if __name__=="__main__":
    transform_nasa_data()