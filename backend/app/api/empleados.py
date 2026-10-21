from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Empleado
from ..schemas.empleados import EmpleadoCreate, EmpleadoOut, EmpleadoUpdate

router = APIRouter(prefix="/api/empleados", tags=["Empleados"])

def get_empleado(db, empleado_id):
    empleado = db.get(Empleado, empleado_id)
    if not empleado: raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@router.get("", response_model=list[EmpleadoOut])
def listar(documento: str = Query(""), nombre: str = Query(""), activos: bool | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(Empleado)
    if documento: q = q.filter(Empleado.numero_documento.ilike(f"%{documento}%"))
    if nombre: q = q.filter(or_(Empleado.nombres.ilike(f"%{nombre}%"), Empleado.apellidos.ilike(f"%{nombre}%")))
    if activos is not None: q = q.filter(Empleado.activo == activos)
    return q.order_by(Empleado.id.desc()).all()

@router.get("/{empleado_id}", response_model=EmpleadoOut)
def obtener(empleado_id: int, db: Session = Depends(get_db)): return get_empleado(db, empleado_id)

@router.post("", response_model=EmpleadoOut, status_code=status.HTTP_201_CREATED)
def crear(payload: EmpleadoCreate, db: Session = Depends(get_db)):
    if db.query(Empleado).filter(Empleado.numero_documento == payload.numero_documento).first():
        raise HTTPException(status_code=409, detail="Ya existe un empleado con ese documento")
    empleado = Empleado(**payload.model_dump())
    db.add(empleado); db.commit(); db.refresh(empleado); return empleado

@router.put("/{empleado_id}", response_model=EmpleadoOut)
def actualizar(empleado_id: int, payload: EmpleadoUpdate, db: Session = Depends(get_db)):
    empleado = get_empleado(db, empleado_id)
    data = payload.model_dump(exclude_unset=True)
    if "numero_documento" in data:
        dup = db.query(Empleado).filter(Empleado.numero_documento == data["numero_documento"], Empleado.id != empleado_id).first()
        if dup: raise HTTPException(status_code=409, detail="Ya existe un empleado con ese documento")
    for k,v in data.items(): setattr(empleado,k,v)
    db.commit(); db.refresh(empleado); return empleado

@router.delete("/{empleado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(empleado_id: int, db: Session = Depends(get_db)):
    empleado = get_empleado(db, empleado_id); db.delete(empleado); db.commit()
