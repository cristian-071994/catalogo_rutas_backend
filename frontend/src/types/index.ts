// Tipos de autenticación
export interface Usuario {
  id: number;
  email: string;
  nombre_completo: string;
  activo: boolean;
  empresa?: string;  // Nombre de la empresa
  rol: {
    id: number;
    nombre: string;
  };
  permisos?: string[];
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  usuario_nombre: string;  // Lo que realmente devuelve el backend
  usuario_rol: string;     // Lo que realmente devuelve el backend
  empresa_nombre: string;  // Nombre de la empresa
  usuario_permisos: string[];
}

// Tipos de entidades
export interface Cliente {
  id: number;
  nombre: string;
  nit: string;
  contacto: string;
  email: string;
  telefono: string;
  activo: boolean;
}

export interface Vehiculo {
  id: number;
  placa: string;
  marca_id: number;
  configuracion_id: number;
  activo: boolean;
  marca?: MarcaVehiculo;
  configuracion?: ConfiguracionVehiculo;
}

export interface ConfiguracionVehiculo {
  id: number;
  nombre: string;
  capacidad_tanque: number;
  activo: boolean;
}

export interface MarcaVehiculo {
  id: number;
  nombre: string;
  activo: boolean;
}

export interface Ruta {
  id: number;
  cliente_id: number;
  nombre?: string;
  descripcion?: string;
  origen: string;
  destino: string;
  distancia_km: number;
  activo: boolean;
  cliente?: Cliente;
}

export interface Tramo {
  id: number;
  ruta_id: number;
  origen: string;
  destino: string;
  distancia_km: number;
  orden: number;
  activo: boolean;
}

export interface Peaje {
  id: number;
  nombre: string;
  sector: string;
  valor: number;
  activo: boolean;
}

export interface TramoDetalle {
  id: number;
  tramo_id: number;
  peaje_id: number;
  activo: boolean;
  peaje?: Peaje;
}

// Respuesta de resumen de ruta
export interface ResumenRutaDetallado {
  ruta: {
    id: number;
    nombre: string;
    cliente: string;
  };
  vehiculo: {
    placa: string;
  };
  configuracion_vehiculo: {
    marca: string;
    modelo: number;
    rendimientos_configurados: Record<string, number>;
  };
  resumen_distancia: {
    km_totales: number;
  };
  resumen_combustible: {
    precio_galon: number;
    galones_totales_requeridos: number;
    costo_total_combustible: number;
  };
  resumen_peajes: {
    cantidad_peajes: number;
    costo_total_peajes: number;
    detalles_peajes: ResumenPeajeDetalle[];
  };
  tramos_detalle: ResumenTramoDetalle[];
  costo_total_ruta: {
    km_totales: number;
    galones_requeridos: number;
    costo_combustible: number;
    costo_peajes: number;
    costo_total: number;
  };
}

export interface ResumenPeajeDetalle {
  peaje_id: number;
  nombre: string;
  costo: number;
  sector: string | null;
}

export interface ResumenTramoDetalleItem {
  tipo_carga: string;
  tipo_terreno: string;
  kilometros: number;
  rendimiento_km_galon: number;
  galones_necesarios: number;
}

export interface ResumenTramoDetalle {
  tramo_id: number;
  nombre: string;
  orden: number;
  km_totales: number;
  galones_totales: number;
  cantidad_peajes: number;
  costo_peajes: number;
  peajes: ResumenPeajeDetalle[];
  detalles: ResumenTramoDetalleItem[];
}
