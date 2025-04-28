import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import io

API_ENDPOINT = "https://data.cityofnewyork.us/resource/h9gi-nx95.csv"
SAVE_DIR = Path("../../data/raw/")
CHUNK_SIZE = 50000


def download_all_collisions():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.today().strftime("%Y-%m-%d")
    save_path = SAVE_DIR / f"collisions_full_{today}.csv"

    all_chunks = []
    offset = 0

    while True:
        params = {
            "$limit": CHUNK_SIZE,
            "$offset": offset
        }
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()

        chunk = pd.read_csv(io.StringIO(response.text))
        if chunk.empty:
            break

        all_chunks.append(chunk)
        offset += CHUNK_SIZE
        print(f"Downloaded {offset} rows...")

    full_data = pd.concat(all_chunks, ignore_index=True)
    full_data.to_csv(save_path, index=False)
    print(f"Saved full collision dataset: {save_path}")


if __name__ == "__main__":
    download_all_collisions()
