from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from app.models.enums import TipoCarga, TipoTerreno, EstadoGeneral


class RendimientoConfiguracionBase(BaseModel):
    configuracion_id: int
    tipo_carga: TipoCarga
    tipo_terreno: TipoTerreno
    rendimiento_km_galon: Decimal
    estado: Optional[EstadoGeneral] = EstadoGeneral.activo


class RendimientoConfiguracionCreate(RendimientoConfiguracionBase):
    pass


class RendimientoConfiguracionUpdate(BaseModel):
    rendimiento_km_galon: Optional[Decimal] = None
    estado: Optional[EstadoGeneral] = None


class RendimientoConfiguracionResponse(RendimientoConfiguracionBase):
    id: int

    class Config:
        from_attributes = True

