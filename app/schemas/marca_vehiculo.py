from pydantic import BaseModel
from typing import Optional
from app.models.enums import EstadoGeneral


class MarcaVehiculoBase(BaseModel):
    nombre: str
    estado: Optional[EstadoGeneral] = EstadoGeneral.activo


class MarcaVehiculoCreate(MarcaVehiculoBase):
    pass


class MarcaVehiculoResponse(MarcaVehiculoBase):
    id: int

    class Config:
        from_attributes = True
