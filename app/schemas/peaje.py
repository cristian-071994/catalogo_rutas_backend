from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from app.models.enums import EstadoGeneral


class PeajeBase(BaseModel):
    """Base: datos comunes de un peaje"""
    nombre: str
    costo: Decimal
    estado: Optional[EstadoGeneral] = EstadoGeneral.activo


class PeajeCreate(BaseModel):
    """Para CREAR un peaje (POST)"""
    nombre: str
    costo: Decimal


class PeajeUpdate(BaseModel):
    """Para ACTUALIZAR un peaje (PUT)"""
    nombre: Optional[str] = None
    costo: Optional[Decimal] = None
    estado: Optional[EstadoGeneral] = None


class PeajeResponse(PeajeBase):
    """Para RESPONDER un peaje (GET/POST/PUT)"""
    id: int

    class Config:
        from_attributes = True
