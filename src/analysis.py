from config import DATABASE_NAME, CLEAN_COLLECTION_NAME, get_database


def print_results(title, results):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)
    if not results:
        print("No results found.")
        return
    for item in results:
        print(item)


def get_latest_year(collection):
    result = collection.find_one(sort=[("year", -1)])
    return result["year"] if result else None


def top_countries_by_renewable_electricity(collection, year):
    pipeline = [
        {"$match": {"year": year, "renewables_electricity": {"$gt": 0}}},
        {"$sort": {"renewables_electricity": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "country": 1, "year": 1, "renewables_electricity": 1}},
    ]
    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by renewable electricity generation in {year}", results)


def top_countries_by_renewable_share(collection, year):
    pipeline = [
        {"$match": {"year": year, "electricity_generation": {"$gt": 50}, "renewables_share_electricity": {"$gt": 0}}},
        {"$sort": {"renewables_share_electricity": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "country": 1, "year": 1, "renewables_share_electricity": 1, "electricity_generation": 1}},
    ]
    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by renewable electricity share in {year}", results)


def growth_ranking(collection, start_year, end_year, field_name, output_name):
    pipeline = [
        {"$match": {"year": {"$in": [start_year, end_year]}, field_name: {"$gte": 0}}},
        {"$group": {"_id": "$country", "records": {"$push": {"year": "$year", "value": f"${field_name}"}}}},
        {"$project": {
            "_id": 0,
            "country": "$_id",
            "start_value": {"$first": {"$map": {"input": {"$filter": {"input": "$records", "as": "r", "cond": {"$eq": ["$$r.year", start_year]}}}, "as": "x", "in": "$$x.value"}}},
            "end_value": {"$first": {"$map": {"input": {"$filter": {"input": "$records", "as": "r", "cond": {"$eq": ["$$r.year", end_year]}}}, "as": "x", "in": "$$x.value"}}},
        }},
        {"$match": {"start_value": {"$ne": None}, "end_value": {"$ne": None}}},
        {"$project": {"country": 1, "start_value": 1, "end_value": 1, output_name: {"$subtract": ["$end_value", "$start_value"]}}},
        {"$sort": {output_name: -1}},
        {"$limit": 10},
    ]
    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by {output_name.replace('_', ' ')} from {start_year} to {end_year}", results)


def fossil_dependency_ranking(collection, year):
    pipeline = [
        {"$match": {"year": year, "electricity_generation": {"$gt": 50}, "fossil_share_electricity": {"$gt": 0}}},
        {"$sort": {"fossil_share_electricity": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "country": 1, "year": 1, "fossil_share_electricity": 1, "electricity_generation": 1}},
    ]
    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by fossil electricity dependency in {year}", results)


def electricity_demand_ranking(collection, year):
    pipeline = [
        {"$match": {"year": year, "electricity_demand": {"$gt": 0}}},
        {"$sort": {"electricity_demand": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "country": 1, "year": 1, "electricity_demand": 1}},
    ]
    results = list(collection.aggregate(pipeline))
    print_results(f"Top 10 countries by electricity demand in {year}", results)


def run_analysis():
    client, db = get_database()
    collection = db[CLEAN_COLLECTION_NAME]
    try:
        print("Reading cleaned data from MongoDB...")
        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {CLEAN_COLLECTION_NAME}")
        doc_count = collection.count_documents({})
        print(f"Documents found: {doc_count}")

        if doc_count == 0:
            raise RuntimeError("Clean collection has 0 documents. Run: python src/cleaning.py")

        latest_year = get_latest_year(collection)
        print(f"\nLatest available year in MongoDB: {latest_year}")

        start_year = latest_year - 10
        top_countries_by_renewable_electricity(collection, latest_year)
        top_countries_by_renewable_share(collection, latest_year)
        growth_ranking(collection, start_year, latest_year, "solar_electricity", "solar_growth")
        growth_ranking(collection, start_year, latest_year, "wind_electricity", "wind_growth")
        fossil_dependency_ranking(collection, latest_year)
        electricity_demand_ranking(collection, latest_year)

    finally:
        client.close()


if __name__ == "__main__":
    run_analysis()
