import os
import certifi
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

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
