"""Configuración general del backend analítico.

Todos los valores se leen de variables de entorno (archivo .env). En el código no se
guardan credenciales: si falta una variable sensible queda vacía y la conexión falla
con un mensaje claro.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "Backend Analítico AgroPacayales - Cosechas y Rendimiento"
    APP_PORT = int(os.getenv("APP_PORT", "5050"))

    # MongoDB: colección plots (parcelas agrícolas)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
    MONGO_DB = os.getenv("MONGO_DB", "agropacayales_db")

    # SQL Server: tablas harvest, harvest_planting_cycle y cultivos
    SQL_SERVER = os.getenv("SQL_SERVER", "localhost")
    SQL_PORT = int(os.getenv("SQL_PORT", "1433"))
    SQL_DATABASE = os.getenv("SQL_DATABASE", "agropacayales_db")
    SQL_USER = os.getenv("SQL_USER", "")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")


settings = Settings()
