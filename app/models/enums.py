from enum import Enum


class EstadoGeneral(str, Enum):
    activo = "activo"
    inactivo = "inactivo"


class TipoCarga(str, Enum):
    VACIO = "VACIO"
    CARGADO = "CARGADO"


class TipoTerreno(str, Enum):
    PLANO = "PLANO"
    ONDULADO = "ONDULADO"
    MONTAÑA = "MONTAÑA"
    URBANO = "URBANO"


class DireccionPeaje(str, Enum):
    """Para diferenciar si el peaje es en ida o regreso"""
    IDA = "IDA"
    REGRESO = "REGRESO"

