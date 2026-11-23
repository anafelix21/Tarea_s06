"""Pruebas de los indicadores de cosechas (sin base de datos: el repository se reemplaza)."""
from datetime import date

import pytest

from app.models.linea_cosecha import LineaCosecha
from app.services.analytics import cosecha_service

LINEAS = [
    LineaCosecha(1, date(2026, 7, 8), "Ing. Carlos Ramos", 2, "Uva Red Globe", "PARC-NOR-001", 820, 30),
    LineaCosecha(1, date(2026, 7, 8), "Ing. Carlos Ramos", 3, "Palta Hass", "PARC-SUR-002", 610, 45),
    LineaCosecha(2, date(2026, 8, 12), "Ing. Rosa Flores", 2, "Uva Red Globe", "PARC-NOR-001", 760, 28),
    LineaCosecha(3, date(2026, 8, 27), "Ing. Diego Mendoza", 4, "Mango Kent", "PARC-CEN-063", 930, 125),
]


@pytest.fixture(autouse=True)
def datos_de_prueba(monkeypatch):
    monkeypatch.setattr(cosecha_service.cosecha_repository, "obtener_lineas_cosecha", lambda: LINEAS)


def test_resumen_suma_kilos_y_calcula_merma_global():
    r = cosecha_service.resumen_cosechas()
    assert r["total_cosechas"] == 3
    assert r["total_lineas"] == 4
    assert r["kilos_optimos"] == 3120
    assert r["kilos_merma"] == 228
    assert r["kilos_totales"] == 3348
    assert r["porcentaje_merma_global"] == round(228 / 3348 * 100, 2)


def test_por_cultivo_agrupa_y_ordena_de_mayor_a_menor():
    r = cosecha_service.kilos_por_cultivo()
    assert list(r) == ["Uva Red Globe", "Mango Kent", "Palta Hass"]
    assert r["Uva Red Globe"]["kilos_totales"] == 1638
    assert r["Mango Kent"]["porcentaje_merma"] == round(125 / 1055 * 100, 2)


@pytest.mark.parametrize("porcentaje, categoria", [
    (3.5, "Óptima (merma menor al 5%)"),
    (5.0, "Aceptable (merma entre 5% y 10%)"),
    (10.0, "Aceptable (merma entre 5% y 10%)"),
    (11.8, "Crítica (merma entre 10% y 20%)"),
    (25.0, "Fuera de norma (merma mayor al 20%)"),
])
def test_clasificar_merma(porcentaje, categoria):
    assert cosecha_service.clasificar_merma(porcentaje) == categoria


def test_calidad_cuenta_lineas_por_categoria():
    r = cosecha_service.calidad_de_cosecha()
    assert r["Óptima (merma menor al 5%)"] == 2          # 3.53% y 3.55%
    assert r["Aceptable (merma entre 5% y 10%)"] == 1    # 6.87%
    assert r["Crítica (merma entre 10% y 20%)"] == 1     # 11.85%
    assert r["Fuera de norma (merma mayor al 20%)"] == 0
    assert sum(r.values()) == len(LINEAS)


def test_mensual_agrupa_por_mes_en_orden():
    assert cosecha_service.cosechas_por_mes() == {"2026-07": 1505.0, "2026-08": 1843.0}


def test_sin_datos_no_divide_entre_cero(monkeypatch):
    monkeypatch.setattr(cosecha_service.cosecha_repository, "obtener_lineas_cosecha", lambda: [])
    r = cosecha_service.resumen_cosechas()
    assert r["total_cosechas"] == 0 and r["porcentaje_merma_global"] == 0.0 and r["promedio_kilos_por_cosecha"] == 0.0
