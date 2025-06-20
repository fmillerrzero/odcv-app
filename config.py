"""
Configuration for ODCV Prospecting App
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# NYC Geoclient API (get from NYC Developer Portal)
GEOCLIENT_APP_ID = os.getenv("GEOCLIENT_APP_ID", "")
GEOCLIENT_APP_KEY = os.getenv("GEOCLIENT_APP_KEY", "")

# Database
DB_PATH = str(CACHE_DIR / "odcv.db")

# Data file paths
PLUTO_FILES = {
    "MN": DATA_DIR / "pluto" / "MN.csv",
    "BX": DATA_DIR / "pluto" / "BX.csv", 
    "BK": DATA_DIR / "pluto" / "BK.csv",
    "QN": DATA_DIR / "pluto" / "QN.csv",
    "SI": DATA_DIR / "pluto" / "SI.csv"
}

LL84_FILE = DATA_DIR / "ll84_monthly.csv"
LL87_FILE = DATA_DIR / "ll87_2019_2024.csv"
LL33_FILE = DATA_DIR / "ll33_grades.csv"

# ODCV Scoring Parameters
ODCV_PARAMS = {
    "min_building_size": 75000,  # sq ft
    "target_building_age": 2010,  # built before
    "high_eui_threshold": 100,   # kBtu/sq ft
    "low_occupancy_threshold": 70,  # %
    "poor_grades": ["D", "F"],
    "medium_grade": "C",
    
    # Deployment parameters
    "ahu_per_floors": 5,  # Estimate 1 AHU per 5 floors
    "sensor_cost": 2000,  # $ per sensor
    "integration_weeks_with_bms": 2,
    "integration_weeks_without_bms": 4,
    
    # Savings estimates
    "savings_low_occupancy": 0.30,  # 30% for <60% occupancy
    "savings_medium_occupancy": 0.20,  # 20% for 60-80%
    "savings_high_occupancy": 0.10,  # 10% for >80%
    "energy_cost_per_kwh": 0.15  # $/kWh
}

# API Settings
API_TITLE = "ODCV Building Intelligence API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
R-Zero ODCV Prospecting Tool

Transforms building data into actionable ODCV opportunities.
"""

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
