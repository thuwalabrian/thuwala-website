import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-this')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///thuwala.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False