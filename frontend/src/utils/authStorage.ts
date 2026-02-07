import type { Usuario } from '../types/index';

type AuthPayload = {
  usuario_nombre?: string;
  usuario_rol?: string;
  empresa_nombre?: string;
  usuario_permisos?: string[];
};

export const mergeStoredUser = (payload: AuthPayload): Usuario | null => {
  const raw = localStorage.getItem('usuario');
  if (!raw) {
    return null;
  }

  try {
    const existing = JSON.parse(raw) as Usuario;
    const next: Usuario = {
      ...existing,
      nombre_completo: payload.usuario_nombre ?? existing.nombre_completo,
      rol: {
        id: existing.rol?.id ?? 0,
        nombre: payload.usuario_rol ?? existing.rol?.nombre ?? '',
      },
      empresa: payload.empresa_nombre ?? existing.empresa,
      permisos: payload.usuario_permisos ?? existing.permisos ?? [],
    };

    localStorage.setItem('usuario', JSON.stringify(next));
    return next;
  } catch (error) {
    console.error('Error parsing stored usuario:', error);
    return null;
  }
};
