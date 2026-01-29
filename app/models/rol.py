from enum import Enum


class RolEnum(str, Enum):
    """Enumeración de roles disponibles en el sistema"""
    
    admin = "admin"                    # Todo acceso (incluido DELETE)
    supervisor = "supervisor"          # Todo EXCEPTO DELETE
    gestor_rutas = "gestor_rutas"      # Solo rutas (POST/PUT/GET)
    gestor_peajes = "gestor_peajes"    # Solo peajes (POST/PUT/GET)
    gestor_clientes = "gestor_clientes"  # Solo clientes (POST/PUT/GET)
    consultor = "consultor"            # Solo GET (lectura)


# Mapeo de permisos por rol
PERMISOS_POR_ROL = {
    RolEnum.admin: {
        "crear": True,
        "actualizar": True,
        "eliminar": True,
        "consultar": True,
        "gestionar_usuarios": True,
    },
    RolEnum.supervisor: {
        "crear": True,
        "actualizar": True,
        "eliminar": False,  # ← NO puede eliminar
        "consultar": True,
        "gestionar_usuarios": False,
    },
    RolEnum.gestor_rutas: {
        "crear_rutas": True,
        "actualizar_rutas": True,
        "eliminar_rutas": True,
        "consultar_rutas": True,
        "crear_otros": False,
        "actualizar_otros": False,
        "eliminar_otros": False,
    },
    RolEnum.gestor_peajes: {
        "crear_peajes": True,
        "actualizar_peajes": True,
        "eliminar_peajes": True,
        "consultar_peajes": True,
        "crear_otros": False,
        "actualizar_otros": False,
        "eliminar_otros": False,
    },
    RolEnum.gestor_clientes: {
        "crear_clientes": True,
        "actualizar_clientes": True,
        "eliminar_clientes": True,
        "consultar_clientes": True,
        "crear_otros": False,
        "actualizar_otros": False,
        "eliminar_otros": False,
    },
    RolEnum.consultor: {
        "crear": False,
        "actualizar": False,
        "eliminar": False,
        "consultar": True,  # ← Solo lectura
    },
}
