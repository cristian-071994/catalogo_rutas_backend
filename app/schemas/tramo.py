from pydantic import BaseModel
from typing import List
from app.schemas.tramo_detalle import TramoDetalleResponse


class TramoResponse(BaseModel):
    id: int
    origen: str
    destino: str

    detalles: List[TramoDetalleResponse]

    class Config:
        from_attributes = True
