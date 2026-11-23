"""Pruebas de los endpoints: estructura de la respuesta y manejo de errores."""
import pytest

from app.main import create_app
from app.services.analytics import cosecha_service, parcela_service, rendimiento_service


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(cosecha_service, "resumen_cosechas", lambda: {"total_cosechas": 3})
    monkeypatch.setattr(cosecha_service, "kilos_por_cultivo", lambda: {"Uva": {"kilos_totales": 10}})
    monkeypatch.setattr(cosecha_service, "calidad_de_cosecha", lambda: {"Óptima (merma menor al 5%)": 1})
    monkeypatch.setattr(cosecha_service, "cosechas_por_mes", lambda: {"2026-07": 10.0})
    monkeypatch.setattr(rendimiento_service, "rendimiento_por_parcela", lambda: {"Sector Norte": {"rendimiento_kg_ha": 1.0}})
    monkeypatch.setattr(parcela_service, "parcelas_por_estado_riego", lambda: {"Completo": 2})
    return create_app().test_client()


@pytest.mark.parametrize("ruta, fuente", [
    ("/analytics/cosechas/resumen", "SQL Server"),
    ("/analytics/cosechas/por-cultivo", "SQL Server"),
    ("/analytics/cosechas/calidad", "SQL Server"),
    ("/analytics/cosechas/mensual", "SQL Server"),
    ("/analytics/cosechas/rendimiento-parcela", "SQL Server + MongoDB"),
    ("/analytics/parcelas/estado-riego", "MongoDB"),
])
def test_indicadores_responden_con_la_estructura_comun(client, ruta, fuente):
    respuesta = client.get(ruta)
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert set(cuerpo) == {"indicator", "description", "source", "data"}
    assert cuerpo["source"] == fuente and cuerpo["data"]


def test_ruta_inexistente_responde_404_en_json(client):
    respuesta = client.get("/analytics/no-existe")
    assert respuesta.status_code == 404
    assert "error" in respuesta.get_json()


def test_metodo_no_permitido_conserva_405(client):
    assert client.post("/analytics/cosechas/resumen").status_code == 405


def test_si_falla_la_base_responde_503(monkeypatch):
    def falla():
        raise ConnectionError("SQL Server no disponible")
    monkeypatch.setattr(cosecha_service, "resumen_cosechas", falla)
    respuesta = create_app().test_client().get("/analytics/cosechas/resumen")
    assert respuesta.status_code == 503
    assert respuesta.get_json()["error"] == "No se pudo calcular el indicador"


def test_swagger_disponible(client):
    assert client.get("/static/swagger.json").status_code == 200
    assert client.get("/apidocs/").status_code == 200
