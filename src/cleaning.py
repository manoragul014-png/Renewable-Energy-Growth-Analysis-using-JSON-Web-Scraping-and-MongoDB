import os
import certifi
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = "energy_project_db_New"

# Possible raw collection names
POSSIBLE_RAW_COLLECTIONS = [
    "raw_energy_json_new",
    "owid_energy_data"
]

CLEAN_COLLECTION_NAME = "renewable_energy_new"


if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")


client = MongoClient(
    MONGO_URI,
    server_api=ServerApi("1"),
    tls=True,
    tlsCAFile=certifi.where()
)

db = client[DATABASE_NAME]
cleaned_collection = db[CLEAN_COLLECTION_NAME]


def find_raw_collection_with_data():
    print("\nAvailable databases:")
    print(client.list_database_names())

    print(f"\nAvailable collections in database '{DATABASE_NAME}':")
    print(db.list_collection_names())

    for collection_name in POSSIBLE_RAW_COLLECTIONS:
        collection = db[collection_name]
        count = collection.count_documents({})
        print(f"Documents in {collection_name}: {count}")

        if count > 0:
            print(f"\nUsing raw collection: {collection_name}")
            return collection

    raise Exception(
        "No raw data found in any expected raw collection. "
        "Please check which database and collection your scraper inserted into."
    )


def clean_energy_data():
    print("Reading raw data from MongoDB...")
    print(f"Database: {DATABASE_NAME}")

    raw_collection = find_raw_collection_with_data()

    raw_data = list(raw_collection.find({}, {"_id": 0}))

    print(f"\nRaw documents found: {len(raw_data)}")

    if len(raw_data) == 0:
        raise Exception("Raw collection exists, but it has 0 documents.")

    df = pd.DataFrame(raw_data)

    print(f"Raw dataframe shape: {df.shape}")

    required_columns = [
        "country",
        "year",
        "iso_code",
        "population",
        "gdp",

        "primary_energy_consumption",
        "fossil_fuel_consumption",
        "renewables_consumption",
        "solar_consumption",
        "wind_consumption",
        "hydro_consumption",
        "biofuel_consumption",
        "low_carbon_consumption",

        "coal_consumption",
        "gas_consumption",
        "oil_consumption",

        "energy_per_capita",
        "electricity_generation",
        "electricity_demand",

        "renewables_electricity",
        "renewables_share_electricity",
        "solar_electricity",
        "wind_electricity",
        "fossil_share_electricity",
        "fossil_electricity",
        "coal_electricity",
        "gas_electricity",
        "oil_electricity",
        "low_carbon_electricity",
        "low_carbon_share_electricity",
    ]

    available_columns = [col for col in required_columns if col in df.columns]

    print(f"\nAvailable required columns: {len(available_columns)}")
    print(available_columns)

    if len(available_columns) == 0:
        raise Exception(
            "None of the required columns were found. "
            "Check whether the scraper inserted the expected OWID energy data."
        )

    df = df[available_columns]

    df = df.dropna(subset=["country", "year"])

    df["year"] = df["year"].astype(int)

    if "iso_code" in df.columns:
        df = df[df["iso_code"].notna()]

    df = df.where(pd.notnull(df), None)

    cleaned_documents = df.to_dict(orient="records")

    print(f"\nCleaned documents prepared: {len(cleaned_documents)}")

    cleaned_collection.delete_many({})

    if cleaned_documents:
        cleaned_collection.insert_many(cleaned_documents)

        print("\nCleaned data inserted successfully into MongoDB.")
        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {CLEAN_COLLECTION_NAME}")
    else:
        print("No cleaned documents available to insert.")

    client.close()


if __name__ == "__main__":
    clean_energy_data()
