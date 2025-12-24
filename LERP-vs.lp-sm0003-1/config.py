# config.py
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "lerp_super_chave_segura")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///lerp_gestao.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
