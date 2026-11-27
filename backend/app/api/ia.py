from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Anotacion, Empleado
from ..services import revisor, temas
from ..services.auth import get_current_user

# Todo el router exige JWT: el revisor nunca queda expuesto sin autenticación.
router = APIRouter(prefix="/api/ia", tags=["Inteligencia artificial"], dependencies=[Depends(get_current_user)])


class RevisarRequest(BaseModel):
    descripcion: str = Field(min_length=1, max_length=2000)
    tipo: Optional[str] = Field(default=None, max_length=40)
    fecha: Optional[date] = None
    empleado_id: Optional[int] = Field(default=None, ge=1, description="Activa las reglas de historial")
    anotacion_id: Optional[int] = Field(default=None, ge=1, description="Al editar, excluye la propia anotación")


def _historial(db: Session, empleado_id: int | None) -> list[revisor.Previa]:
    if not empleado_id:
        return []
    filas = db.query(Anotacion).filter(Anotacion.empleado_id == empleado_id).all()
    return [revisor.Previa(a.id, revisor.clave_tipo(a.tipo), a.fecha, a.descripcion) for a in filas]


@router.post("/revisar-anotacion")
def revisar_anotacion(payload: RevisarRequest, db: Session = Depends(get_db)):
    """Revisa la calidad de una anotación antes de guardarla: puntaje, problemas y cómo corregirlos."""
    if not payload.descripcion.strip():
        raise HTTPException(status_code=422, detail="La descripción no puede estar vacía")
    historial = _historial(db, payload.empleado_id)
    resultado = revisor.revisar(
        payload.descripcion, payload.tipo, payload.fecha, historial=historial, anotacion_id=payload.anotacion_id)
    resultado.update(temas.analizar(
        payload.descripcion, payload.tipo, payload.fecha, historial, anotacion_id=payload.anotacion_id))
    return resultado


@router.get("/auditoria-anotaciones")
def auditoria_anotaciones(
    nivel_maximo: int = Query(70, ge=0, le=100, description="Lista las anotaciones con puntaje igual o menor"),
    db: Session = Depends(get_db),
):
    """Revisa TODAS las anotaciones guardadas y lista las de menor calidad (para corregirlas)."""
    todas = db.query(Anotacion).all()
    por_empleado: dict[int, list[revisor.Previa]] = {}
    for a in todas:
        por_empleado.setdefault(a.empleado_id, []).append(
            revisor.Previa(a.id, revisor.clave_tipo(a.tipo), a.fecha, a.descripcion))
    hallazgos = []
    for a in todas:
        r = revisor.revisar(a.descripcion, a.tipo, a.fecha, historial=por_empleado[a.empleado_id],
                            anotacion_id=a.id, registrar_metricas=False)
        if r["puntaje"] <= nivel_maximo:
            hallazgos.append({
                "anotacion_id": a.id, "empleado_id": a.empleado_id, "tipo": a.tipo, "puntaje": r["puntaje"],
                "nivel": r["etiqueta"], "problemas": [h["mensaje"] for h in r["hallazgos"] if h["severidad"] != "info"],
                "descripcion": a.descripcion,
            })
    hallazgos.sort(key=lambda h: h["puntaje"])
    return {"revisadas": len(todas), "nivel_maximo": nivel_maximo, "anotaciones": hallazgos}


@router.get("/reglas")
def reglas():
    """La base de conocimiento: todas las reglas que aplica el revisor."""
    return {"total": len(revisor.REGLAS), "reglas": revisor.catalogo()}


@router.get("/temas-empleado/{empleado_id}")
def temas_empleado(empleado_id: int, dias: int = Query(90, ge=7, le=730), db: Session = Depends(get_db)):
    """Temas que aparecen en las anotaciones de un empleado y alertas de reincidencia (tema negativo repetido)."""
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return {"empleado_id": empleado_id, **temas.perfil_empleado(_historial(db, empleado_id), dias=dias)}


@router.get("/reincidencias")
def reincidencias(
    dias: int = Query(90, ge=7, le=730, description="Ventana de tiempo en días"),
    minimo: int = Query(2, ge=2, le=10, description="Repeticiones mínimas para alertar"),
    db: Session = Depends(get_db),
):
    """Empleados que repiten un mismo tema negativo dentro de la ventana de tiempo (los más graves primero)."""
    por_empleado: dict[int, list[revisor.Previa]] = {}
    for a in db.query(Anotacion).all():
        por_empleado.setdefault(a.empleado_id, []).append(
            revisor.Previa(a.id, revisor.clave_tipo(a.tipo), a.fecha, a.descripcion))
    nombres = {e.id: f"{e.nombres} {e.apellidos}" for e in db.query(Empleado).all()}
    resultado = []
    for emp_id, historial in por_empleado.items():
        alertas = temas.perfil_empleado(historial, dias=dias, minimo=minimo)["alertas"]
        if alertas:
            resultado.append({"empleado_id": emp_id, "empleado": nombres.get(emp_id, f"#{emp_id}"), "alertas": alertas})
    resultado.sort(key=lambda r: -max(a["ocurrencias"] for a in r["alertas"]))
    return {"ventana_dias": dias, "minimo": minimo, "empleados": resultado}
