import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataConfigVehiculo {
  marca_id: number | '';
  modelo: number | '';
}

export default function ConfiguracionVehicleModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataConfigVehiculo>({
    marca_id: '',
    modelo: '',
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: configs = [], isLoading } = useQuery({
    queryKey: ['configuracion-vehiculos'],
    queryFn: () => api.getConfiguracionVehiculos(),
  });

  const { data: marcas = [] } = useQuery({
    queryKey: ['marcas'],
    queryFn: () => api.getMarcas(),
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataConfigVehiculo) => api.createConfiguracionVehiculo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configuracion-vehiculos'] });
      setFormData({ marca_id: '', modelo: '' });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear configuración');
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.marca_id || !formData.modelo) {
      setError('Todos los campos son requeridos');
      return;
    }
    createMutation.mutate({
      marca_id: Number(formData.marca_id),
      modelo: Number(formData.modelo)
    });
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
        Nueva Configuración
      </button>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nueva Configuración</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Marca *</label>
              <select
                className="input-base"
                value={formData.marca_id}
                onChange={(e) => setFormData({ ...formData, marca_id: e.target.value ? Number(e.target.value) : '' })}
                required
              >
                <option value="">Selecciona una marca</option>
                {marcas.map((marca: any) => (
                  <option key={marca.id} value={marca.id}>
                    {marca.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Modelo (año) *</label>
              <input
                type="number"
                placeholder="2020"
                className="input-base"
                value={formData.modelo || ''}
                onChange={(e) => setFormData({ ...formData, modelo: e.target.value ? Number(e.target.value) : '' })}
                min="1900"
                max="2100"
                required
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary" disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Guardando...' : 'Guardar'}
              </button>
              <button
                type="button"
                className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
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
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Marca</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Modelo</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Estado</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {configs.map((config: any) => {
              const marca = marcas.find((m: any) => m.id === config.marca_id);
              return (
                <tr key={config.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm text-neutral-900">{marca?.nombre || 'Desconocida'}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{config.modelo}</td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      config.estado === 'activo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {config.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button className="p-1 text-red-600 hover:bg-red-50 rounded">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {configs.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay configuraciones registradas. Crea una nueva para comenzar.</p>
        </div>
      )}
    </div>
  );
}
