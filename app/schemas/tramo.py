from pydantic import BaseModel
from typing import List, Optional
from app.schemas.tramo_detalle import TramoDetalleResponse
from app.schemas.peaje import PeajeResponse


class TramoCreate(BaseModel):
    """Schema para crear un tramo con opción de asociar peajes"""
    origen: str
    destino: str
    peaje_ids: Optional[List[int]] = None  # IDs de peajes a asociar


class TramoUpdate(BaseModel):
    """Schema para actualizar un tramo"""
    origen: Optional[str] = None
    destino: Optional[str] = None


class TramoResponse(BaseModel):
    """Schema de respuesta de tramo con detalles y peajes"""
    id: int
    origen: str
    destino: str
    detalles: List[TramoDetalleResponse]
    peajes_list: List[PeajeResponse] = []  # Peajes asociados a este tramo

    class Config:
        from_attributes = True
        # Permite usar propiedades del modelo
        allow_population_by_field_name = True
