from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .core.config import settings
from .db import Base, engine, SessionLocal
from .models import Empleado, Anotacion, Usuario
from .services.auth import hash_password
from .api import empleados, anotaciones, auth, ia as ia_api
from .metrics import EMPLEADOS_ACTIVOS, MetricsMiddleware, respuesta_metricas
from .services import revisor

app = FastAPI(title="RHControl API", version="2.0.0", description="API REST para gestión de recursos humanos")
origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(MetricsMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(empleados.router); app.include_router(anotaciones.router); app.include_router(ia_api.router)

@app.get("/api/salud", tags=["Sistema"])
def salud():
    """Liveness probe de Kubernetes: el proceso responde."""
    return {"estado":"ok","servicio":"RHControl API"}

@app.get("/api/listo", tags=["Sistema"])
def listo():
    """Readiness probe de Kubernetes: además del proceso, la base de datos responde."""
    try:
        with engine.connect() as con: con.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")
    return {"estado":"listo","reglas_ia":len(revisor.REGLAS)}

@app.get("/metrics", include_in_schema=False)
def metrics():
    """Métricas en formato Prometheus. Va fuera de /api para que el Ingress no la publique."""
    try:
        with SessionLocal() as db:
            EMPLEADOS_ACTIVOS.set(db.query(Empleado).filter(Empleado.activo.is_(True)).count())
    except Exception:
        pass  # si la BD falla, igual se exponen las demás métricas
    return respuesta_metricas()

LOCK_ARRANQUE = 727272  # id del advisory lock de PostgreSQL

@app.on_event("startup")
def startup():
    # Con 2 o más réplicas arrancando a la vez, solo una crea tablas y datos iniciales (lock de PostgreSQL).
    with engine.connect() as lock_conn:
        es_pg = engine.dialect.name == "postgresql"
        if es_pg: lock_conn.execute(text("SELECT pg_advisory_lock(:k)"), {"k": LOCK_ARRANQUE})
        try: inicializar_datos()
        finally:
            if es_pg: lock_conn.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": LOCK_ARRANQUE})
            lock_conn.commit()

def inicializar_datos():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    try:
        if not db.query(Usuario).filter(Usuario.usuario=="admin").first():
            db.add(Usuario(usuario="admin", nombre="Administrador RH", password_hash=hash_password(settings.admin_password)))
        if db.query(Empleado).count()==0:
            e1=Empleado(nombres="Juan", apellidos="Pérez", tipo_documento="CC", numero_documento="123456789", cargo="Desarrollador", salario=5000000, dependencia="Tecnología", tiene_cuenta_bancaria=True, activo=True)
            e2=Empleado(nombres="María", apellidos="Gómez", tipo_documento="CC", numero_documento="987654321", cargo="Diseñadora", salario=4500000, dependencia="Marketing", tiene_cuenta_bancaria=True, activo=True)
            e3=Empleado(nombres="Carlos", apellidos="Rodríguez", tipo_documento="CC", numero_documento="456789123", cargo="Gerente", salario=8000000, dependencia="Administración", activo=False)
            db.add_all([e1,e2,e3]); db.flush()
            db.add_all([Anotacion(empleado_id=e1.id,tipo="Felicitación",descripcion="Excelente desempeño en el proyecto de transformación digital."), Anotacion(empleado_id=e1.id,tipo="Observación",descripcion="Realizar seguimiento a documentación técnica."), Anotacion(empleado_id=e2.id,tipo="Reconocimiento",descripcion="Reconocimiento por cumplimiento de objetivos del trimestre.")])
        db.commit()
    finally: db.close()
