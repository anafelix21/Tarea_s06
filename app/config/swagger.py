"""Configuración de Swagger UI.

La documentación vive en app/static/swagger.json y se muestra en /apidocs.
"""
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/apidocs"
API_URL = "/static/swagger.json"

swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Backend Analítico - Cosechas y Rendimiento (Ana Félix)"},
)
