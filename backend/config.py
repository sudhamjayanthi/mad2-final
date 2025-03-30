import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
    SECURITY_PASSWORD_SALT = os.getenv(
        "SECURITY_PASSWORD_SALT", "your-salt-keep-it-secret"
    )
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///main.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECURITY_HEADERS = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authentication-Token",
        "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,OPTIONS",
    }

    SECURITY_RETURN_GENERIC_RESPONSES = False
    SECURITY_JSON_MESSAGES = True

