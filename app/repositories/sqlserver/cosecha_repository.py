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


_CONSULTA_TOP_CULTIVO_MES = """
    SELECT TOP 1
        FORMAT(h.fecha_cosecha, 'yyyy-MM') AS mes,
        c.id_cultivo,
        c.nombre AS cultivo,
        c.id_parcela,
        SUM(d.kilos_optimos + d.kilos_merma) AS kilos_totales
    FROM dbo.harvest h
    JOIN dbo.harvest_planting_cycle d ON d.id_harvest = h.id_harvest
    JOIN dbo.cultivos c ON c.id_cultivo = d.id_cultivo
    WHERE h.estado = 1
      AND FORMAT(h.fecha_cosecha, 'yyyy-MM') = (
          SELECT FORMAT(MAX(fecha_cosecha), 'yyyy-MM') FROM dbo.harvest WHERE estado = 1
      )
    GROUP BY FORMAT(h.fecha_cosecha, 'yyyy-MM'), c.id_cultivo, c.nombre, c.id_parcela
    ORDER BY kilos_totales DESC
"""


def obtener_top_cultivo_mes() -> dict | None:
    """Cultivo con más kilos cosechados en el último mes con cosechas.

    SQL Server solo sabe: "el cultivo 4 (parcela PARC-CEN-063) cosechó 925 kg en 2026-11".
    """
    with get_connection() as connection:
        cursor = connection.cursor(as_dict=True)
        cursor.execute(_CONSULTA_TOP_CULTIVO_MES)
        fila = cursor.fetchone()
    if not fila:
        return None
    return {
        "mes": fila["mes"],
        "id_cultivo": fila["id_cultivo"],
        "cultivo": fila["cultivo"],
        "id_parcela": fila["id_parcela"],
        "kilos": float(fila["kilos_totales"]),
    }
