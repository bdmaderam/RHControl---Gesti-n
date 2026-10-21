from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .core.config import settings
from .db import Base, engine, SessionLocal
from .models import Empleado, Anotacion, Usuario
from .services.auth import hash_password
from .api import empleados, anotaciones, auth

app = FastAPI(title="RHControl API", version="2.0.0", description="API REST para gestión de recursos humanos")
origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(empleados.router); app.include_router(anotaciones.router)

@app.get("/api/salud", tags=["Sistema"])
def salud(): return {"estado":"ok","servicio":"RHControl API"}

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    try:
        if not db.query(Usuario).filter(Usuario.usuario=="admin").first():
            db.add(Usuario(usuario="admin", nombre="Administrador RH", password_hash=hash_password("admin123")))
        if db.query(Empleado).count()==0:
            e1=Empleado(nombres="Juan", apellidos="Pérez", tipo_documento="CC", numero_documento="123456789", cargo="Desarrollador", salario=5000000, dependencia="Tecnología", tiene_cuenta_bancaria=True, activo=True)
            e2=Empleado(nombres="María", apellidos="Gómez", tipo_documento="CC", numero_documento="987654321", cargo="Diseñadora", salario=4500000, dependencia="Marketing", tiene_cuenta_bancaria=True, activo=True)
            e3=Empleado(nombres="Carlos", apellidos="Rodríguez", tipo_documento="CC", numero_documento="456789123", cargo="Gerente", salario=8000000, dependencia="Administración", activo=False)
            db.add_all([e1,e2,e3]); db.flush()
            db.add_all([Anotacion(empleado_id=e1.id,tipo="Felicitación",descripcion="Excelente desempeño en el proyecto de transformación digital."), Anotacion(empleado_id=e1.id,tipo="Observación",descripcion="Realizar seguimiento a documentación técnica."), Anotacion(empleado_id=e2.id,tipo="Reconocimiento",descripcion="Reconocimiento por cumplimiento de objetivos del trimestre.")])
        db.commit()
    finally: db.close()
