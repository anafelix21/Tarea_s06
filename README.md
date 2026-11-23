# Backend Analítico — Cosechas y Rendimiento (AgroPacayales S.A.C.)

**Autora:** Ana Félix · **Tecnología:** Python + Flask · **Bases de datos:** SQL Server y MongoDB

Backend analítico organizado por capas según el estándar del curso: cada capa tiene una sola responsabilidad y el flujo siempre es **Route → Service → Repository → Database**. Calcula los indicadores del módulo de **Cosechas y Rendimiento**.

## 1. Estructura del proyecto

```text
Tarea_s06/
├── app/
│   ├── config/
│   │   ├── settings.py              # Variables de entorno (.env)
│   │   └── swagger.py               # Swagger UI en /apidocs
│   ├── database/
│   │   ├── sqlserver.py             # Conexión a SQL Server (pymssql)
│   │   └── mongodb.py               # Conexión a MongoDB (pymongo)
│   ├── models/
│   │   ├── linea_cosecha.py         # Un cultivo dentro de una cosecha
│   │   └── parcela.py               # Una parcela agrícola
│   ├── repositories/
│   │   ├── sqlserver/
│   │   │   └── cosecha_repository.py    # Consulta harvest + harvest_planting_cycle + cultivos
│   │   └── mongodb/
│   │       └── parcela_repository.py    # Consulta la colección plots
│   ├── services/
│   │   └── analytics/
│   │       ├── cosecha_service.py       # Resumen, por cultivo, calidad y mensual
│   │       ├── parcela_service.py       # Parcelas por estado de riego
│   │       ├── rendimiento_service.py   # Rendimiento kg/ha (SQL Server + MongoDB)
│   │       └── top_cultivo_service.py   # Cultivo más cosechado del mes (SQL Server + MongoDB)
│   ├── routes/
│   │   ├── cosecha_routes.py        # /analytics/cosechas/...
│   │   └── parcela_routes.py        # /analytics/parcelas/...
│   ├── schemas/
│   │   ├── indicador_schema.py      # Estructura común de la respuesta
│   │   └── analytics_schema.py      # IndicatorResponse (indicador integrado)
│   ├── static/
│   │   └── swagger.json             # Documentación OpenAPI
│   └── main.py                      # Crea la app, registra rutas, /health y errores
├── tests/                           # 28 pruebas con pytest
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 2. Responsabilidad de cada capa

| Capa | Archivo | Qué hace | Qué NO hace |
| :-- | :-- | :-- | :-- |
| **Route** | `routes/cosecha_routes.py` | Recibe la petición, llama al service y devuelve JSON | No consulta la base ni calcula |
| **Service** | `services/analytics/cosecha_service.py` | Suma, agrupa, clasifica y calcula porcentajes | No escribe SQL ni consultas Mongo |
| **Repository** | `repositories/sqlserver/cosecha_repository.py` | Ejecuta la consulta y devuelve modelos | No calcula indicadores |
| **Database** | `database/sqlserver.py` | Abre y cierra la conexión | No sabe qué se consulta |

## 3. Indicadores

| Endpoint | Indicador | Fuente | Cálculo en el service |
| :-- | :-- | :-- | :-- |
| `GET /analytics/cosechas/top-cultivo` | **Cultivo más cosechado del mes** (integrado) | **SQL Server + MongoDB** | SQL Server da el cultivo con más kilos del último mes; MongoDB da los datos de su parcela |
| `GET /analytics/cosechas/resumen` | Resumen de cosechas | SQL Server | Total de cosechas, kilos óptimos, merma, total, % de merma global y promedio por cosecha |
| `GET /analytics/cosechas/por-cultivo` | Kilos por cultivo | SQL Server | Agrupación por cultivo, ordenada de mayor a menor, con % de merma |
| `GET /analytics/cosechas/calidad` | Calidad según la merma | SQL Server | Clasificación de cada línea: óptima (< 5%), aceptable (5–10%), crítica (10–20%), fuera de norma (> 20%) |
| `GET /analytics/cosechas/mensual` | Kilos por mes | SQL Server | Agrupación por mes (yyyy-MM) en orden cronológico |
| `GET /analytics/cosechas/rendimiento-parcela` | Rendimiento kg/ha | **SQL Server + MongoDB** | Kilos de cada parcela (SQL) entre su área en hectáreas (MongoDB) |
| `GET /analytics/parcelas/estado-riego` | Parcelas por estado de riego | MongoDB | Conteo de parcelas activas por estado de riego |
| `GET /health` | Estado de las conexiones | Ambas | `UP` / `DOWN` de cada base de datos |

### Ejemplo de flujo

```text
GET /analytics/cosechas/calidad
        ↓
routes/cosecha_routes.py          → calidad()
        ↓
services/analytics/cosecha_service.py   → calidad_de_cosecha()  (clasifica cada línea por su % de merma)
        ↓
repositories/sqlserver/cosecha_repository.py → obtener_lineas_cosecha()
        ↓
database/sqlserver.py             → get_connection()  →  SQL Server
```

### Ejemplo de respuesta

```json
{
  "indicator": "Calidad de cosecha según la merma",
  "description": "Cantidad de líneas de cosecha en cada nivel de merma (límite permitido: 20%)",
  "source": "SQL Server",
  "data": {
    "Óptima (merma menor al 5%)": 14,
    "Aceptable (merma entre 5% y 10%)": 9,
    "Crítica (merma entre 10% y 20%)": 1,
    "Fuera de norma (merma mayor al 20%)": 0
  }
}
```

### Indicador integrado: cultivo más cosechado del mes

Construido según la guía del indicador integrado MongoDB + SQL Server (producto → cultivo, ventas → cosechas, productos → parcelas):

| Paso | Archivo | Qué hace |
| :-- | :-- | :-- |
| 1 | `repositories/sqlserver/cosecha_repository.py` → `obtener_top_cultivo_mes()` | `SELECT TOP 1` del cultivo con más kilos en el último mes con cosechas. SQL Server solo sabe: *"el cultivo 4 de la parcela PARC-CEN-063 cosechó 925 kg"* |
| 2 | `repositories/mongodb/parcela_repository.py` → `obtener_parcela_por_id()` | `find_one` de la parcela en la colección `plots` |
| 3 | `schemas/analytics_schema.py` → `IndicatorResponse` | Estructura estándar: `indicator`, `title`, `chart_type`, `data`, `sources` |
| 4 | `services/analytics/top_cultivo_service.py` → `get_top_cultivo_mes()` | Integra las dos fuentes y devuelve el `IndicatorResponse` |
| 5 | `routes/cosecha_routes.py` → `GET /analytics/cosechas/top-cultivo` | Devuelve `result.__dict__`, o 404 `{"message": "No se encontró información"}` |
| 6 | `static/swagger.json` | Documentado en la etiqueta **Integrado** |

```json
{
  "indicator": "top_cultivo_month",
  "title": "Cultivo más cosechado del mes",
  "chart_type": "card",
  "data": {
    "mes": "2026-11", "id_cultivo": 4, "cultivo": "Mango Kent - Lote 03", "kilos": 925.0,
    "id_parcela": "PARC-CEN-063", "parcela": "Sector Central - Lote 063",
    "tipo_suelo": "Franco Limoso", "area_hectareas": 7.05, "estado_riego": "Completo"
  },
  "sources": ["SQL Server", "MongoDB"]
}
```

## 4. Configuración (.env)

Las credenciales no están en el código. Copiar `.env.example` como `.env` y completar:

```env
APP_PORT=5050
MONGO_URI=mongodb://127.0.0.1:27017
MONGO_DB=agropacayales_db
SQL_SERVER=localhost
SQL_PORT=1433
SQL_DATABASE=agropacayales_db
SQL_USER=<usuario>
SQL_PASSWORD=<contraseña>
```

El archivo `.env` está en `.gitignore` y **no** se sube al repositorio.

## 5. Ejecución

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

- Swagger: **http://localhost:5050/apidocs**
- Estado de las bases: **http://localhost:5050/health**

## 6. Pruebas

```bash
python -m pytest -v
```

28 pruebas sin base de datos (el repository se reemplaza por datos de ejemplo): cálculos de cada indicador, clasificación de la merma, cruce SQL Server + MongoDB (rendimiento y cultivo más cosechado), estructura de las respuestas, errores 404, 405 y 503, y disponibilidad de Swagger.

## 7. Buenas prácticas aplicadas

- Una responsabilidad por capa: las rutas no consultan ni calculan, y los repositories no calculan.
- Consultas de SQL Server en `repositories/sqlserver` y de MongoDB en `repositories/mongodb`.
- Conexiones centralizadas en `database/`; la de SQL Server se cierra siempre (`contextmanager`).
- Credenciales en `.env`, con `.env.example` como referencia.
- Respuesta con una estructura común (`schemas/indicador_schema.py`).
- Errores en JSON: 404 si la ruta no existe y 503 si una base de datos no responde.
- Si una parcela no existe en MongoDB, el indicador lo informa y no inventa su área.
