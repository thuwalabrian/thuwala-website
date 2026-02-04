# update_for_postgres.py
import os

print("Updating files for PostgreSQL deployment...")

# 1. Update config.py
config_content = """import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
    
    # Handle PostgreSQL URL (Render provides postgres://, SQLAlchemy needs postgresql://)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix postgres:// to postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback to SQLite for local development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///thuwala.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
"""

with open("config.py", "w", encoding="utf-8") as f:
    f.write(config_content)
print("✓ Updated config.py")

# 2. Update requirements.txt
requirements = """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-WTF==1.2.1
Flask-Login==0.6.2
Werkzeug==2.3.7
python-dotenv==1.0.0
gunicorn==20.1.0
psycopg2-binary==2.9.9
alembic==1.11.1
"""

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(requirements)
print("✓ Updated requirements.txt")

# 3. Update app.py - add proper initialization
print("\n📝 Now you need to update app.py manually or use Alembic for migrations:")
print(
    "\nRecommended steps:\n"
    "1) Do NOT run destructive schema SQL from application import. Ensure your DB init is behind an `if __name__ == '__main__'` guard (app.py already updated by helper).\n"
    "2) Use Alembic (included in requirements) to manage schema changes. Run `alembic revision --autogenerate -m \"desc\"` then `alembic upgrade head`.\n"
    "3) If you cannot use Alembic, apply manual ALTER TABLE statements on your Postgres instance.\n"
)

print(
    "If you will use Alembic, initialize the local environment once:\n"
    "  pip install -r requirements.txt\n"
    "  alembic revision --autogenerate -m \"init\"\n"
    "  alembic upgrade head\n"
)

print("\n✅ Updates ready!")
print("\nNext steps:")
print("1. Update app.py as shown above")
print("2. git add config.py requirements.txt app.py")
print("3. git commit -m 'Add PostgreSQL support'")
print("4. git push")
print("5. Render will auto-redeploy")
