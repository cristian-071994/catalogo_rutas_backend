"""
Router de Empresas
Gestión de empresas de transporte (multi-tenancy)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.auth import get_current_user
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.models.rol_permiso import Rol
from app.schemas.empresa import EmpresaCreate, EmpresaResponse, EmpresaUpdate, CrearEmpresaConAdminRequest, CrearEmpresaConAdminResponse
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"]
)


@router.get("/", response_model=List[EmpresaResponse], summary="Listar Empresas")
def listar_empresas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas las empresas del sistema.
    
    **Super admin** puede ver todas las empresas.
    **Todos los demás** (incluyendo admin) solo ven su propia empresa.
    """
    
    # Solo super admin ve todas las empresas
    if current_user.rol and current_user.rol.nombre == "super_admin":
        empresas = db.query(Empresa).offset(skip).limit(limit).all()
        return empresas
    
    # Todos los demás usuarios solo ven su propia empresa
    empresa = db.query(Empresa).filter(Empresa.id == current_user.empresa_id).first()
    return [empresa] if empresa else []


@router.get("/{empresa_id}", response_model=EmpresaResponse, summary="Obtener Empresa")
def obtener_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene los detalles de una empresa específica.
    
    Los usuarios solo pueden ver su propia empresa, excepto administradores.
    """
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Solo super admin puede ver cualquier empresa
    if current_user.rol and current_user.rol.nombre == "super_admin":
        return empresa
    
    # Todos los demás usuarios (incluyendo admin) solo pueden ver su propia empresa
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta empresa"
        )
    
    return empresa


@router.post("/", response_model=CrearEmpresaConAdminResponse, summary="Crear Empresa con Administrador", status_code=status.HTTP_201_CREATED)
def crear_empresa_con_admin(
    datos: CrearEmpresaConAdminRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva empresa en el sistema CON su administrador.
    
    **Solo SUPER ADMIN** puede crear empresas.
    
    Este endpoint es para onboarding de nuevas empresas de transporte.
    Crea la empresa Y su primer administrador en una sola operación.
    
    POST /empresas
    Body:
    {
        "empresa_nombre": "Cointra S.A.S.",
        "empresa_nit": "9001234567",
        "empresa_contacto": "Gerente General",
        "empresa_email": "contacto@cointra.com",
        "empresa_telefono": "3001234567",
        "admin_nombre": "Admin Cointra",
        "admin_email": "admin@cointra.com",
        "admin_password": "admin123"
    }
    """
    
    # 1. Verificar que es super_admin
    if not current_user.rol or current_user.rol.nombre != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el super administrador puede crear empresas"
        )
    
    # 2. Verificar que no exista el NIT
    empresa_existente = db.query(Empresa).filter(Empresa.nit == datos.empresa_nit).first()
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una empresa con NIT {datos.empresa_nit}"
        )
    
    # 3. Verificar que no exista el nombre
    empresa_existente = db.query(Empresa).filter(Empresa.nombre == datos.empresa_nombre).first()
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una empresa con el nombre '{datos.empresa_nombre}'"
        )
    
    # 4. Verificar que el email del admin no exista
    usuario_existente = db.query(Usuario).filter(Usuario.email == datos.admin_email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email {datos.admin_email} ya está registrado"
        )
    
    # 5. Buscar el rol "admin"
    rol_admin = db.query(Rol).filter(Rol.nombre == "admin").first()
    if not rol_admin:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error: Rol 'admin' no encontrado en el sistema"
        )
    
    try:
        # 6. Crear la empresa
        nueva_empresa = Empresa(
            nombre=datos.empresa_nombre,
            nit=datos.empresa_nit,
            contacto=datos.empresa_contacto,
            email=datos.empresa_email,
            telefono=datos.empresa_telefono,
            activo=1
        )
        db.add(nueva_empresa)
        db.flush()  # Para obtener el ID
        
        # 7. Crear el administrador de la empresa
        password_hash = pwd_context.hash(datos.admin_password)
        
        admin = Usuario(
            nombre=datos.admin_nombre,
            email=datos.admin_email,
            password_hash=password_hash,
            empresa_id=nueva_empresa.id,
            rol_id=rol_admin.id,
            activo=1,
            aprobado=1,  # Auto-aprobado
            aprobado_por=current_user.id,  # Aprobado por super admin
            aprobado_en=datetime.now()
        )
        db.add(admin)
        
        # 8. Commit
        db.commit()
        db.refresh(nueva_empresa)
        db.refresh(admin)
        
        return CrearEmpresaConAdminResponse(
            mensaje=f"Empresa '{nueva_empresa.nombre}' creada exitosamente con su administrador.",
            empresa=EmpresaResponse.model_validate(nueva_empresa),
            admin_email=admin.email
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear empresa y administrador: {str(e)}"
        )


@router.put("/{empresa_id}", response_model=EmpresaResponse, summary="Actualizar Empresa")
def actualizar_empresa(
    empresa_id: int,
    datos: EmpresaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza los datos de una empresa.
    
    Solo administradores de la empresa pueden actualizarla.
    """
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Super admin puede actualizar cualquier empresa
    if current_user.rol and current_user.rol.nombre == "super_admin":
        pass  # Permitir
    # Admin solo puede actualizar su propia empresa
    elif current_user.rol and current_user.rol.nombre == "admin" and current_user.empresa_id == empresa_id:
        pass  # Permitir
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo super admin o administradores de la empresa pueden actualizarla"
        )
    
    # Actualizar campos
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(empresa, campo, valor)
    
    db.commit()
    db.refresh(empresa)
    
    return empresa


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Empresa")
def eliminar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Desactiva una empresa (soft delete).
    
    **Solo super administradores** pueden eliminar empresas.
    
    ⚠️ Esto desactiva todos los usuarios, clientes, rutas, etc. de la empresa.
    """
    
    # Solo super_admin puede eliminar empresas
    if not current_user.rol or current_user.rol.nombre != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el super administrador puede eliminar empresas"
        )
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Soft delete
    empresa.activo = 0
    db.commit()
    
    return None
