"""Endpoints de los indicadores de parcelas."""
from flask import Blueprint, jsonify

from app.schemas.indicador_schema import respuesta_indicador
from app.services.analytics import parcela_service

parcela_bp = Blueprint("parcelas", __name__, url_prefix="/analytics/parcelas")


@parcela_bp.route("/estado-riego", methods=["GET"])
def estado_riego():
    return jsonify(respuesta_indicador(
        "Parcelas por estado de riego",
        "Cantidad de parcelas activas en cada estado de riego",
        "MongoDB",
        parcela_service.parcelas_por_estado_riego(),
    ))
