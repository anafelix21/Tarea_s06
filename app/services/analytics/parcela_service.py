"""Indicadores de parcelas (MongoDB)."""
from collections import Counter

from app.repositories.mongodb import parcela_repository


def parcelas_por_estado_riego() -> dict:
    """Cantidad de parcelas activas según su estado de riego, de mayor a menor."""
    conteo = Counter(p.estado_riego for p in parcela_repository.obtener_parcelas_activas())
    return dict(conteo.most_common())
