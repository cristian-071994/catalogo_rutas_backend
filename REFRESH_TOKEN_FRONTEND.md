# 🔄 Implementación Refresh Token - Frontend

## ✅ Backend Completado

Ya está implementado en el backend:
- **Access Token**: 30 minutos (para operaciones normales)
- **Refresh Token**: 7 días (para renovar automáticamente)
- Endpoint `/api/v1/refresh` para renovar el access token

## 📝 Implementación Frontend (React)

### 1. Actualizar `AuthContext.tsx`

Modifica el archivo `frontend/src/context/AuthContext.tsx`:

```typescript
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/v1';

interface User {
  nombre: string;
  rol: string;
  empresa_nombre: string;
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  // Al cargar, restaurar tokens desde localStorage
  useEffect(() => {
    const storedAccessToken = localStorage.getItem('access_token');
    const storedRefreshToken = localStorage.getItem('refresh_token');
    const storedUser = localStorage.getItem('user');

    if (storedAccessToken && storedUser) {
      setAccessToken(storedAccessToken);
      setUser(JSON.parse(storedUser));
      
      // Configurar interceptor para renovar automáticamente
      setupAxiosInterceptor(storedRefreshToken);
    }
  }, []);

  // Configurar interceptor de axios para manejar expiración
  const setupAxiosInterceptor = (refreshToken: string | null) => {
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Si el error es 401 y no hemos intentado renovar
        if (error.response?.status === 401 && !originalRequest._retry && refreshToken) {
          originalRequest._retry = true;

          try {
            // Llamar al endpoint de refresh
            const response = await axios.post(`${API_URL}/refresh`, {
              refresh_token: refreshToken
            });

            const { access_token, refresh_token: newRefreshToken } = response.data;

            // Actualizar tokens en localStorage
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', newRefreshToken);
            
            // Actualizar estado
            setAccessToken(access_token);

            // Reintentar la petición original con el nuevo token
            originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
            return axios(originalRequest);
          } catch (refreshError) {
            // Si falla el refresh, cerrar sesión
            logout();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_URL}/login`, {
        email,
        password
      });

      const { 
        access_token, 
        refresh_token,
        usuario_nombre, 
        usuario_rol, 
        empresa_nombre 
      } = response.data;

      // Guardar tokens en localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      const userData = {
        nombre: usuario_nombre,
        rol: usuario_rol,
        empresa_nombre: empresa_nombre
      };
      
      localStorage.setItem('user', JSON.stringify(userData));

      // Actualizar estado
      setAccessToken(access_token);
      setUser(userData);

      // Configurar interceptor
      setupAxiosInterceptor(refresh_token);

    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error al iniciar sesión');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setAccessToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      accessToken,
      login,
      logout,
      isAuthenticated: !!accessToken
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};
```

### 2. Actualizar `axiosConfig` o servicio API

Crea/actualiza `frontend/src/services/api.ts`:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
});

// Interceptor para añadir token en cada petición
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
```

### 3. Usar el servicio API en lugar de axios directo

En todos tus componentes, usa el servicio configurado:

```typescript
// ❌ Antes
import axios from 'axios';
axios.get('http://127.0.0.1:8000/api/v1/clientes')

// ✅ Ahora
import api from '../services/api';
api.get('/clientes')
```

## 🎯 Cómo Funciona

1. **Login**:
   - Usuario ingresa credenciales
   - Backend devuelve `access_token` (30 min) + `refresh_token` (7 días)
   - Ambos se guardan en `localStorage`

2. **Peticiones Normales**:
   - Cada petición usa el `access_token` en el header
   - Funciona normal durante 30 minutos

3. **Cuando expira el Access Token**:
   - API devuelve 401 Unauthorized
   - Interceptor detecta el error
   - Automáticamente llama a `/refresh` con el `refresh_token`
   - Obtiene nuevo `access_token`
   - Reintenta la petición original con el nuevo token
   - **El usuario NO se da cuenta** ✨

4. **Cuando expira el Refresh Token** (7 días):
   - `/refresh` devuelve 401
   - Se cierra la sesión automáticamente
   - Usuario debe hacer login nuevamente

## ⏱️ Tiempos

| Token | Duración | Propósito |
|-------|----------|-----------|
| Access Token | 30 minutos | Operaciones del día a día |
| Refresh Token | 7 días | Renovar automáticamente |

## 🔐 Seguridad

- ✅ Access token corto minimiza riesgo si es interceptado
- ✅ Refresh token largo permite sesiones cómodas
- ✅ Renovación automática sin que el usuario lo note
- ✅ Logout automático después de 7 días de inactividad

## 🚀 Próximos Pasos

1. Implementar el código del `AuthContext.tsx` según arriba
2. Crear el archivo `api.ts` con el interceptor
3. Actualizar todos los componentes para usar `api` en lugar de `axios`
4. Probar el flujo completo:
   - Login → trabajar 31 minutos → verificar que se renueva automáticamente
   - Esperar 7 días → verificar que cierra sesión automática

## 💡 Opcional: Renovación Proactiva

Si quieres renovar **antes** de que expire (más profesional):

```typescript
// En AuthContext, cada 25 minutos renovar proactivamente
useEffect(() => {
  if (!accessToken) return;

  const interval = setInterval(async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        const response = await axios.post(`${API_URL}/refresh`, {
          refresh_token: refreshToken
        });
        
        localStorage.setItem('access_token', response.data.access_token);
        setAccessToken(response.data.access_token);
      } catch (error) {
        console.error('Error renovando token:', error);
      }
    }
  }, 25 * 60 * 1000); // 25 minutos

  return () => clearInterval(interval);
}, [accessToken]);
```
