import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"

load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

# One clear database name for the full project
DATABASE_NAME = "renewable_energy_growth_db"

# One collection for raw scraped data and one collection for cleaned data
RAW_COLLECTION_NAME = "raw_energy_data"
CLEAN_COLLECTION_NAME = "clean_energy_data"

OWID_ENERGY_JSON_URL = "https://owid-public.owid.io/data/energy/owid-energy-data.json"


def get_client() -> MongoClient:
    if not MONGO_URI:
        raise ValueError("MONGO_URI not found. Create a .env file in the project root.")

    return MongoClient(
        MONGO_URI,
        server_api=ServerApi("1"),
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=30000,
    )


def get_database():
    client = get_client()
    return client, client[DATABASE_NAME]
