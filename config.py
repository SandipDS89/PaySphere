import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file and loads variables

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # turns off a feature we don't need, saves memory
    SECRET_KEY = os.getenv("SECRET_KEY")