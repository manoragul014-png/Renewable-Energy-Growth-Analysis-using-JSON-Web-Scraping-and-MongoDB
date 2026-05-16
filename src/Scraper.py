import requests
from config import get_database, RAW_COLLECTION_NAME


def scrape_owid_energy_json():
    """
    Scrapes energy data from Our World in Data JSON source
    and inserts raw records into MongoDB.
    """

    client, db = get_database()
    raw_collection = db[RAW_COLLECTION_NAME]

    url = "https://owid-public.owid.io/data/energy/owid-energy-data.json"

    print("Scraping data from OWID energy JSON...")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()

    raw_documents = []

    for country_key, country_info in data.items():
        country_name = country_info.get("country") or country_key
        iso_code = country_info.get("iso_code") or country_key
        yearly_records = country_info.get("data", [])

        for record in yearly_records:
            doc = dict(record)
            doc["country"] = country_name
            doc["iso_code"] = iso_code
            raw_documents.append(doc)

    print(f"Raw records prepared: {len(raw_documents)}")

    if len(raw_documents) == 0:
        print("No records found. Nothing inserted.")
        client.close()
        return

    raw_collection.delete_many({})

    result = raw_collection.insert_many(raw_documents)

    print(f"Raw data inserted successfully: {len(result.inserted_ids)} records")
    print("Database: renewable_energy_growth_db")
    print(f"Collection: {RAW_COLLECTION_NAME}")

    client.close()


if __name__ == "__main__":
    scrape_owid_energy_json()
