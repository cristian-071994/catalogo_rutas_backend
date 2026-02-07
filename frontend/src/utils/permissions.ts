import type { Usuario } from '../types/index';

const CONFIG_PERMISSION_KEYS = [
  'editar_configuracion',
  'ver_clientes',
  'crear_cliente',
  'editar_cliente',
  'eliminar_cliente',
  'ver_marcas',
  'crear_marca',
  'editar_marca',
  'eliminar_marca',
  'ver_configuracion_vehiculos',
  'crear_configuracion_vehiculo',
  'editar_configuracion_vehiculo',
  'eliminar_configuracion_vehiculo',
  'ver_rendimiento',
  'crear_rendimiento',
  'editar_rendimiento',
  'eliminar_rendimiento',
  'ver_vehiculos',
  'crear_vehiculo',
  'editar_vehiculo',
  'eliminar_vehiculo',
  'ver_rutas',
  'crear_ruta',
  'editar_ruta',
  'eliminar_ruta',
  'ver_tramos',
  'crear_tramo',
  'editar_tramo',
  'eliminar_tramo',
  'ver_tramo_detalle',
  'crear_tramo_detalle',
  'editar_tramo_detalle',
  'eliminar_tramo_detalle',
  'ver_peajes',
  'crear_peaje',
  'editar_peaje',
  'eliminar_peaje',
];

export const hasPermission = (usuario: Usuario | null, permission: string): boolean => {
  if (!usuario) {
    return false;
  }

  if (usuario.rol?.nombre === 'super_admin') {
    return true;
  }

  return usuario.permisos?.includes(permission) ?? false;
};

export const hasAnyPermission = (usuario: Usuario | null, permissions: string[]): boolean => {
  if (!usuario) {
    return false;
  }

  if (usuario.rol?.nombre === 'super_admin') {
    return true;
  }

  const userPermissions = usuario.permisos ?? [];
  return permissions.some((permission) => userPermissions.includes(permission));
};

export const canAccessConfig = (usuario: Usuario | null): boolean => {
  return hasAnyPermission(usuario, CONFIG_PERMISSION_KEYS);
};
