import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { Usuario, AuthResponse } from '../types/index';
import api from '../services/api';

interface AuthContextType {
  usuario: Usuario | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, nombre_completo: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Verificar si hay sesión al cargar
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const usuarioStored = localStorage.getItem('usuario');
    
    if (token && usuarioStored) {
      try {
        setUsuario(JSON.parse(usuarioStored));
      } catch (error) {
        console.error('Error parsing stored usuario:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('usuario');
      }
    }
    
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response: any = await api.login(email, password);
      
      // Guardar token
      localStorage.setItem('access_token', response.access_token);
      
      // Crear objeto usuario desde la respuesta del backend
      const usuario: Usuario = {
        id: 0, // Temporal, se obtiene del token o endpoint /me
        email: email,
        nombre_completo: response.usuario_nombre,
        activo: true,
        rol: {
          id: 0,
          nombre: response.usuario_rol
        },
        empresa: response.empresa_nombre  // Guardamos la empresa
      };
      
      localStorage.setItem('usuario', JSON.stringify(usuario));
      setUsuario(usuario);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string, nombre_completo: string) => {
    try {
      const response: AuthResponse = await api.register(email, password, nombre_completo);
      
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('usuario', JSON.stringify(response.usuario));
      
      setUsuario(response.usuario);
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('usuario');
    setUsuario(null);
  };

  return (
    <AuthContext.Provider
      value={{
        usuario,
        isAuthenticated: !!usuario,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
}
