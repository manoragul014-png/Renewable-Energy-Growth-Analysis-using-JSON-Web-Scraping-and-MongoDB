import pandas as pd
import numpy as np
from config import get_database, DATABASE_NAME, RAW_COLLECTION_NAME, CLEAN_COLLECTION_NAME


def clean_energy_data():
    """
    Reads raw energy data from MongoDB, cleans it,
    and inserts cleaned records into a new MongoDB collection.
    """

    client, db = get_database()

    raw_collection = db[RAW_COLLECTION_NAME]
    clean_collection = db[CLEAN_COLLECTION_NAME]

    print("Reading raw data from MongoDB...")
    print(f"Database: {DATABASE_NAME}")
    print(f"Raw collection: {RAW_COLLECTION_NAME}")

    raw_data = list(raw_collection.find({}, {"_id": 0}))

    print(f"Raw documents found: {len(raw_data)}")

    if len(raw_data) == 0:
        print("No raw data found. Run scraper.py first.")
        client.close()
        return 0

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
        "solar_electricity",
        "wind_electricity",
        "fossil_electricity",
        "coal_electricity",
        "gas_electricity",
        "oil_electricity",
        "low_carbon_electricity",
    ]

    available_columns = [col for col in required_columns if col in df.columns]

    print(f"Available required columns: {len(available_columns)}")
    print(available_columns)

    if len(available_columns) == 0:
        print("No required columns found. Check scraper output.")
        client.close()
        return 0

    df = df[available_columns]

    # Keep only records with country and year
    df = df.dropna(subset=["country", "year"])

    # Convert year safely
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    # Remove records without iso_code if iso_code exists
    if "iso_code" in df.columns:
        df = df[df["iso_code"].notna()]

    # Calculate share columns if possible
    if (
        "renewables_share_electricity" not in df.columns
        and "renewables_electricity" in df.columns
        and "electricity_generation" in df.columns
    ):
        df["renewables_share_electricity"] = (
            df["renewables_electricity"] / df["electricity_generation"] * 100
        )

    if (
        "fossil_share_electricity" not in df.columns
        and "fossil_electricity" in df.columns
        and "electricity_generation" in df.columns
    ):
        df["fossil_share_electricity"] = (
            df["fossil_electricity"] / df["electricity_generation"] * 100
        )

    if (
        "low_carbon_share_electricity" not in df.columns
        and "low_carbon_electricity" in df.columns
        and "electricity_generation" in df.columns
    ):
        df["low_carbon_share_electricity"] = (
            df["low_carbon_electricity"] / df["electricity_generation"] * 100
        )

    # Replace invalid infinity values
    df = df.replace([float("inf"), float("-inf")], None)

    # Replace  with NaN for MongoDB
    df = df.replace({np.nan: None})

    cleaned_documents = df.to_dict(orient="records")

    print(f"Cleaned documents prepared: {len(cleaned_documents)}")

    clean_collection.delete_many({})

    if not cleaned_documents:
        print("No cleaned documents available to insert.")
        client.close()
        return 0

    result = clean_collection.insert_many(cleaned_documents)

    print(f"Cleaned data inserted successfully: {len(result.inserted_ids)} records")
    print(f"Database: {DATABASE_NAME}")
    print(f"Clean collection: {CLEAN_COLLECTION_NAME}")

    client.close()
    return len(result.inserted_ids)


if __name__ == "__main__":
    clean_energy_data()
