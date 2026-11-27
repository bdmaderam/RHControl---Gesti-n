"""Métricas Prometheus de RHControl.

Se exponen en GET /metrics (fuera del prefijo /api, así el Ingress no las publica).
Cada pod mantiene sus propios contadores; Prometheus los suma con sum(...) en las consultas.
El backend corre con un solo worker de uvicorn por pod, por eso la memoria del proceso basta.
"""
import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# --- Métricas HTTP (las mismas del taller de monitoreo) ---
REQUESTS = Counter("http_requests_total", "Total de requests HTTP", ["method", "endpoint", "status"])
LATENCY = Histogram(
    "http_request_duration_seconds", "Latencia de las requests en segundos", ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
IN_PROGRESS = Gauge("http_requests_in_progress", "Requests que se están atendiendo ahora")

# --- Métrica de negocio (gauge que se actualiza en cada scrape) ---
EMPLEADOS_ACTIVOS = Gauge("rhcontrol_empleados_activos", "Empleados activos registrados en la base de datos")

# --- Métricas del revisor de anotaciones (sistema experto basado en reglas) ---
IA_REVISIONES = Counter("ia_revisiones_total", "Revisiones de anotaciones realizadas", ["nivel"])
IA_HALLAZGOS = Counter("ia_hallazgos_total", "Hallazgos detectados por regla", ["regla", "severidad"])
IA_PUNTAJE = Histogram(
    "ia_puntaje_calidad", "Puntaje de calidad (0-100) de las anotaciones revisadas",
    buckets=(20, 40, 60, 70, 80, 85, 90, 95, 100),
)
IA_DURACION = Histogram(
    "ia_revision_duracion_seconds", "Tiempo de cada revisión",
    buckets=(0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25),
)
IA_TEMAS = Counter("ia_temas_detectados_total", "Temas detectados en anotaciones", ["tema", "tono"])
IA_REINCIDENCIAS = Counter("ia_reincidencias_total", "Alertas de reincidencia emitidas", ["tema", "nivel"])
IA_REGLAS_CARGADAS = Gauge("ia_reglas_cargadas", "Reglas cargadas en la base de conocimiento del revisor")

# Rutas que no se miden: el scrape y las probes de Kubernetes ensuciarían el throughput real.
RUTAS_EXCLUIDAS = {"/metrics", "/api/salud", "/api/listo"}


def etiqueta_endpoint(request: Request) -> str:
    """Usa la ruta definida (/api/empleados/{empleado_id}) y no la URL real, para no crear
    una serie nueva por cada id y mantener baja la cardinalidad."""
    ruta = request.scope.get("route")
    return getattr(ruta, "path", None) or "no_encontrado"


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in RUTAS_EXCLUIDAS:
            return await call_next(request)
        inicio = time.perf_counter()
        IN_PROGRESS.inc()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            IN_PROGRESS.dec()
            endpoint = etiqueta_endpoint(request)
            LATENCY.labels(request.method, endpoint).observe(time.perf_counter() - inicio)
            REQUESTS.labels(request.method, endpoint, str(status)).inc()


def respuesta_metricas() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
