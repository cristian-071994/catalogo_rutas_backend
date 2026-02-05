from pydantic import BaseModel
from typing import List, Optional

from app.schemas.ruta import RutaResponse
from app.models.enums import EstadoGeneral


class ClienteBase(BaseModel):
    nombre: str


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(BaseModel):
    id: int
    nombre: str
    estado: EstadoGeneral
    empresa_id: int

    rutas: List[RutaResponse] = []

    class Config:
        from_attributes = True


class ClienteUpdate(BaseModel):
    nombre: Optional[str]

    class Config:
        from_attributes = True
