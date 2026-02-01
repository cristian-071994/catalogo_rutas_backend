from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from datetime import datetime
from app.models.enums import EstadoGeneral


class PeajeBase(BaseModel):
    """Base: datos comunes de un peaje"""
    nombre_peaje: str
    costo: Decimal
    estado: Optional[EstadoGeneral] = EstadoGeneral.activo


class PeajeCreate(BaseModel):
    """Para CREAR un peaje MANUAL (POST)"""
    nombre_peaje: str
    ubicacion: Optional[str] = None
    sector: Optional[str] = None
    costo: Decimal
    longitud: Optional[Decimal] = None
    latitud: Optional[Decimal] = None


class PeajeUpdate(BaseModel):
    """Para ACTUALIZAR un peaje (PUT)"""
    nombre_peaje: Optional[str] = None
    ubicacion: Optional[str] = None
    sector: Optional[str] = None
    costo: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    latitud: Optional[Decimal] = None
    estado: Optional[EstadoGeneral] = None


class PeajeResponse(PeajeBase):
    """Para RESPONDER un peaje (GET/POST/PUT)"""
    id: int
    ubicacion: Optional[str] = None
    sector: Optional[str] = None
    longitud: Optional[Decimal] = None
    latitud: Optional[Decimal] = None
    codigo_peaje: Optional[str] = None
    codigo_tramo: Optional[str] = None
    fuente: Optional[str] = None
    ultima_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True
