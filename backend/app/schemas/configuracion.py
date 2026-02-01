from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConfiguracionBase(BaseModel):
    """
    Base: datos comunes en todas las operaciones
    """
    clave: str
    valor: str
    descripcion: Optional[str] = None


class ConfiguracionCreate(ConfiguracionBase):
    """
    Para CREAR una configuración (POST)
    El frontend envía: clave, valor, descripcion
    """
    pass


class ConfiguracionUpdate(BaseModel):
    """
    Para ACTUALIZAR una configuración (PUT)
    Solo actualizamos valor y descripcion, la clave no cambia
    """
    valor: str
    descripcion: Optional[str] = None


class ConfiguracionResponse(ConfiguracionBase):
    """
    Para RESPONDER al frontend (GET/POST/PUT)
    Incluye el ID y los timestamps
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
