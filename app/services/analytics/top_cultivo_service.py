"""Indicador integrado: cultivo más cosechado del mes (SQL Server + MongoDB).

SQL Server aporta cuánto se cosechó (transaccional) y MongoDB aporta los datos
maestros de la parcela donde está sembrado el cultivo.
"""
from app.repositories.mongodb import parcela_repository
from app.repositories.sqlserver import cosecha_repository
from app.schemas.analytics_schema import IndicatorResponse


def get_top_cultivo_mes() -> IndicatorResponse | None:
    # 1. Obtener la cosecha desde SQL Server
    cosecha = cosecha_repository.obtener_top_cultivo_mes()
    if not cosecha:
        return None

    # 2. Obtener la información de la parcela desde MongoDB
    parcela = parcela_repository.obtener_parcela_por_id(cosecha["id_parcela"])
    if not parcela:
        return None

    # 3. Integrar ambas fuentes
    data = {
        "mes": cosecha["mes"],
        "id_cultivo": cosecha["id_cultivo"],
        "cultivo": cosecha["cultivo"],
        "kilos": cosecha["kilos"],
        "id_parcela": cosecha["id_parcela"],
        "parcela": parcela.get("nombre"),
        "tipo_suelo": parcela.get("tipo_suelo"),
        "area_hectareas": parcela.get("area_hectareas"),
        "estado_riego": parcela.get("estado_riego"),
    }

    # 4. Retornar el indicador estándar
    return IndicatorResponse(
        indicator="top_cultivo_month",
        title="Cultivo más cosechado del mes",
        chart_type="card",
        data=data,
        sources=["SQL Server", "MongoDB"],
    )
