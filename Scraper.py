import os
import certifi
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = "energy_project"
RAW_COLLECTION_NAME = "owid_energy_data"

SOURCE_PAGE_URL = "https://github.com/owid/energy-data"

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")


client = MongoClient(
    MONGO_URI,
    server_api=ServerApi("1"),
    tls=True,
    tlsCAFile=certifi.where()
)

db = client[DATABASE_NAME]
collection = db[RAW_COLLECTION_NAME]


def scrape_dataset_link():
    print("Scraping OWID energy data webpage...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(SOURCE_PAGE_URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    csv_url = None

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if href.endswith("owid-energy-data.csv"):
            csv_url = "https://raw.githubusercontent.com" + href.replace("/blob/", "/")
            break

    if not csv_url:
        raise Exception("Could not find OWID energy CSV link from the webpage.")

    print(f"Dataset link found: {csv_url}")
    return csv_url


def scrape_owid_energy_data():
    csv_url = scrape_dataset_link()

    print("Downloading dataset from scraped link...")

    df = pd.read_csv(csv_url)

    print(f"Rows downloaded: {len(df)}")
    print(f"Columns downloaded: {len(df.columns)}")

    df = df.where(pd.notnull(df), None)

    records = df.to_dict(orient="records")

    collection.delete_many({})

    if records:
        collection.insert_many(records)
        print(f"Inserted {len(records)} raw records into MongoDB.")
        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {RAW_COLLECTION_NAME}")
    else:
        print("No records found to insert.")

    client.close()


if __name__ == "__main__":
    scrape_owid_energy_data()