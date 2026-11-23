"""Endpoints de los indicadores de cosechas.

Cada ruta solo recibe la petición, llama al service y devuelve la respuesta JSON.
"""
from flask import Blueprint, jsonify

from app.schemas.indicador_schema import respuesta_indicador
from app.services.analytics import cosecha_service, rendimiento_service, top_cultivo_service

cosecha_bp = Blueprint("cosechas", __name__, url_prefix="/analytics/cosechas")


@cosecha_bp.route("/resumen", methods=["GET"])
def resumen():
    return jsonify(respuesta_indicador(
        "Resumen de cosechas",
        "Total de cosechas, kilos óptimos, merma y porcentaje de merma global",
        "SQL Server",
        cosecha_service.resumen_cosechas(),
    ))


@cosecha_bp.route("/por-cultivo", methods=["GET"])
def por_cultivo():
    return jsonify(respuesta_indicador(
        "Kilos cosechados por cultivo",
        "Kilos óptimos, merma, total y porcentaje de merma de cada cultivo",
        "SQL Server",
        cosecha_service.kilos_por_cultivo(),
    ))


@cosecha_bp.route("/calidad", methods=["GET"])
def calidad():
    return jsonify(respuesta_indicador(
        "Calidad de cosecha según la merma",
        "Cantidad de líneas de cosecha en cada nivel de merma (límite permitido: 20%)",
        "SQL Server",
        cosecha_service.calidad_de_cosecha(),
    ))


@cosecha_bp.route("/mensual", methods=["GET"])
def mensual():
    return jsonify(respuesta_indicador(
        "Kilos cosechados por mes",
        "Kilos totales cosechados en cada mes, en orden cronológico",
        "SQL Server",
        cosecha_service.cosechas_por_mes(),
    ))


@cosecha_bp.route("/rendimiento-parcela", methods=["GET"])
def rendimiento_parcela():
    return jsonify(respuesta_indicador(
        "Rendimiento por parcela (kg/ha)",
        "Kilos cosechados (SQL Server) entre el área de cada parcela (MongoDB)",
        "SQL Server + MongoDB",
        rendimiento_service.rendimiento_por_parcela(),
    ))


@cosecha_bp.route("/top-cultivo", methods=["GET"])
def top_cultivo_mes():
    result = top_cultivo_service.get_top_cultivo_mes()
    if not result:
        return jsonify({"message": "No se encontró información"}), 404
    return jsonify(result.__dict__)
