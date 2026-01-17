# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 19:47:34 2026

@author: DMZ
"""

# quick_fix.py
with open("requirements.txt", "w") as f:
    f.write(
        """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-WTF==1.2.1
Flask-Login==0.6.2
Werkzeug==2.3.7
python-dotenv==1.0.0
gunicorn==20.1.0"""
    )

with open("config.py", "w") as f:
    f.write(
        """import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-this')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///thuwala.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False"""
    )

print("Files updated. Now commit and push.")
