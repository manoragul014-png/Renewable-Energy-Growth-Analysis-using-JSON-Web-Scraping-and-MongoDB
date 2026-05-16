import os
import certifi
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")

client = MongoClient(
    MONGO_URI,
    server_api=ServerApi("1"),
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["energy_project"]

# This should match the collection where scraper.py inserted data
raw_collection = db["owid_energy_data"]

# Cleaned output collection
cleaned_collection = db["owid_energy_cleaned"]


def clean_energy_data():
    print("Reading raw data from MongoDB...")

    raw_data = list(raw_collection.find({}, {"_id": 0}))

    print(f"Raw documents found: {len(raw_data)}")

    if len(raw_data) == 0:
        raise Exception(
            "No raw data found. Check whether scraper.py inserted data into 'owid_energy_data'."
        )

    df = pd.DataFrame(raw_data)

    print(f"Raw dataframe shape: {df.shape}")

    # Keep only useful columns that exist in your dataset
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

    df = df[available_columns]

    print(f"Selected columns: {len(available_columns)}")
    print(available_columns)

    # Remove rows without country/year
    df = df.dropna(subset=["country", "year"])

    # Convert year to integer
    df["year"] = df["year"].astype(int)

    # Optional: remove aggregate regions if you only want countries
    if "iso_code" in df.columns:
        df = df[df["iso_code"].notna()]

    # Replace NaN with None for MongoDB
    df = df.where(pd.notnull(df), None)

    cleaned_documents = df.to_dict(orient="records")

    print(f"Cleaned documents prepared: {len(cleaned_documents)}")

    cleaned_collection.delete_many({})

    if cleaned_documents:
        cleaned_collection.insert_many(cleaned_documents)

    print("Cleaned data inserted successfully into MongoDB.")
    print("Collection name: owid_energy_cleaned")


if __name__ == "__main__":
    clean_energy_data()