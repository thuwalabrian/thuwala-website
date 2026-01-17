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
"""

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(requirements)
print("✓ Updated requirements.txt")

# 3. Update app.py - add proper initialization
print("\n📝 Now you need to update app.py manually:")
print(
    "\nIn app.py, make sure the database initialization is INSIDE app context:"
)
print(
    """
# Add this at the end of app.py (replace the existing if __name__ block):

if __name__ == '__main__':
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created")
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@thuwalaco.com',
                password_hash=generate_password_hash('Admin@2024')
            )
            db.session.add(admin)
            print("Admin user created")
        
        # Add sample services
        if not Service.query.first():
            services = [
                Service(title='Administrative Support', description='Virtual assistant services', icon='fas fa-briefcase'),
                Service(title='Project Support', description='Proposal writing', icon='fas fa-project-diagram'),
                Service(title='Data Analytics', description='Data cleaning', icon='fas fa-chart-bar'),
                Service(title='Communications', description='Corporate profiles', icon='fas fa-comments'),
            ]
            for service in services:
                db.session.add(service)
            print("Sample services added")
        
        db.session.commit()
    
    # Run app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
"""
)

print("\n✅ Updates ready!")
print("\nNext steps:")
print("1. Update app.py as shown above")
print("2. git add config.py requirements.txt app.py")
print("3. git commit -m 'Add PostgreSQL support'")
print("4. git push")
print("5. Render will auto-redeploy")
