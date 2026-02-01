import axios, { AxiosInstance } from 'axios';

const API_URL = 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

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

    // Interceptor para manejar errores
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('usuario');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', {
      username: email,
      password,
    });
    return response.data;
  }

  async register(email: string, password: string, nombre_completo: string) {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      nombre_completo,
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
