import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = "energy_project_db"
RAW_COLLECTION_NAME = "raw_energy_json"
CLEAN_COLLECTION_NAME = "renewable_energy"

OWID_ENERGY_JSON_URL = "https://owid-public.owid.io/data/energy/owid-energy-data.json"
