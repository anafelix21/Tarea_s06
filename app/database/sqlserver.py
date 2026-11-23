"""Conexión con SQL Server (base transaccional: cosechas y cultivos)."""
from contextlib import contextmanager

import pymssql

from app.config.settings import settings


@contextmanager
def get_connection():
    """Abre una conexión a SQL Server y la cierra siempre al terminar."""
    connection = pymssql.connect(
        server=settings.SQL_SERVER,
        port=settings.SQL_PORT,
        user=settings.SQL_USER,
        password=settings.SQL_PASSWORD,
        database=settings.SQL_DATABASE,
        login_timeout=5,
        timeout=15,
    )
    try:
        yield connection
    finally:
        connection.close()


def ping() -> bool:
    """True si SQL Server responde."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except Exception:
        return False
