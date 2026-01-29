from pydantic import BaseModel
from typing import Optional, List
from app.schemas.tramo_ruta import TramoRutaResponse
from app.models.enums import EstadoGeneral


class RutaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RutaCreate(RutaBase):
    cliente_id: int


class RutaUpdate(BaseModel):
    """Para actualizar una ruta"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[EstadoGeneral] = None


class RutaResponse(RutaBase):
    id: int
    cliente_id: int
    estado: EstadoGeneral

    tramos: List[TramoRutaResponse]

    class Config:
        from_attributes = True

