"""Consultas a SQL Server sobre las cosechas.

Solo obtiene datos: los cálculos e indicadores se hacen en services/analytics.
Tablas: harvest (cabecera), harvest_planting_cycle (detalle) y cultivos.
"""
from app.database.sqlserver import get_connection
from app.models.linea_cosecha import LineaCosecha

_CONSULTA_LINEAS = """
    SELECT h.id_harvest, h.fecha_cosecha, h.responsable,
           d.id_cultivo, c.nombre AS cultivo, c.id_parcela,
           d.kilos_optimos, d.kilos_merma
    FROM dbo.harvest h
    JOIN dbo.harvest_planting_cycle d ON d.id_harvest = h.id_harvest
    JOIN dbo.cultivos c ON c.id_cultivo = d.id_cultivo
    WHERE h.estado = 1
    ORDER BY h.fecha_cosecha, h.id_harvest
"""


def obtener_lineas_cosecha() -> list[LineaCosecha]:
    """Devuelve cada cultivo cosechado (detalle) de las cosechas activas."""
    with get_connection() as connection:
        cursor = connection.cursor(as_dict=True)
        cursor.execute(_CONSULTA_LINEAS)
        filas = cursor.fetchall()
    return [
        LineaCosecha(
            id_cosecha=fila["id_harvest"],
            fecha_cosecha=fila["fecha_cosecha"],
            responsable=fila["responsable"],
            id_cultivo=fila["id_cultivo"],
            cultivo=fila["cultivo"],
            id_parcela=fila["id_parcela"],
            kilos_optimos=float(fila["kilos_optimos"]),
            kilos_merma=float(fila["kilos_merma"]),
        )
        for fila in filas
    ]
