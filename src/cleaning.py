import pandas as pd
from config import DATABASE_NAME, RAW_COLLECTION_NAME, CLEAN_COLLECTION_NAME, get_database


REQUIRED_COLUMNS = [
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


def clean_energy_data():
    client, db = get_database()
    raw_collection = db[RAW_COLLECTION_NAME]
    clean_collection = db[CLEAN_COLLECTION_NAME]

    try:
        print("Reading raw data from MongoDB...")
        print(f"Database: {DATABASE_NAME}")
        print(f"Raw collection: {RAW_COLLECTION_NAME}")

        raw_count = raw_collection.count_documents({})
        print(f"Raw documents found: {raw_count}")

        if raw_count == 0:
            raise RuntimeError("Raw collection has 0 documents. Run: python src/scraper.py")

        raw_data = list(raw_collection.find({}, {"_id": 0}))
        df = pd.DataFrame(raw_data)
        print(f"Raw dataframe shape: {df.shape}")

        available_columns = [col for col in REQUIRED_COLUMNS if col in df.columns]
        print(f"Available required columns: {len(available_columns)}")
        print(available_columns)

        if "country" not in available_columns or "year" not in available_columns:
            raise RuntimeError("Required fields country/year are missing from raw data.")

        df = df[available_columns].copy()

        # Keep only real country/year rows
        df = df.dropna(subset=["country", "year"])
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["year"])
        df["year"] = df["year"].astype(int)

        # OWID also contains regions/world aggregates. Keeping iso_code helps remove invalid rows.
        if "iso_code" in df.columns:
            df = df[df["iso_code"].notna()]

        # Convert numeric columns safely
        for col in df.columns:
            if col not in ["country", "iso_code"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Replace NaN with None for MongoDB compatibility
        df = df.where(pd.notnull(df), None)
        cleaned_documents = df.to_dict(orient="records")

        print(f"Cleaned documents prepared: {len(cleaned_documents)}")

        clean_collection.delete_many({})

        if not cleaned_documents:
            print("No cleaned documents available to insert.")
            return 0

        result = clean_collection.insert_many(cleaned_documents)
        inserted_count = len(result.inserted_ids)

        print(f"Cleaned data inserted successfully: {inserted_count} records")
        print(f"Database: {DATABASE_NAME}")
        print(f"Clean collection: {CLEAN_COLLECTION_NAME}")
        return inserted_count

    finally:
        client.close()


if __name__ == "__main__":
    clean_energy_data()
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
