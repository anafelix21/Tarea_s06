"""Indicador combinado: rendimiento por parcela (SQL Server + MongoDB).

Los kilos cosechados vienen de SQL Server (cultivos.id_parcela) y el área de cada
parcela viene de MongoDB (plots._id). El service cruza ambas fuentes y calcula kg/ha.
"""
from collections import defaultdict

from app.repositories.mongodb import parcela_repository
from app.repositories.sqlserver import cosecha_repository


def rendimiento_por_parcela() -> dict:
    """Kilos cosechados, área y rendimiento (kg por hectárea) de cada parcela."""
    kilos = defaultdict(float)
    for l in cosecha_repository.obtener_lineas_cosecha():
        kilos[l.id_parcela] += l.kilos_totales

    parcelas = {p.id_parcela: p for p in parcela_repository.obtener_parcelas_por_ids(list(kilos))}

    resultado = {}
    for id_parcela, total in sorted(kilos.items(), key=lambda x: -x[1]):
        parcela = parcelas.get(id_parcela)
        if parcela and parcela.area_hectareas > 0:
            resultado[parcela.nombre] = {
                "id_parcela": id_parcela,
                "area_hectareas": round(parcela.area_hectareas, 2),
                "kilos_totales": round(total, 2),
                "rendimiento_kg_ha": round(total / parcela.area_hectareas, 2),
            }
        else:
            # La parcela no existe en MongoDB: se informa sin inventar el área
            resultado[f"Parcela {id_parcela} (no registrada en MongoDB)"] = {
                "id_parcela": id_parcela,
                "area_hectareas": None,
                "kilos_totales": round(total, 2),
                "rendimiento_kg_ha": None,
            }
    return resultado
