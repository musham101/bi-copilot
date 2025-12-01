import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ---------- GEMINI ----------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash"

# ---------- DB ----------
DB_HOST = "relational.fel.cvut.cz"
DB_PORT = 3306
DB_NAME = "AdventureWorks2014"  # case-sensitive as on the site
DB_USER = "guest"
DB_PASSWORD = "ctu-relational"