from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import BASE_DIR, DATABASE_NAME, CLEAN_COLLECTION_NAME, OUTPUT_DIR, get_database


SELECTED_COUNTRIES = ["India", "Germany", "China", "United States"]


def load_clean_dataframe():
    client, db = get_database()
    collection = db[CLEAN_COLLECTION_NAME]
    try:
        count = collection.count_documents({})
        print(f"Documents found in {DATABASE_NAME}.{CLEAN_COLLECTION_NAME}: {count}")
        if count == 0:
            raise RuntimeError("Clean collection has 0 documents. Run: python src/cleaning.py")
        data = list(collection.find({}, {"_id": 0}))
        return pd.DataFrame(data)
    finally:
        client.close()


def save_bar_chart(df, column, title, filename, year=None):
    if year is not None:
        df = df[df["year"] == year]

    chart_df = df[["country", column]].dropna().copy()
    chart_df = chart_df[chart_df[column] > 0]
    chart_df = chart_df.sort_values(column, ascending=False).head(10)

    if chart_df.empty:
        print(f"Skipping {filename}: no data available.")
        return

    plt.figure(figsize=(11, 6))
    plt.bar(chart_df["country"], chart_df[column])
    plt.title(title)
    plt.xlabel("Country")
    plt.ylabel(column.replace("_", " ").title())
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    output_path = OUTPUT_DIR / filename
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def save_growth_chart(df, column, title, filename, start_year, end_year):
    start_df = df[df["year"] == start_year][["country", column]].rename(columns={column: "start_value"})
    end_df = df[df["year"] == end_year][["country", column]].rename(columns={column: "end_value"})
    merged = pd.merge(start_df, end_df, on="country", how="inner")
    merged = merged.dropna(subset=["start_value", "end_value"])
    merged["growth"] = merged["end_value"] - merged["start_value"]
    chart_df = merged.sort_values("growth", ascending=False).head(10)

    if chart_df.empty:
        print(f"Skipping {filename}: no data available.")
        return

    plt.figure(figsize=(11, 6))
    plt.bar(chart_df["country"], chart_df["growth"])
    plt.title(title)
    plt.xlabel("Country")
    plt.ylabel("Growth")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    output_path = OUTPUT_DIR / filename
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def save_renewable_trend(df):
    trend_df = df[(df["country"].isin(SELECTED_COUNTRIES)) & (df["year"] >= 2000)]
    trend_df = trend_df.dropna(subset=["renewables_electricity"])

    if trend_df.empty:
        print("Skipping renewable_electricity_trend.png: no data available.")
        return

    plt.figure(figsize=(11, 6))
    for country in SELECTED_COUNTRIES:
        country_df = trend_df[trend_df["country"] == country].sort_values("year")
        if not country_df.empty:
            plt.plot(country_df["year"], country_df["renewables_electricity"], marker="o", label=country)

    plt.title("Renewable Electricity Trend Since 2000")
    plt.xlabel("Year")
    plt.ylabel("Renewable Electricity")
    plt.legend()
    plt.tight_layout()
    output_path = OUTPUT_DIR / "renewable_electricity_trend.png"
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def generate_all_visualizations():
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = load_clean_dataframe()

    latest_year = int(df["year"].max())
    start_year = latest_year - 10
    print(f"Latest available year: {latest_year}")

    save_bar_chart(
        df,
        "renewables_electricity",
        f"Top 10 Countries by Renewable Electricity Generation in {latest_year}",
        "top_renewable_electricity.png",
        latest_year,
    )
    save_bar_chart(
        df,
        "electricity_demand",
        f"Top 10 Countries by Electricity Demand in {latest_year}",
        "top_electricity_demand.png",
        latest_year,
    )
    save_growth_chart(
        df,
        "solar_electricity",
        f"Top 10 Countries by Solar Electricity Growth: {start_year} to {latest_year}",
        "top_solar_growth.png",
        start_year,
        latest_year,
    )
    save_growth_chart(
        df,
        "wind_electricity",
        f"Top 10 Countries by Wind Electricity Growth: {start_year} to {latest_year}",
        "top_wind_growth.png",
        start_year,
        latest_year,
    )
    save_renewable_trend(df)


if __name__ == "__main__":
    generate_all_visualizations()
