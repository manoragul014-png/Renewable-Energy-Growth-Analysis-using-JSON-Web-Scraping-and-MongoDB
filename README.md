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
├── outputs/
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
fetching JSON data using Python requests and BeautifulSoup
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

## Installation and Setup

Follow the steps below to install and set up the project on your local system.

### 1. Clone the Repository
      git clone <repository-link>
      cd <project-folder-name>

### 2. Create a Virtual Environment
      python -m venv energy_project

### 3. Activate the Virtual Environment
#### For macOS/Linux:
      source energy_project/bin/activate

#### For Windows:
      energy_project\Scripts\activate

### 4. Install Required Libraries
      pip install -r requirements.txt

### 5. Create a .env File
      Create a .env file in the root folder of the project and add your MongoDB connection string:
            MONGO_URI=your_mongodb_connection_string

#### Example:
      MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/


## How to Run the Project
### Configuration                      --- Stores the project configuration settings such as MongoDB URI, database name, collection names, and the OWID energy data source URL.
      python src/config.py
### Clean the scraped JSON data        --- Raw data will be cleaned and stored in the MongoDB
      python src/scraper.py                          
### Insert cleaned data into MongoDB   --- After this, a separate folder for cleaned data will be created in the MongoDB
      python src/cleaning.py     
### Run business analysis              --- Objectives are achieved in this step                  
      python src/analysis.py                 
### Generate visualization             --- Output will be stored in the separate folder
      python src/visualization.py           

## Key Skills Demonstrated

- Web scraping and JSON data extraction using Python
- NoSQL database management using MongoDB
- Data cleaning and preprocessing with Pandas
- Exploratory data analysis for renewable energy trends
- Data visualization using Matplotlib
- End-to-end data pipeline development



