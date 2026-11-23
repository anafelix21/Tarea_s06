"""Modelo de una parcela agrícola (documento de la colección plots en MongoDB)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Parcela:
    id_parcela: str
    nombre: str
    area_hectareas: float
    estado_riego: str
    tipo_suelo: str
