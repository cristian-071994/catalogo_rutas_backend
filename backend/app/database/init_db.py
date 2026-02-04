from app.database.db import engine
from app.database.base import Base

# 🔴 IMPORTANTE: importar modelos ANTES de create_all
# Esto asegura que SQLAlchemy "registre" los modelos en el Base
from app.models import (
    Cliente, Ruta, Tramo, TramoRuta, TramoDetalle,
    Peaje, RutaPeaje,
    MarcaVehiculo, ConfiguracionVehiculo, Vehiculo,
    RendimientoConfiguracion,
    ConfiguracionGeneral,
    Usuario
)
from app.models.rol_permiso import Rol, Permiso


def init_db():
    """
    Crea todas las tablas en la BD si no existen.
    SQLAlchemy verifica inteligentemente y solo crea las que faltan.
    """
    Base.metadata.create_all(bind=engine)
    
    # Crear roles y permisos del sistema si no existen
    _create_system_roles_and_permissions()


def _create_system_roles_and_permissions():
    """
    Crea roles y permisos del sistema en la BD
    Se ejecuta una sola vez (valida que no existan)
    """
    from app.database.session import SessionLocal
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        # Definir permisos del sistema (45 permisos en total)
        PERMISOS_DEL_SISTEMA = [
            # ========================================
            # USUARIOS
            # ========================================
            ("crear_usuario", "Crear nuevos usuarios", "usuarios"),
            ("editar_usuario", "Editar información de usuarios", "usuarios"),
            ("eliminar_usuario", "Eliminar usuarios", "usuarios"),
            ("ver_usuarios", "Ver lista de usuarios", "usuarios"),
            ("cambiar_rol_usuario", "Cambiar rol de un usuario", "usuarios"),
            
            # ========================================
            # ROLES Y PERMISOS
            # ========================================
            ("gestionar_roles", "Crear, editar y eliminar roles", "roles"),
            ("gestionar_permisos", "Crear, editar y eliminar permisos", "permisos"),
            
            # ========================================
            # CLIENTES
            # ========================================
            ("crear_cliente", "Crear nuevos clientes", "clientes"),
            ("editar_cliente", "Editar clientes existentes", "clientes"),
            ("eliminar_cliente", "Eliminar clientes", "clientes"),
            ("ver_clientes", "Ver lista de clientes", "clientes"),
            
            # ========================================
            # RUTAS
            # ========================================
            ("crear_ruta", "Crear nuevas rutas", "rutas"),
            ("editar_ruta", "Editar rutas existentes", "rutas"),
            ("eliminar_ruta", "Eliminar rutas", "rutas"),
            ("ver_rutas", "Ver lista de rutas", "rutas"),
            
            # ========================================
            # TRAMOS
            # ========================================
            ("crear_tramo", "Crear nuevos tramos", "tramos"),
            ("editar_tramo", "Editar tramos existentes", "tramos"),
            ("eliminar_tramo", "Eliminar tramos", "tramos"),
            ("ver_tramos", "Ver lista de tramos", "tramos"),
            
            # ========================================
            # TRAMO DETALLE
            # ========================================
            ("crear_tramo_detalle", "Crear detalles de tramos", "tramo_detalle"),
            ("editar_tramo_detalle", "Editar detalles de tramos", "tramo_detalle"),
            ("eliminar_tramo_detalle", "Eliminar detalles de tramos", "tramo_detalle"),
            ("ver_tramo_detalle", "Ver detalles de tramos", "tramo_detalle"),
            
            # ========================================
            # PEAJES
            # ========================================
            ("crear_peaje", "Crear nuevos peajes", "peajes"),
            ("editar_peaje", "Editar peajes existentes", "peajes"),
            ("eliminar_peaje", "Eliminar peajes", "peajes"),
            ("ver_peajes", "Ver lista de peajes", "peajes"),
            
            # ========================================
            # VEHÍCULOS
            # ========================================
            ("crear_vehiculo", "Crear nuevos vehículos", "vehiculos"),
            ("editar_vehiculo", "Editar vehículos existentes", "vehiculos"),
            ("eliminar_vehiculo", "Eliminar vehículos", "vehiculos"),
            ("ver_vehiculos", "Ver lista de vehículos", "vehiculos"),
            
            # ========================================
            # MARCAS DE VEHÍCULOS
            # ========================================
            ("crear_marca", "Crear nuevas marcas de vehículos", "marcas_vehiculos"),
            ("editar_marca", "Editar marcas de vehículos", "marcas_vehiculos"),
            ("eliminar_marca", "Eliminar marcas de vehículos", "marcas_vehiculos"),
            ("ver_marcas", "Ver lista de marcas de vehículos", "marcas_vehiculos"),
            
            # ========================================
            # CONFIGURACIÓN DE VEHÍCULOS
            # ========================================
            ("crear_configuracion_vehiculo", "Crear configuraciones de vehículos", "configuracion_vehiculos"),
            ("editar_configuracion_vehiculo", "Editar configuraciones de vehículos", "configuracion_vehiculos"),
            ("eliminar_configuracion_vehiculo", "Eliminar configuraciones de vehículos", "configuracion_vehiculos"),
            ("ver_configuracion_vehiculos", "Ver configuraciones de vehículos", "configuracion_vehiculos"),
            
            # ========================================
            # RENDIMIENTO
            # ========================================
            ("crear_rendimiento", "Crear configuraciones de rendimiento", "rendimiento"),
            ("editar_rendimiento", "Editar configuraciones de rendimiento", "rendimiento"),
            ("eliminar_rendimiento", "Eliminar configuraciones de rendimiento", "rendimiento"),
            ("ver_rendimiento", "Ver configuraciones de rendimiento", "rendimiento"),
            
            # ========================================
            # CONFIGURACIÓN Y REPORTES
            # ========================================
            ("editar_configuracion", "Editar configuración general del sistema", "configuracion"),
            ("ver_reportes", "Ver reportes y análisis", "reportes"),
        ]
        
        # Crear permisos si no existen
        for nombre, descripcion, categoria in PERMISOS_DEL_SISTEMA:
            existente = db.query(Permiso).filter(
                func.lower(Permiso.nombre) == func.lower(nombre)
            ).first()
            
            if not existente:
                permiso = Permiso(
                    nombre=nombre,
                    descripcion=descripcion,
                    categoria=categoria,
                    es_sistema=1,
                    activo=1
                )
                db.add(permiso)
        
        db.commit()
        
        # Definir roles del sistema
        ROLES_DEL_SISTEMA = {
            "super_admin": {
                "descripcion": "Super Administrador del sistema (puede gestionar todas las empresas)",
                "permisos": [perm[0] for perm in PERMISOS_DEL_SISTEMA]  # Todos los permisos
            },
            "admin": {
                "descripcion": "Administrador de empresa con acceso total a su empresa",
                "permisos": [perm[0] for perm in PERMISOS_DEL_SISTEMA]  # Todos los permisos
            },
            "supervisor": {
                "descripcion": "Supervisor con acceso a la mayoría de funciones",
                "permisos": [
                    "ver_usuarios", "ver_rutas", "editar_ruta", "ver_peajes", "editar_peaje",
                    "ver_clientes", "editar_cliente", "ver_vehiculos", "editar_vehiculo",
                    "ver_reportes"
                ]
            },
            "gestor_rutas": {
                "descripcion": "Gestor especializado en rutas",
                "permisos": ["crear_ruta", "editar_ruta", "eliminar_ruta", "ver_rutas", "ver_peajes"]
            },
            "gestor_peajes": {
                "descripcion": "Gestor especializado en peajes",
                "permisos": ["crear_peaje", "editar_peaje", "eliminar_peaje", "ver_peajes", "ver_rutas"]
            },
            "gestor_clientes": {
                "descripcion": "Gestor especializado en clientes",
                "permisos": ["crear_cliente", "editar_cliente", "eliminar_cliente", "ver_clientes"]
            },
            "consultor": {
                "descripcion": "Consultante con acceso de solo lectura",
                "permisos": ["ver_usuarios", "ver_rutas", "ver_peajes", "ver_clientes", "ver_vehiculos", "ver_reportes"]
            }
        }
        
        # Crear roles si no existen
        for nombre_rol, config in ROLES_DEL_SISTEMA.items():
            existente = db.query(Rol).filter(
                func.lower(Rol.nombre) == func.lower(nombre_rol)
            ).first()
            
            if not existente:
                # Obtener permisos para este rol
                permisos = db.query(Permiso).filter(
                    Permiso.nombre.in_(config["permisos"])
                ).all()
                
                rol = Rol(
                    nombre=nombre_rol,
                    descripcion=config["descripcion"],
                    es_sistema=1,
                    activo=1,
                    permisos=permisos
                )
                db.add(rol)
        
        db.commit()
        print("✅ Roles y permisos del sistema inicializados correctamente")
        
    except Exception as e:
        print(f"❌ Error inicializando roles y permisos: {e}")
        db.rollback()
    finally:
        db.close()

