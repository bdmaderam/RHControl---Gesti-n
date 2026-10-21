from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Anotacion, Empleado
from ..schemas.anotaciones import AnotacionCreate, AnotacionOut, AnotacionUpdate
from ..services.auth import get_current_user

router = APIRouter(prefix="/api/anotaciones", tags=["Anotaciones"], dependencies=[Depends(get_current_user)])

def get_anotacion(db, anotacion_id):
    obj=db.get(Anotacion, anotacion_id)
    if not obj: raise HTTPException(status_code=404, detail="Anotación no encontrada")
    return obj

def get_empleado(db, empleado_id):
    obj=db.get(Empleado, empleado_id)
    if not obj: raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return obj

@router.get("", response_model=list[AnotacionOut])
def listar(db: Session = Depends(get_db)):
    return db.query(Anotacion).order_by(Anotacion.fecha.desc(), Anotacion.id.desc()).all()

@router.get("/empleado/{empleado_id}", response_model=list[AnotacionOut])
def listar_por_empleado(empleado_id: int, db: Session = Depends(get_db)):
    get_empleado(db, empleado_id)
    return db.query(Anotacion).filter(Anotacion.empleado_id == empleado_id).order_by(Anotacion.fecha.desc()).all()

@router.post("/empleado/{empleado_id}", response_model=AnotacionOut, status_code=status.HTTP_201_CREATED)
def crear(empleado_id: int, payload: AnotacionCreate, db: Session = Depends(get_db)):
    get_empleado(db, empleado_id)
    obj=Anotacion(empleado_id=empleado_id, **payload.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj

@router.put("/{anotacion_id}", response_model=AnotacionOut)
def actualizar(anotacion_id: int, payload: AnotacionUpdate, db: Session = Depends(get_db)):
    obj=get_anotacion(db, anotacion_id)
    for k,v in payload.model_dump(exclude_unset=True).items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{anotacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(anotacion_id: int, db: Session = Depends(get_db)):
    obj=get_anotacion(db, anotacion_id); db.delete(obj); db.commit()
