import requests
from bs4 import BeautifulSoup
from config import get_database, RAW_COLLECTION_NAME


def find_energy_json_url():
    """
    Uses BeautifulSoup to parse the Our World in Data energy page.
    """

    page_url = "https://ourworldindata.org/energy"

    print("Opening Our World in Data energy page...")
    response = requests.get(page_url, timeout=60)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    print("Parsing page using BeautifulSoup...")

    json_url = None

    # Search all links on the page
    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "owid-energy-data.json" in href:
            if href.startswith("http"):
                json_url = href
            else:
                json_url = "https://ourworldindata.org" + href
            break

    # OWID website
    if json_url is None:
        print("JSON link not found directly in page. Using known OWID JSON data URL.")
        json_url = "https://owid-public.owid.io/data/energy/owid-energy-data.json"

    print(f"JSON data source found: {json_url}")
    return json_url


def scrape_owid_energy_json():
    """
    Scrapes renewable energy data from Our World in Data.
    """

    client, db = get_database()
    raw_collection = db[RAW_COLLECTION_NAME]

    try:
        json_url = find_energy_json_url()

        print("Fetching JSON energy data...")
        response = requests.get(json_url, timeout=60)
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
            return

        print("Clearing existing raw collection...")
        raw_collection.delete_many({})

        print("Inserting raw records into MongoDB...")
        result = raw_collection.insert_many(raw_documents)

        print(f"Raw data inserted successfully: {len(result.inserted_ids)} records")
        print("Database: renewable_energy_growth_db")
        print(f"Collection: {RAW_COLLECTION_NAME}")

    except requests.exceptions.RequestException as e:
        print("Error while requesting data from the web:")
        print(e)

    except Exception as e:
        print("Unexpected error occurred:")
        print(e)

    finally:
        client.close()
        print("MongoDB connection closed.")


if __name__ == "__main__":
    scrape_owid_energy_json()
