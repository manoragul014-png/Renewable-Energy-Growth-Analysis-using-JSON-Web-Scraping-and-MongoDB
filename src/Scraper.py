import os
import certifi
import requests
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# Get project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = "energy_project_db_New"
RAW_COLLECTION_NAME = "raw_energy_json_new"

OWID_ENERGY_JSON_URL = "https://owid-public.owid.io/data/energy/owid-energy-data.json"


if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")


client = MongoClient(
    MONGO_URI,
    server_api=ServerApi("1"),
    tls=True,
    tlsCAFile=certifi.where()
)

db = client[DATABASE_NAME]
raw_collection = db[RAW_COLLECTION_NAME]


def scrape_owid_energy_json():
    print("Downloading OWID energy JSON data...")

    response = requests.get(OWID_ENERGY_JSON_URL, timeout=60)
    response.raise_for_status()

    data = response.json()

    print("JSON data downloaded successfully.")
    print(f"Countries/regions found: {len(data)}")

    raw_documents = []

    for country_code, country_info in data.items():
        country_name = country_info.get("country")
        country_data = country_info.get("data", [])

        for record in country_data:
            record["country"] = country_name
            record["iso_code"] = country_code
            raw_documents.append(record)

    print(f"Raw records prepared: {len(raw_documents)}")

    raw_collection.delete_many({})

    if raw_documents:
        raw_collection.insert_many(raw_documents)
        print("Raw data inserted successfully into MongoDB.")
        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {RAW_COLLECTION_NAME}")
    else:
        print("No records found to insert.")

    client.close()


if __name__ == "__main__":
    scrape_owid_energy_json()
