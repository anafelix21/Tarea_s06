"""Pruebas del indicador integrado: cultivo más cosechado del mes (SQL Server + MongoDB)."""
from app.main import create_app
from app.schemas.analytics_schema import IndicatorResponse
from app.services.analytics import top_cultivo_service

COSECHA = {"mes": "2026-11", "id_cultivo": 4, "cultivo": "Mango Kent - Lote 03",
           "id_parcela": "PARC-CEN-063", "kilos": 925.0}
PARCELA = {"_id": "PARC-CEN-063", "nombre": "Sector Central - Lote 063", "tipo_suelo": "Franco Limoso",
           "area_hectareas": 7.05, "estado_riego": "Completo"}


def _simular(monkeypatch, cosecha, parcela):
    monkeypatch.setattr(top_cultivo_service.cosecha_repository, "obtener_top_cultivo_mes", lambda: cosecha)
    monkeypatch.setattr(top_cultivo_service.parcela_repository, "obtener_parcela_por_id", lambda _id: parcela)


def test_integra_sql_server_y_mongodb(monkeypatch):
    _simular(monkeypatch, COSECHA, PARCELA)
    r = top_cultivo_service.get_top_cultivo_mes()
    assert isinstance(r, IndicatorResponse)
    assert r.chart_type == "card" and r.sources == ["SQL Server", "MongoDB"]
    assert r.data["kilos"] == 925.0 and r.data["parcela"] == "Sector Central - Lote 063"


def test_sin_cosechas_devuelve_none(monkeypatch):
    _simular(monkeypatch, None, PARCELA)
    assert top_cultivo_service.get_top_cultivo_mes() is None


def test_parcela_inexistente_en_mongodb_devuelve_none(monkeypatch):
    _simular(monkeypatch, COSECHA, None)
    assert top_cultivo_service.get_top_cultivo_mes() is None


def test_endpoint_responde_200_con_estructura_estandar(monkeypatch):
    _simular(monkeypatch, COSECHA, PARCELA)
    cuerpo = create_app().test_client().get("/analytics/cosechas/top-cultivo").get_json()
    assert set(cuerpo) == {"indicator", "title", "chart_type", "data", "sources"}


def test_endpoint_responde_404_sin_informacion(monkeypatch):
    _simular(monkeypatch, None, None)
    r = create_app().test_client().get("/analytics/cosechas/top-cultivo")
    assert r.status_code == 404 and r.get_json() == {"message": "No se encontró información"}
