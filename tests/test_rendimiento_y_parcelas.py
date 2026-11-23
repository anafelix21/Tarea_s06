"""Pruebas del indicador combinado (SQL Server + MongoDB) y del de parcelas."""
from datetime import date

from app.models.linea_cosecha import LineaCosecha
from app.models.parcela import Parcela
from app.services.analytics import parcela_service, rendimiento_service

LINEAS = [
    LineaCosecha(1, date(2026, 7, 8), "Ana", 2, "Uva", "PARC-NOR-001", 1000, 70),
    LineaCosecha(2, date(2026, 8, 8), "Ana", 2, "Uva", "PARC-NOR-001", 500, 30),
    LineaCosecha(3, date(2026, 9, 8), "Ana", 1, "Palto", "ID-SIN-PARCELA", 400, 20),
]
PARCELAS = [Parcela("PARC-NOR-001", "Sector Norte - Lote 001", 5.0, "Completo", "Franco Arenoso")]


def test_rendimiento_cruza_sql_y_mongo(monkeypatch):
    monkeypatch.setattr(rendimiento_service.cosecha_repository, "obtener_lineas_cosecha", lambda: LINEAS)
    monkeypatch.setattr(rendimiento_service.parcela_repository, "obtener_parcelas_por_ids", lambda ids: PARCELAS)
    r = rendimiento_service.rendimiento_por_parcela()
    norte = r["Sector Norte - Lote 001"]
    assert norte["kilos_totales"] == 1600
    assert norte["area_hectareas"] == 5.0
    assert norte["rendimiento_kg_ha"] == 320.0


def test_rendimiento_parcela_inexistente_no_inventa_area(monkeypatch):
    monkeypatch.setattr(rendimiento_service.cosecha_repository, "obtener_lineas_cosecha", lambda: LINEAS)
    monkeypatch.setattr(rendimiento_service.parcela_repository, "obtener_parcelas_por_ids", lambda ids: PARCELAS)
    r = rendimiento_service.rendimiento_por_parcela()
    sin = r["Parcela ID-SIN-PARCELA (no registrada en MongoDB)"]
    assert sin["kilos_totales"] == 420 and sin["area_hectareas"] is None and sin["rendimiento_kg_ha"] is None


def test_parcelas_por_estado_riego(monkeypatch):
    parcelas = [
        Parcela("P1", "A", 1, "Completo", "x"), Parcela("P2", "B", 1, "Pendiente", "x"),
        Parcela("P3", "C", 1, "Completo", "x"),
    ]
    monkeypatch.setattr(parcela_service.parcela_repository, "obtener_parcelas_activas", lambda: parcelas)
    assert parcela_service.parcelas_por_estado_riego() == {"Completo": 2, "Pendiente": 1}
