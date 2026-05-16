import os
import certifi
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = "energy_project"
CLEAN_COLLECTION_NAME = "owid_energy_cleaned"

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


def create_output_folder():
    os.makedirs("outputs", exist_ok=True)


def get_latest_year():
    result = collection.find_one(sort=[("year", -1)])
    return result["year"] if result else None


def save_bar_chart(df, x_col, y_col, title, xlabel, ylabel, filename):
    if df.empty:
        print(f"No data available for {title}")
        return

    plt.figure(figsize=(12, 6))
    plt.bar(df[x_col], df[y_col])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    path = f"outputs/{filename}"
    plt.savefig(path)
    plt.close()

    print(f"Saved chart: {path}")


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
                "renewables_electricity": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    save_bar_chart(
        df=df,
        x_col="country",
        y_col="renewables_electricity",
        title=f"Top 10 Countries by Renewable Electricity Generation ({year})",
        xlabel="Country",
        ylabel="Renewable Electricity Generation",
        filename="top_renewable_electricity.png"
    )


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
                "renewables_share_electricity": 1,
                "electricity_generation": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    save_bar_chart(
        df=df,
        x_col="country",
        y_col="renewables_share_electricity",
        title=f"Top 10 Countries by Renewable Electricity Share ({year})",
        xlabel="Country",
        ylabel="Renewable Electricity Share (%)",
        filename="top_renewable_share.png"
    )


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
                "solar_growth": {"$subtract": ["$end_value", "$start_value"]}
            }
        },
        {"$sort": {"solar_growth": -1}},
        {"$limit": 10}
    ]

    results = list(collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    save_bar_chart(
        df=df,
        x_col="country",
        y_col="solar_growth",
        title=f"Top 10 Countries by Solar Electricity Growth ({start_year}–{end_year})",
        xlabel="Country",
        ylabel="Solar Electricity Growth",
        filename="top_solar_growth.png"
    )


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
                "wind_growth": {"$subtract": ["$end_value", "$start_value"]}
            }
        },
        {"$sort": {"wind_growth": -1}},
        {"$limit": 10}
    ]

    results = list(collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    save_bar_chart(
        df=df,
        x_col="country",
        y_col="wind_growth",
        title=f"Top 10 Countries by Wind Electricity Growth ({start_year}–{end_year})",
        xlabel="Country",
        ylabel="Wind Electricity Growth",
        filename="top_wind_growth.png"
    )


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
                "fossil_share_electricity": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    save_bar_chart(
        df=df,
        x_col="country",
        y_col="fossil_share_electricity",
        title=f"Top 10 Countries by Fossil Electricity Dependency ({year})",
        xlabel="Country",
        ylabel="Fossil Electricity Share (%)",
        filename="top_fossil_dependency.png"
    )


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
                "electricity_demand": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    save_bar_chart(
        df=df,
        x_col="country",
        y_col="electricity_demand",
        title=f"Top 10 Countries by Electricity Demand ({year})",
        xlabel="Country",
        ylabel="Electricity Demand",
        filename="top_electricity_demand.png"
    )


def renewable_trend_for_selected_countries():
    selected_countries = ["India", "Germany", "China", "United States"]

    pipeline = [
        {
            "$match": {
                "country": {"$in": selected_countries},
                "year": {"$gte": 2000},
                "renewables_electricity": {"$gt": 0}
            }
        },
        {
            "$project": {
                "_id": 0,
                "country": 1,
                "year": 1,
                "renewables_electricity": 1
            }
        },
        {"$sort": {"year": 1}}
    ]

    results = list(collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    if df.empty:
        print("No data available for renewable trend chart")
        return

    plt.figure(figsize=(12, 6))

    for country in selected_countries:
        country_df = df[df["country"] == country]
        plt.plot(
            country_df["year"],
            country_df["renewables_electricity"],
            marker="o",
            label=country
        )

    plt.title("Renewable Electricity Trend for Selected Countries Since 2000")
    plt.xlabel("Year")
    plt.ylabel("Renewable Electricity Generation")
    plt.legend()
    plt.tight_layout()

    path = "outputs/renewable_electricity_trend.png"
    plt.savefig(path)
    plt.close()

    print(f"Saved chart: {path}")


def generate_all_visualizations():
    create_output_folder()

    latest_year = get_latest_year()

    if not latest_year:
        print("No data found in MongoDB.")
        return

    start_year = latest_year - 10

    print(f"Creating visualizations using latest year: {latest_year}")
    print(f"Growth period: {start_year} to {latest_year}")

    top_countries_by_renewable_electricity(latest_year)
    top_countries_by_renewable_share(latest_year)
    top_solar_growth_countries(start_year, latest_year)
    top_wind_growth_countries(start_year, latest_year)
    fossil_dependency_ranking(latest_year)
    electricity_demand_ranking(latest_year)
    renewable_trend_for_selected_countries()

    print("\nAll visualizations created successfully.")
    print("Check the outputs folder.")


if __name__ == "__main__":
    generate_all_visualizations()
    client.close()