import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "slims_reminder"),
}

SMTP_CONFIG = {
    "email": os.getenv("SMTP_EMAIL", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
    "host": "smtp.gmail.com",
    "port": 587,
}

REMINDER_DAYS_BEFORE = [1, 2]