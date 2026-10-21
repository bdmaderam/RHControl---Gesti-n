from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class EmpleadoBase(BaseModel):
    nombres: str = Field(min_length=1, max_length=100)
    apellidos: str = Field(min_length=1, max_length=100)
    tipo_documento: str = Field(default="CC", pattern="^(CC|CE|PA)$")
    numero_documento: str = Field(min_length=1, max_length=30)
    fecha_nacimiento: date | None = None
    cargo: str = Field(default="", max_length=120)
    salario: float = Field(default=0, ge=0)
    dependencia: str = Field(default="", max_length=120)
    tiene_cuenta_bancaria: bool = False
    es_temporal: bool = False
    activo: bool = True

class EmpleadoCreate(EmpleadoBase): pass
class EmpleadoUpdate(BaseModel):
    nombres: str | None = Field(default=None, min_length=1, max_length=100)
    apellidos: str | None = Field(default=None, min_length=1, max_length=100)
    tipo_documento: str | None = Field(default=None, pattern="^(CC|CE|PA)$")
    numero_documento: str | None = Field(default=None, min_length=1, max_length=30)
    fecha_nacimiento: date | None = None
    cargo: str | None = Field(default=None, max_length=120)
    salario: float | None = Field(default=None, ge=0)
    dependencia: str | None = Field(default=None, max_length=120)
    tiene_cuenta_bancaria: bool | None = None
    es_temporal: bool | None = None
    activo: bool | None = None
class EmpleadoOut(EmpleadoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None
