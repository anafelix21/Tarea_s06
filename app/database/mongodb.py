"""Conexión con MongoDB (base documental: parcelas agrícolas)."""
from pymongo import MongoClient

from app.config.settings import settings

_client = None


def get_database():
    """Devuelve la base de MongoDB reutilizando un único cliente."""
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client[settings.MONGO_DB]


def ping() -> bool:
    """True si MongoDB responde."""
    try:
        get_database().command("ping")
        return True
    except Exception:
        return False
