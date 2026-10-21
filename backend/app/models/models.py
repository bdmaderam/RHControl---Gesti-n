from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import Base

class Empleado(Base):
    __tablename__ = "empleados"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(2), nullable=False, default="CC")
    numero_documento: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    cargo: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    salario: Mapped[float] = mapped_column(Numeric(14,2), nullable=False, default=0)
    dependencia: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    tiene_cuenta_bancaria: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    es_temporal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    anotaciones: Mapped[list["Anotacion"]] = relationship(back_populates="empleado", cascade="all, delete-orphan")

class Anotacion(Base):
    __tablename__ = "anotaciones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False, default="Llamado de atención")
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    empleado: Mapped[Empleado] = relationship(back_populates="anotaciones")

class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
