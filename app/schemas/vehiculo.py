from pydantic import BaseModel
from typing import Optional
from app.models.enums import EstadoGeneral


class VehiculoBase(BaseModel):
    placa: str
    configuracion_id: int
    estado: Optional[EstadoGeneral] = EstadoGeneral.activo


class VehiculoCreate(BaseModel):
    placa: str
    configuracion_id: int


class VehiculoUpdate(BaseModel):
    placa: Optional[str] = None
    configuracion_id: Optional[int] = None
    estado: Optional[EstadoGeneral] = None


class VehiculoResponse(VehiculoBase):
    id: int

    class Config:
        from_attributes = True

