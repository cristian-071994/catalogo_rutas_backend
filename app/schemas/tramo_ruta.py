from pydantic import BaseModel
from app.schemas.tramo import TramoResponse


class TramoRutaBase(BaseModel):
    orden: int
    tramo_id: int


class TramoRutaCreate(TramoRutaBase):
    pass


class TramoRutaResponse(BaseModel):
    id: int
    orden: int
    tramo: TramoResponse

    class Config:
        from_attributes = True
