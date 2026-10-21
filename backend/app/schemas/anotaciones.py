from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class AnotacionBase(BaseModel):
    tipo: str = Field(default="Llamado de atención", max_length=40)
    descripcion: str = Field(min_length=1, max_length=2000)
    fecha: date = Field(default_factory=date.today)
class AnotacionCreate(AnotacionBase): pass
class AnotacionUpdate(BaseModel):
    tipo: str | None = Field(default=None, max_length=40)
    descripcion: str | None = Field(default=None, min_length=1, max_length=2000)
    fecha: date | None = None
class AnotacionOut(AnotacionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None
