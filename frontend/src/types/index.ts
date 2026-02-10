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
export interface PeajeResumen {
  id: number;
  nombre: string;
  valor: number;
  sector: string;
}

export interface TramoResumen {
  id: number;
  origen: string;
  destino: string;
  distancia_km: number;
  costo_peajes: number;
  cantidad_peajes: number;
  peajes: PeajeResumen[];
}

export interface ResumenRutaDetallado {
  ruta_id: number;
  cliente_nombre: string;
  origen: string;
  destino: string;
  distancia_total_km: number;
  vehiculo_placa: string;
  consumo_galones: number;
  costo_combustible: number;
  costo_peajes_total: number;
  costo_total: number;
  tramos: TramoResumen[];
}
