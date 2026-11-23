"""Indicadores de cosechas (lógica de análisis).

Obtiene los datos desde el repository de SQL Server y realiza los cálculos:
sumas, promedios, agrupaciones y clasificaciones.
"""
from collections import defaultdict

from app.repositories.sqlserver import cosecha_repository

LIMITE_MERMA = 20.0   # regla de negocio: la merma no puede superar el 20 % de cada línea


def _redondear(valor: float) -> float:
    return round(valor, 2)


def _porcentaje(parte: float, total: float) -> float:
    return _redondear(parte / total * 100) if total > 0 else 0.0


def resumen_cosechas() -> dict:
    """Totales generales: cosechas, kilos óptimos, merma y porcentaje de merma global."""
    lineas = cosecha_repository.obtener_lineas_cosecha()
    optimos = sum(l.kilos_optimos for l in lineas)
    merma = sum(l.kilos_merma for l in lineas)
    totales = optimos + merma
    return {
        "total_cosechas": len({l.id_cosecha for l in lineas}),
        "total_lineas": len(lineas),
        "kilos_optimos": _redondear(optimos),
        "kilos_merma": _redondear(merma),
        "kilos_totales": _redondear(totales),
        "porcentaje_merma_global": _porcentaje(merma, totales),
        "promedio_kilos_por_cosecha": _redondear(totales / len({l.id_cosecha for l in lineas})) if lineas else 0.0,
    }


def kilos_por_cultivo() -> dict:
    """Kilos totales y porcentaje de merma de cada cultivo, de mayor a menor producción."""
    acumulado = defaultdict(lambda: {"kilos_optimos": 0.0, "kilos_merma": 0.0})
    for l in cosecha_repository.obtener_lineas_cosecha():
        acumulado[l.cultivo]["kilos_optimos"] += l.kilos_optimos
        acumulado[l.cultivo]["kilos_merma"] += l.kilos_merma

    resultado = {}
    for cultivo, v in sorted(acumulado.items(), key=lambda x: -(x[1]["kilos_optimos"] + x[1]["kilos_merma"])):
        totales = v["kilos_optimos"] + v["kilos_merma"]
        resultado[cultivo] = {
            "kilos_optimos": _redondear(v["kilos_optimos"]),
            "kilos_merma": _redondear(v["kilos_merma"]),
            "kilos_totales": _redondear(totales),
            "porcentaje_merma": _porcentaje(v["kilos_merma"], totales),
        }
    return resultado


def clasificar_merma(porcentaje: float) -> str:
    """Clasifica una línea de cosecha según su porcentaje de merma."""
    if porcentaje < 5:
        return "Óptima (merma menor al 5%)"
    if porcentaje <= 10:
        return "Aceptable (merma entre 5% y 10%)"
    if porcentaje <= LIMITE_MERMA:
        return "Crítica (merma entre 10% y 20%)"
    return "Fuera de norma (merma mayor al 20%)"


def calidad_de_cosecha() -> dict:
    """Cantidad de líneas de cosecha en cada nivel de calidad (según su merma)."""
    categorias = {
        "Óptima (merma menor al 5%)": 0,
        "Aceptable (merma entre 5% y 10%)": 0,
        "Crítica (merma entre 10% y 20%)": 0,
        "Fuera de norma (merma mayor al 20%)": 0,
    }
    for l in cosecha_repository.obtener_lineas_cosecha():
        categorias[clasificar_merma(l.porcentaje_merma)] += 1
    return categorias


def cosechas_por_mes() -> dict:
    """Kilos totales cosechados por mes (yyyy-MM), en orden cronológico."""
    por_mes = defaultdict(float)
    for l in cosecha_repository.obtener_lineas_cosecha():
        por_mes[l.fecha_cosecha.strftime("%Y-%m")] += l.kilos_totales
    return {mes: _redondear(kilos) for mes, kilos in sorted(por_mes.items())}
