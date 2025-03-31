import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-fallback-secret-key")
    SECURITY_PASSWORD_SALT = os.getenv(
        "SECURITY_PASSWORD_SALT", "default-fallback-salt"
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

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    )

    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "1025"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False").lower() in ("true", "1", "t")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() in ("true", "1", "t")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")
