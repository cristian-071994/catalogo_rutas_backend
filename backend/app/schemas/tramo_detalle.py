from pydantic import BaseModel
from decimal import Decimal
from app.models.enums import TipoCarga, TipoTerreno


class TramoDetalleResponse(BaseModel):
    id: int
    tipo_carga: TipoCarga
    tipo_terreno: TipoTerreno
    kilometros: Decimal

    class Config:
        from_attributes = True
