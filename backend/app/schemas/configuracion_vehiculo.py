from pydantic import BaseModel
from typing import Optional
from app.models.enums import EstadoGeneral


class ConfiguracionVehiculoBase(BaseModel):
    marca_id: int
    modelo: int
    estado: Optional[EstadoGeneral] = EstadoGeneral.activo


class ConfiguracionVehiculoCreate(ConfiguracionVehiculoBase):
    pass


class ConfiguracionVehiculoUpdate(BaseModel):
    marca_id: Optional[int] = None
    modelo: Optional[int] = None
    estado: Optional[EstadoGeneral] = None


class ConfiguracionVehiculoResponse(ConfiguracionVehiculoBase):
    id: int

    class Config:
        from_attributes = True

