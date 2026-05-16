# Renewable Energy Growth Analysis using JSON Web Scraping and MongoDB

## Project Overview

This project focuses on collecting, storing, cleaning, analyzing, and visualizing renewable energy data using JSON-based web scraping and MongoDB. The main objective is to understand renewable energy growth trends across countries and years by building a small end-to-end data management and analysis pipeline.

The project demonstrates how raw JSON data can be extracted from a web source, stored in MongoDB, cleaned using Python, analyzed for meaningful insights, and visualized for better interpretation.

---

## Objectives

- Which countries generate the most renewable electricity?
- Which countries have the highest renewable electricity share?
- Which countries showed the highest solar electricity growth?
- Which countries showed the highest wind electricity growth?
- Which countries still depend heavily on fossil fuels for electricity?
- Which countries have the highest electricity demand?
- How has renewable electricity changed since 2000 in India, Germany, China, and the United States?

---

## Project Structure

```text
renewable-energy-json-scraper/
│
├── src/
│   ├── config.py              
│   ├── scraper.py             
│   ├── cleaning.py            
│   ├── analysis.py            
│   └── visualization.py       
│
├── output/
│   ├── renewable_electricity_trend.png     
│   ├── top_electricity_demand.png          
│   ├── top_renewable_electricity.png    
│   ├── top_solar_growth.png
│   └── top_wind_growth.png       
│
├── README.md                  
├── requirements.txt           
└── .env
```


## Dataset / Data Source

The project uses renewable energy data collected from a JSON-based web source.

The data contains information related to:

- Energy consumption
- Electricity generation
- Renewable electricity production
- Countries
- Years

The collected data is stored in MongoDB in raw format and later cleaned for analysis.

---

## Workflow

The project follows a simple end-to-end data pipeline:

```text
Website - Our World In Data - Energy Dataset
      ↓
Scraping the data using Beautifulsoup
      ↓
MongoDB Raw Collection
      ↓
Data Cleaning
      ↓
MongoDB Cleaned Collection
      ↓
Data Analysis
      ↓
Data Visualization
      ↓
Insights (Output)
```


                    




