from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.configuracion import ConfiguracionGeneral
from app.models.usuario import Usuario
from app.schemas.configuracion import (
    ConfiguracionCreate,
    ConfiguracionUpdate,
    ConfiguracionResponse
)
from app.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/configuracion",
    tags=["Configuración"]
)


# ============================================
# OBTENER CONFIGURACIÓN
# ============================================

@router.get("/{clave}", response_model=ConfiguracionResponse)
def obtener_configuracion(
    clave: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el valor de una configuración por su clave.
    
    Ejemplo: GET /configuracion/precio_galon
    Retorna: { "clave": "precio_galon", "valor": "9500", ... }
    """
    query = db.query(ConfiguracionGeneral).filter(
        ConfiguracionGeneral.clave == clave
    )
    
    # Multi-tenancy: filtrar por empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(ConfiguracionGeneral.empresa_id == current_user.empresa_id)
    
    config = query.first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración '{clave}' no encontrada"
        )

    return config


@router.get("/", response_model=list[ConfiguracionResponse])
def listar_configuraciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista TODAS las configuraciones del sistema.
    
    GET /configuracion/
    """
    query = db.query(ConfiguracionGeneral)
    
    # Multi-tenancy: filtrar por empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(ConfiguracionGeneral.empresa_id == current_user.empresa_id)
    
    return query.all()


# ============================================
# CREAR CONFIGURACIÓN
# ============================================

@router.post(
    "/",
    response_model=ConfiguracionResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_configuracion(
    config: ConfiguracionCreate,
    current_user: Usuario = Depends(require_permission("editar_configuracion")),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva configuración.
    
    Body:
    {
        "clave": "precio_galon",
        "valor": "9500",
        "descripcion": "Precio del galón de combustible"
    }
    
    ⚠️ La clave debe ser ÚNICA (no puedes crear dos con la misma clave)
    """
    
    # Verificar que no exista EN LA MISMA EMPRESA
    query_existente = db.query(ConfiguracionGeneral).filter(
        func.lower(ConfiguracionGeneral.clave) == func.lower(config.clave)
    )
    
    # Multi-tenancy: solo validar duplicados en la misma empresa
    if current_user.empresa_id is not None:
        query_existente = query_existente.filter(
            ConfiguracionGeneral.empresa_id == current_user.empresa_id
        )
    
    existente = query_existente.first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe configuración con clave '{config.clave}'"
        )

    # Crear con empresa_id del usuario
    nueva_config = ConfiguracionGeneral(
        **config.model_dump(),
        empresa_id=current_user.empresa_id  # Multi-tenancy
    )
    db.add(nueva_config)
    db.commit()
    db.refresh(nueva_config)

    return nueva_config


# ============================================
# ACTUALIZAR CONFIGURACIÓN
# ============================================

@router.put("/{clave}", response_model=ConfiguracionResponse)
def actualizar_configuracion(
    clave: str,
    config_update: ConfiguracionUpdate,
    current_user: Usuario = Depends(require_permission("editar_configuracion")),
    db: Session = Depends(get_db)
):
    """
    Actualiza el valor de una configuración existente.
    
    PUT /configuracion/precio_galon
    Body:
    {
        "valor": "10000",
        "descripcion": "Nuevo precio actualizado"
    }
    
    La clave NO cambia, es el identificador.
    """
    
    query = db.query(ConfiguracionGeneral).filter(
        func.lower(ConfiguracionGeneral.clave) == func.lower(clave)
    )
    
    # Multi-tenancy: filtrar por empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(ConfiguracionGeneral.empresa_id == current_user.empresa_id)
    
    config = query.first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración '{clave}' no encontrada"
        )

    # Actualizar solo los campos enviados
    for campo, valor in config_update.model_dump(exclude_unset=True).items():
        setattr(config, campo, valor)

    db.add(config)
    db.commit()
    db.refresh(config)

    return config


# ============================================
# ELIMINAR CONFIGURACIÓN (rara, pero por si acaso)
# ============================================

@router.delete("/{clave}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_configuracion(
    clave: str,
    current_user: Usuario = Depends(require_permission("editar_configuracion")),
    db: Session = Depends(get_db)
):
    """
    Elimina una configuración.
    
    DELETE /configuracion/precio_galon
    
    ⚠️ Cuidado: esto puede romper el sistema si eliminas cosas importantes
    """
    
    query = db.query(ConfiguracionGeneral).filter(
        func.lower(ConfiguracionGeneral.clave) == func.lower(clave)
    )
    
    # Multi-tenancy: filtrar por empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(ConfiguracionGeneral.empresa_id == current_user.empresa_id)
    
    config = query.first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración '{clave}' no encontrada"
        )

    db.delete(config)
    db.commit()

    return None
