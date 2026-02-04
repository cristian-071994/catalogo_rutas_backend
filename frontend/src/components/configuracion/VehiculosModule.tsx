import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataVehiculo {
  placa: string;
  marca_id: number;
  configuracion_id: number;
}

export default function VehiculosModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataVehiculo>({
    placa: '',
    marca_id: 0,
    configuracion_id: 0,
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: vehiculos = [], isLoading } = useQuery({
    queryKey: ['vehiculos'],
    queryFn: () => api.getVehiculos(),
  });

  const { data: marcas = [] } = useQuery({
    queryKey: ['marcas'],
    queryFn: () => api.getMarcas(),
  });

  const { data: configs = [] } = useQuery({
    queryKey: ['configuracion-vehiculos'],
    queryFn: () => api.getConfiguracionVehiculos(),
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataVehiculo) => api.createVehiculo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] });
      setFormData({ placa: '', marca_id: 0, configuracion_id: 0 });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear vehículo');
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.placa || !formData.marca_id || !formData.configuracion_id) {
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
              placeholder="Placa (ej: ABC-123)"
              className="input-base"
              value={formData.placa}
              onChange={(e) => setFormData({ ...formData, placa: e.target.value.toUpperCase() })}
              required
            />
            <select
              className="input-base"
              value={formData.marca_id || ''}
              onChange={(e) => setFormData({ ...formData, marca_id: Number(e.target.value) })}
              required
            >
              <option value="">-- Selecciona una marca --</option>
              {marcas.map((marca: any) => (
                <option key={marca.id} value={marca.id}>
                  {marca.nombre}
                </option>
              ))}
            </select>
            <select
              className="input-base"
              value={formData.configuracion_id || ''}
              onChange={(e) => setFormData({ ...formData, configuracion_id: Number(e.target.value) })}
              required
            >
              <option value="">-- Selecciona una configuración --</option>
              {configs.map((config: any) => (
                <option key={config.id} value={config.id}>
                  {config.nombre}
                </option>
              ))}
            </select>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary" disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Guardando...' : 'Guardar'}
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setShowForm(false)}
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-200">
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Placa</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Marca</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Configuración</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {vehiculos.map((vehiculo: any) => (
              <tr key={vehiculo.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                <td className="px-4 py-3 text-sm font-medium text-neutral-900">{vehiculo.placa}</td>
                <td className="px-4 py-3 text-sm text-neutral-600">{vehiculo.marca?.nombre}</td>
                <td className="px-4 py-3 text-sm text-neutral-600">{vehiculo.configuracion?.nombre}</td>
                <td className="px-4 py-3 text-right">
                  <button className="p-1 text-red-600 hover:bg-red-50 rounded">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {vehiculos.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay vehículos registrados. Crea uno nuevo para comenzar.</p>
        </div>
      )}
    </div>
  );
}
