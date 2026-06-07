# config/settings.py
import os

# Database Configuration (SQL Server Localhost)
# Adjust driver if needed (e.g., 'ODBC Driver 18 for SQL Server')
DB_DRIVER = "ODBC Driver 17 for SQL Server"
DB_SERVER = "LOCALHOST\\FYT"
DB_NAME = "BRE"

DATABASE_URL = f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}&trusted_connection=yes"

# Reconciliation Rules
AMOUNT_TOLERANCE = 0.00  # Strict matching
TIME_WINDOW_SECONDS = 300

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")