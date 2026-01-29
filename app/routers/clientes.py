from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteResponse

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

# Crear cliente
@router.post("/", response_model=ClienteResponse)
def crear_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db)
):
    nuevo_cliente = Cliente(**cliente.model_dump())

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return nuevo_cliente

# Listar cliente
@router.get("/", response_model=list[ClienteResponse])
def listar_clientes(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista clientes ACTIVOS por defecto.
    
    GET /clientes/
    GET /clientes/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    from app.models.enums import EstadoGeneral
    
    query = db.query(Cliente)
    
    if not incluir_inactivos:
        query = query.filter(Cliente.estado == EstadoGeneral.activo)
    
    return query.all()

# Obtener cliente por ID (con rutas)
@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    cliente = (
        db.query(Cliente)
        .filter(Cliente.id == cliente_id)
        .first()
    )

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return cliente
