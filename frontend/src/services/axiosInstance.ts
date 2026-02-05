import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Crear instancia de axios
const axiosInstance = axios.create({
  baseURL: API_URL,
});

// Flag para evitar múltiples intentos de refresh simultáneos
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

// Interceptor de respuesta para manejar errores 401
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el error es 401 y no hemos intentado refrescar aún
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Si ya estamos refrescando, poner en cola
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers['Authorization'] = 'Bearer ' + token;
            return axiosInstance(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        // No hay refresh token, redirigir a login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        // Intentar refrescar el token
        const response = await axios.post(`${API_URL}/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token: new_refresh_token } = response.data;
        
        // Guardar nuevos tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', new_refresh_token);
        
        // Actualizar el header del request original
        originalRequest.headers['Authorization'] = 'Bearer ' + access_token;
        
        // Procesar la cola
        processQueue(null, access_token);
        
        isRefreshing = false;
        
        // Reintentar el request original
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Si falla el refresh, cerrar sesión
        processQueue(refreshError, null);
        isRefreshing = false;
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Interceptor de request para agregar token automáticamente
axiosInstance.interceptors.request.use(
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

export default axiosInstance;
