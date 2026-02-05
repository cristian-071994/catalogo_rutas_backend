import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataVehiculo {
  placa: string;
  configuracion_id: number;
}

export default function VehiculosModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataVehiculo>({
    placa: '',
    configuracion_id: 0,
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: vehiculos = [], isLoading } = useQuery({
    queryKey: ['vehiculos'],
    queryFn: async () => {
      const response = await api.getVehiculos();
      return response.data?.items || response.data || [];
    },
  });

  const { data: configs = [] } = useQuery({
    queryKey: ['configuracion-vehiculos'],
    queryFn: async () => {
      const response = await api.getConfiguracionVehiculos();
      return response.data?.items || response.data || [];
    },
  });

  const { data: marcas = [] } = useQuery({
    queryKey: ['marcas'],
    queryFn: async () => {
      const response = await api.getMarcas();
      return response.data?.items || response.data || [];
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataVehiculo) => api.createVehiculo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] });
      setFormData({ placa: '', configuracion_id: 0 });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear vehículo');
      setTimeout(() => setError(''), 10000);
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.placa || !formData.configuracion_id) {
      setError('Todos los campos son requeridos');
      return;
    }
    createMutation.mutate(formData);
  };

  if (isLoading) {
    return <div className="flex items-center justify-center py-8"><Loader className="animate-spin" /></div>;
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => setShowForm(!showForm)}
        className="btn-primary flex items-center gap-2"
      >
        <Plus className="w-5 h-5" />
        Nuevo Vehículo
      </button>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nuevo Vehículo</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Placa (ej: ABC123)"
              className="input-base"
              value={formData.placa}
              onChange={(e) => setFormData({ ...formData, placa: e.target.value.toUpperCase() })}
              required
            />
            <select
              className="input-base"
              value={formData.configuracion_id || ''}
              onChange={(e) => setFormData({ ...formData, configuracion_id: Number(e.target.value) })}
              required
            >
              <option value="">-- Selecciona una configuración --</option>
              {configs.map((config: any) => {
                const marca = marcas.find((m: any) => m.id === config.marca_id);
                return (
                  <option key={config.id} value={config.id}>
                    {marca?.nombre || 'Desconocido'} - {config.modelo}
                  </option>
                );
              })}
            </select>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary" disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Guardando...' : 'Guardar'}
              </button>
              <button
                type="button"
                className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                onClick={() => setShowForm(false)}
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="max-h-[400px] overflow-y-auto border border-neutral-200 rounded-lg">
        <table className="w-full">
          <thead className="sticky top-0 bg-white">
            <tr className="border-b border-neutral-200">
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Placa</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Configuración</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Estado</th>
            </tr>
          </thead>
          <tbody>
            {vehiculos.map((vehiculo: any) => {
              const config = configs.find((c: any) => c.id === vehiculo.configuracion_id);
              const marca = marcas.find((m: any) => m.id === config?.marca_id);
              
              return (
                <tr key={vehiculo.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm font-medium text-neutral-900">{vehiculo.placa}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">
                    {marca?.nombre || 'N/A'} - {config?.modelo || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {vehiculo.estado === 1 ? (
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                        Activo
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                        Inactivo
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {!isLoading && vehiculos.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          No hay vehículos registrados
        </div>
      )}
    </div>
  );
}
