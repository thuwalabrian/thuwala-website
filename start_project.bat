@echo off
echo ========================================
echo    Starting Thuwala Co. Website
echo ========================================
echo.

REM Navigate to project directory
cd /d "C:\Users\DMZ\Desktop\thuwala-website"

REM Activate virtual environment
echo Activating virtual environment...
call thuwala\Scripts\activate.bat

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Install/update packages if needed
echo Checking packages...
pip install -r requirements.txt --quiet

REM Initialize database
echo Initializing database...
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database ready!')
"
echo.

REM Start the application
echo ========================================
echo    Application Starting...
echo ========================================
echo.
echo 🌐 Website:    http://localhost:5000
echo 🔐 Admin:      http://localhost:5000/admin/login
echo 📝 Username:   admin
echo 🔑 Password:   Admin@2024
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause