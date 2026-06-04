import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Twilio base
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Twilio Voice SDK
TWILIO_API_KEY_SID = os.getenv("TWILIO_API_KEY_SID")
TWILIO_API_KEY_SECRET = os.getenv("TWILIO_API_KEY_SECRET")
TWILIO_TWIML_APP_SID = os.getenv("TWILIO_TWIML_APP_SID")

# Patient-facing ScanX caller ID
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

# App
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
CALL_BUTTON_SECRET = os.getenv("CALL_BUTTON_SECRET", "dev-secret")

# PostgreSQL / Cloud SQL
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "scanx_app")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

# print("ENV FILE LOADED")
# print("CALL_BUTTON_SECRET:", repr(CALL_BUTTON_SECRET))
# print("DB_HOST:", DB_HOST)
# print("DB_NAME:", DB_NAME)
# print("DB_USER:", DB_USER)
# print("INSTANCE_CONNECTION_NAME:", INSTANCE_CONNECTION_NAME)