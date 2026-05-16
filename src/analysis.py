import os
import certifi
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# Get project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

# Updated database and cleaned collection names
DATABASE_NAME = "energy_project_db_New"
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
collection = db[CLEAN_COLLECTION_NAME]


def print_results(title, results):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)

    if not results:
        print("No results found.")
        return

    for item in results:
        print(item)


def get_latest_year():
    result = collection.find_one(sort=[("year", -1)])
    return result["year"] if result else None


def top_countries_by_renewable_electricity(year):
    pipeline = [
        {
            "$match": {
                "year": year,
                "renewables_electricity": {"$gt": 0}
            }
        },
        {"$sort": {"renewables_electricity": -1}},
        {"$limit": 10},
        {
            "$project": {
                "_id": 0,
                "country": 1,
                "year": 1,
                "renewables_electricity": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by renewable electricity generation in {year}", results)


def top_countries_by_renewable_share(year):
    pipeline = [
        {
            "$match": {
                "year": year,
                "electricity_generation": {"$gt": 50},
                "renewables_share_electricity": {"$gt": 0}
            }
        },
        {"$sort": {"renewables_share_electricity": -1}},
        {"$limit": 10},
        {
            "$project": {
                "_id": 0,
                "country": 1,
                "year": 1,
                "renewables_share_electricity": 1,
                "electricity_generation": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by renewable electricity share in {year}", results)


def top_solar_growth_countries(start_year, end_year):
    pipeline = [
        {
            "$match": {
                "year": {"$in": [start_year, end_year]},
                "solar_electricity": {"$gte": 0}
            }
        },
        {
            "$group": {
                "_id": "$country",
                "records": {
                    "$push": {
                        "year": "$year",
                        "solar_electricity": "$solar_electricity"
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "country": "$_id",
                "start_value": {
                    "$first": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$records",
                                    "as": "record",
                                    "cond": {"$eq": ["$$record.year", start_year]}
                                }
                            },
                            "as": "r",
                            "in": "$$r.solar_electricity"
                        }
                    }
                },
                "end_value": {
                    "$first": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$records",
                                    "as": "record",
                                    "cond": {"$eq": ["$$record.year", end_year]}
                                }
                            },
                            "as": "r",
                            "in": "$$r.solar_electricity"
                        }
                    }
                }
            }
        },
        {
            "$match": {
                "start_value": {"$ne": None},
                "end_value": {"$ne": None}
            }
        },
        {
            "$project": {
                "country": 1,
                "start_value": 1,
                "end_value": 1,
                "solar_growth": {"$subtract": ["$end_value", "$start_value"]}
            }
        },
        {"$sort": {"solar_growth": -1}},
        {"$limit": 10}
    ]

    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by solar electricity growth from {start_year} to {end_year}", results)


def top_wind_growth_countries(start_year, end_year):
    pipeline = [
        {
            "$match": {
                "year": {"$in": [start_year, end_year]},
                "wind_electricity": {"$gte": 0}
            }
        },
        {
            "$group": {
                "_id": "$country",
                "records": {
                    "$push": {
                        "year": "$year",
                        "wind_electricity": "$wind_electricity"
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "country": "$_id",
                "start_value": {
                    "$first": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$records",
                                    "as": "record",
                                    "cond": {"$eq": ["$$record.year", start_year]}
                                }
                            },
                            "as": "r",
                            "in": "$$r.wind_electricity"
                        }
                    }
                },
                "end_value": {
                    "$first": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$records",
                                    "as": "record",
                                    "cond": {"$eq": ["$$record.year", end_year]}
                                }
                            },
                            "as": "r",
                            "in": "$$r.wind_electricity"
                        }
                    }
                }
            }
        },
        {
            "$match": {
                "start_value": {"$ne": None},
                "end_value": {"$ne": None}
            }
        },
        {
            "$project": {
                "country": 1,
                "start_value": 1,
                "end_value": 1,
                "wind_growth": {"$subtract": ["$end_value", "$start_value"]}
            }
        },
        {"$sort": {"wind_growth": -1}},
        {"$limit": 10}
    ]

    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by wind electricity growth from {start_year} to {end_year}", results)


def fossil_dependency_ranking(year):
    pipeline = [
        {
            "$match": {
                "year": year,
                "electricity_generation": {"$gt": 50},
                "fossil_share_electricity": {"$gt": 0}
            }
        },
        {"$sort": {"fossil_share_electricity": -1}},
        {"$limit": 10},
        {
            "$project": {
                "_id": 0,
                "country": 1,
                "year": 1,
                "fossil_share_electricity": 1,
                "electricity_generation": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by fossil electricity dependency in {year}", results)


def electricity_demand_ranking(year):
    pipeline = [
        {
            "$match": {
                "year": year,
                "electricity_demand": {"$gt": 0}
            }
        },
        {"$sort": {"electricity_demand": -1}},
        {"$limit": 10},
        {
            "$project": {
                "_id": 0,
                "country": 1,
                "year": 1,
                "electricity_demand": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by electricity demand in {year}", results)


if __name__ == "__main__":
    print("Reading cleaned data from MongoDB...")
    print(f"Database: {DATABASE_NAME}")
    print(f"Collection: {CLEAN_COLLECTION_NAME}")
    print(f"Documents found: {collection.count_documents({})}")

    latest_year = get_latest_year()

    print(f"\nLatest available year in MongoDB: {latest_year}")

    if latest_year:
        start_year = latest_year - 10

        top_countries_by_renewable_electricity(latest_year)
        top_countries_by_renewable_share(latest_year)
        top_solar_growth_countries(start_year, latest_year)
        top_wind_growth_countries(start_year, latest_year)
        fossil_dependency_ranking(latest_year)
        electricity_demand_ranking(latest_year)
    else:
        print("No cleaned data found. Please run cleaning.py first.")

    client.close()
