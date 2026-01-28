import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-cambiar-en-produccion")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATA_DIR / 'finanzas.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
