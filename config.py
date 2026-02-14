import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Detect Vercel serverless environment
    IS_VERCEL = os.environ.get("VERCEL", "").lower() in ("1", "true")

    # Require SECRET_KEY in production; allow a development fallback locally.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        if os.environ.get("FLASK_ENV", "").lower() == "production" or IS_VERCEL:
            raise RuntimeError(
                "SECRET_KEY must be set in production (see .env.example)"
            )
        # Development fallback (safe only on local machines)
        SECRET_KEY = "dev-secret-key-change-this"

    # Database URL (use DATABASE_URL env var when provided).
    # On Vercel the project root is read-only, so default SQLite goes to /tmp/.
    _default_db = (
        "sqlite:////tmp/thuwala.db"
        if IS_VERCEL
        else "sqlite:///" + os.path.join(os.path.dirname(__file__), "thuwala.db")
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _default_db)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folder configuration
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "static/uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = set(
        os.environ.get("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif,webp").split(",")
    )

    # Email configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@thuwalaco.com")

    # Password reset settings
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS = int(
        os.environ.get("PASSWORD_RESET_TOKEN_EXPIRE_HOURS", 24)
    )
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    if not SECURITY_PASSWORD_SALT:
        if os.environ.get("FLASK_ENV", "").lower() == "production" or IS_VERCEL:
            raise RuntimeError(
                "SECURITY_PASSWORD_SALT must be set in production (see .env.example)"
            )
        SECURITY_PASSWORD_SALT = "password-reset-salt-change-this"

    # WhatsApp integration (for Vercel / no-database deployments)
    # Set WHATSAPP_ENABLED=true to redirect contact-form submissions to WhatsApp.
    WHATSAPP_ENABLED = os.environ.get("WHATSAPP_ENABLED", "true").lower() == "true"
    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "265887873006")
