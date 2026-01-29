from pydantic import BaseModel
from app.models.enums import DireccionPeaje


class RutaPeajeBase(BaseModel):
    """Base para ruta_peaje"""
    orden: int = None
    direccion: DireccionPeaje = DireccionPeaje.IDA


class RutaPeajeCreate(BaseModel):
    """Para CREAR un ruta_peaje (POST)"""
    orden: int = None
    direccion: DireccionPeaje = DireccionPeaje.IDA


class RutaPeajeResponse(RutaPeajeBase):
    """Para RESPONDER un ruta_peaje"""
    id: int
    ruta_id: int
    peaje_id: int

    class Config:
        from_attributes = True
