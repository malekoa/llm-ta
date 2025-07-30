import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

class Config:
    DB_PATH = os.path.join(BASE_DIR, "shared", "data.db")
    SCHEMA_PATH = os.path.join(BASE_DIR, "shared", "schema.sql")
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
    GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
    GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
