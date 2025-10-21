import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "7"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "joby"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432"))
}

EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "email_user": os.getenv("EMAIL_USER"),
    "email_password": os.getenv("EMAIL_PASSWORD")
}

JOBS_SERVER_URL = os.getenv("JOBS_SERVER_URL", "http://localhost:8002")
BACKEND_SERVER_URL = os.getenv("BACKEND_SERVER_URL", "http://localhost:8001")
