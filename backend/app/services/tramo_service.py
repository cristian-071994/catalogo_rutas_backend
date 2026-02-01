from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.tramo import Tramo
from app.models.tramo_detalle import TramoDetalle
from app.models.enums import TipoCarga, TipoTerreno, EstadoGeneral


def crear_tramo(
    db: Session,
    origen: str,
    destino: str
) -> Tramo:
    # Validar que no exista
    existente = db.query(Tramo).filter(
        and_(
            Tramo.origen == origen,
            Tramo.destino == destino,
            Tramo.estado == EstadoGeneral.activo
        )
    ).first()

    if existente:
        return existente  # reutilizamos

    tramo = Tramo(
        origen=origen,
        destino=destino
    )

    db.add(tramo)
    db.commit()
    db.refresh(tramo)

    return tramo


def crear_tramo_detalle(
    db: Session,
    tramo_id: int,
    tipo_carga: TipoCarga,
    tipo_terreno: TipoTerreno,
    kilometros: float
) -> TramoDetalle:
    existente = db.query(TramoDetalle).filter(
        and_(
            TramoDetalle.tramo_id == tramo_id,
            TramoDetalle.tipo_carga == tipo_carga,
            TramoDetalle.tipo_terreno == tipo_terreno,
            TramoDetalle.estado == EstadoGeneral.activo
        )
    ).first()

    if existente:
        return existente

    detalle = TramoDetalle(
        tramo_id=tramo_id,
        tipo_carga=tipo_carga,
        tipo_terreno=tipo_terreno,
        kilometros=kilometros
    )

    db.add(detalle)
    db.commit()
    db.refresh(detalle)

    return detalle


def crear_tramo_completo(
    db: Session,
    origen: str,
    destino: str,
    detalles: list[dict]
) -> Tramo:
    tramo = crear_tramo(db, origen, destino)

    for d in detalles:
        crear_tramo_detalle(
            db=db,
            tramo_id=tramo.id,
            tipo_carga=d["tipo_carga"],
            tipo_terreno=d["tipo_terreno"],
            kilometros=d["kilometros"]
        )

    return tramo


# Obtener tramo con detalles
def obtener_tramo(db: Session, tramo_id: int) -> Tramo:
    return db.query(Tramo).filter(
        Tramo.id == tramo_id,
        Tramo.estado == EstadoGeneral.activo
    ).first()
