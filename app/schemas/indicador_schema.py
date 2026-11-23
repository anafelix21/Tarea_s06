"""Estructura común de la respuesta de un indicador.

{
    "indicator": "nombre del indicador",
    "description": "qué mide",
    "source": "de qué base de datos sale",
    "data": { ... resultado ... }
}
"""


def respuesta_indicador(indicador: str, descripcion: str, fuente: str, data) -> dict:
    if not indicador or not descripcion or not fuente:
        raise ValueError("indicator, description y source son obligatorios")
    return {"indicator": indicador, "description": descripcion, "source": fuente, "data": data}
