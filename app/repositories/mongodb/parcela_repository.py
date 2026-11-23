"""Consultas a MongoDB sobre las parcelas (colección plots).

Solo obtiene datos: los cálculos e indicadores se hacen en services/analytics.
"""
from app.database.mongodb import get_database
from app.models.parcela import Parcela

_CAMPOS = {"nombre": 1, "area_hectareas": 1, "estado_riego": 1, "tipo_suelo": 1}


def _a_parcela(documento: dict) -> Parcela:
    return Parcela(
        id_parcela=str(documento["_id"]),
        nombre=documento.get("nombre", ""),
        area_hectareas=float(documento.get("area_hectareas") or 0),
        estado_riego=documento.get("estado_riego") or "Sin registro",
        tipo_suelo=documento.get("tipo_suelo") or "Sin registro",
    )


def obtener_parcelas_activas() -> list[Parcela]:
    """Parcelas con estado activo."""
    documentos = get_database()["plots"].find({"estado": True}, _CAMPOS)
    return [_a_parcela(d) for d in documentos]


def obtener_parcelas_por_ids(ids: list[str]) -> list[Parcela]:
    """Parcelas cuyo _id está en la lista (para cruzar con las cosechas de SQL Server)."""
    if not ids:
        return []
    documentos = get_database()["plots"].find({"_id": {"$in": ids}}, _CAMPOS)
    return [_a_parcela(d) for d in documentos]


def obtener_parcela_por_id(id_parcela: str) -> dict | None:
    """Datos maestros de una parcela (nombre, área, suelo, riego) mediante su _id."""
    return get_database()["plots"].find_one({"_id": id_parcela})
