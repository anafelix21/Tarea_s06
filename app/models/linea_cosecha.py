"""Modelo de una línea de cosecha: un cultivo dentro de una cosecha (cabecera + detalle)."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LineaCosecha:
    id_cosecha: int
    fecha_cosecha: date
    responsable: str
    id_cultivo: int
    cultivo: str
    id_parcela: str
    kilos_optimos: float
    kilos_merma: float

    @property
    def kilos_totales(self) -> float:
        return self.kilos_optimos + self.kilos_merma

    @property
    def porcentaje_merma(self) -> float:
        return (self.kilos_merma / self.kilos_totales * 100) if self.kilos_totales > 0 else 0.0
