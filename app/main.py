"""Punto de entrada del backend analítico.

Ejecutar:  python -m app.main   ->   http://localhost:5050/apidocs
"""
import logging

from flask import Flask, jsonify, redirect
from werkzeug.exceptions import HTTPException

from app.config.settings import settings
from app.config.swagger import SWAGGER_URL, swagger_bp
from app.database import mongodb, sqlserver
from app.routes.cosecha_routes import cosecha_bp
from app.routes.parcela_routes import parcela_bp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("backend-analitico")


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static")
    app.json.ensure_ascii = False      # tildes y ñ legibles en las respuestas JSON
    app.json.sort_keys = False         # respeta el orden calculado (por ejemplo, de mayor a menor)

    app.register_blueprint(cosecha_bp)
    app.register_blueprint(parcela_bp)
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    @app.get("/")
    def inicio():
        return redirect(SWAGGER_URL)

    @app.get("/health")
    def health():
        estado = {"sqlserver": "UP" if sqlserver.ping() else "DOWN",
                  "mongodb": "UP" if mongodb.ping() else "DOWN"}
        codigo = 200 if all(v == "UP" for v in estado.values()) else 503
        return jsonify({"status": "UP" if codigo == 200 else "DEGRADED", "databases": estado}), codigo

    @app.errorhandler(404)
    def no_encontrado(_error):
        return jsonify({"error": "El endpoint solicitado no existe"}), 404

    @app.errorhandler(Exception)
    def error_general(error):
        if isinstance(error, HTTPException):      # 404, 405, etc. conservan su código
            return jsonify({"error": error.description}), error.code
        logger.error("Error al calcular el indicador: %s", error, exc_info=True)
        return jsonify({"error": "No se pudo calcular el indicador",
                        "detail": "Verifique la conexión con SQL Server y MongoDB (GET /health)"}), 503

    return app


app = create_app()

if __name__ == "__main__":
    logger.info("%s en http://localhost:%s%s", settings.APP_NAME, settings.APP_PORT, SWAGGER_URL)
    app.run(host="0.0.0.0", port=settings.APP_PORT)
