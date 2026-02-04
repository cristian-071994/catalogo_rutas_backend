import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { AuthResponse } from '../types/index';

const API_URL = 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;
  private isRefreshing = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor para manejar errores y refresh token automático
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Si es 401 y no es el endpoint de login/refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (originalRequest.url?.includes('/login') || originalRequest.url?.includes('/refresh')) {
            // Si falla login o refresh, cerrar sesión
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('usuario');
            window.location.href = '/login';
            return Promise.reject(error);
          }

          originalRequest._retry = true;

          if (!this.isRefreshing) {
            this.isRefreshing = true;
            const refreshToken = localStorage.getItem('refresh_token');

            if (!refreshToken) {
              localStorage.removeItem('access_token');
              localStorage.removeItem('usuario');
              window.location.href = '/login';
              return Promise.reject(error);
            }

            try {
              const response = await axios.post(`${API_URL}/refresh`, { refresh_token: refreshToken });
              const { access_token, refresh_token: newRefreshToken } = response.data;

              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', newRefreshToken);

              this.isRefreshing = false;
              this.onRefreshed(access_token);
              this.refreshSubscribers = [];

              return this.client(originalRequest);
            } catch (refreshError) {
              this.isRefreshing = false;
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              localStorage.removeItem('usuario');
              window.location.href = '/login';
              return Promise.reject(refreshError);
            }
          }

          // Esperar a que el refresh termine
          return new Promise((resolve) => {
            this.subscribeTokenRefresh((token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(this.client(originalRequest));
            });
          });
        }

        return Promise.reject(error);
      }
    );
  }

  private subscribeTokenRefresh(cb: (token: string) => void) {
    this.refreshSubscribers.push(cb);
  }

  private onRefreshed(token: string) {
    this.refreshSubscribers.forEach((cb) => cb(token));
  }

  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/login', {
      email: email,
      password,
    });
    return response.data;
  }

  async register(email: string, password: string, nombre_completo: string, empresa_nit: string): Promise<any> {
    const response = await this.client.post<any>('/registro', {
      email,
      password,
      nombre: nombre_completo,
      empresa_nit
    });
    return response.data;
  }

  // Clientes
  async getClientes() {
    const response = await this.client.get('/clientes/');
    return response.data;
  }

  async createCliente(data: any) {
    const response = await this.client.post('/clientes/', data);
    return response.data;
  }

  // Vehículos
  async getVehiculos() {
    const response = await this.client.get('/vehiculos/');
    return response.data;
  }

  async createVehiculo(data: any) {
    const response = await this.client.post('/vehiculos/', data);
    return response.data;
  }

  // Rutas
  async getRutas() {
    const response = await this.client.get('/rutas/');
    return response.data;
  }

  async createRuta(data: any) {
    const response = await this.client.post('/rutas/', data);
    return response.data;
  }

  async getResumenRuta(rutaId: number, vehiculoId: number) {
    const response = await this.client.get(`/rutas/${rutaId}/resumen`, {
      params: { vehiculo_id: vehiculoId },
    });
    return response.data;
  }

  // Tramos
  async getTramos(rutaId: number) {
    const response = await this.client.get(`/rutas/${rutaId}/tramos`);
    return response.data;
  }

  async createTramo(data: any) {
    const response = await this.client.post('/tramos/', data);
    return response.data;
  }

  async updateTramo(tramoId: number, data: any) {
    const response = await this.client.put(`/tramos/${tramoId}`, data);
    return response.data;
  }

  // Peajes
  async getPeajes() {
    const response = await this.client.get('/peajes/');
    return response.data;
  }

  async createPeaje(data: any) {
    const response = await this.client.post('/peajes/', data);
    return response.data;
  }

  // Configuración
  async getConfiguracionVehiculos() {
    const response = await this.client.get('/configuracion_vehiculos/');
    return response.data;
  }

  async createConfiguracionVehiculo(data: any) {
    const response = await this.client.post('/configuracion_vehiculos/', data);
    return response.data;
  }

  // Marcas
  async getMarcas() {
    const response = await this.client.get('/marcas_vehiculos/');
    return response.data;
  }

  async createMarca(data: any) {
    const response = await this.client.post('/marcas_vehiculos/', data);
    return response.data;
  }
}

export default new ApiClient();
