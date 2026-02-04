import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataConfigVehiculo {
  nombre: string;
  capacidad_tanque: number;
}

export default function ConfiguracionVehicleModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataConfigVehiculo>({
    nombre: '',
    capacidad_tanque: 0,
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: configs = [], isLoading } = useQuery({
    queryKey: ['configuracion-vehiculos'],
    queryFn: () => api.getConfiguracionVehiculos(),
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataConfigVehiculo) => api.createConfiguracionVehiculo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configuracion-vehiculos'] });
      setFormData({ nombre: '', capacidad_tanque: 0 });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear configuración');
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.nombre || formData.capacidad_tanque <= 0) {
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
            <input
              type="text"
              placeholder="Nombre (ej: Camión tipo C)"
              className="input-base"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              required
            />
            <input
              type="number"
              placeholder="Capacidad del tanque (galones)"
              className="input-base"
              value={formData.capacidad_tanque || ''}
              onChange={(e) => setFormData({ ...formData, capacidad_tanque: parseFloat(e.target.value) })}
              step="0.1"
              required
            />
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
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Nombre</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Capacidad (gal)</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {configs.map((config: any) => (
              <tr key={config.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                <td className="px-4 py-3 text-sm text-neutral-900">{config.nombre}</td>
                <td className="px-4 py-3 text-sm text-neutral-600">{config.capacidad_tanque}</td>
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

      {configs.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay configuraciones registradas. Crea una nueva para comenzar.</p>
        </div>
      )}
    </div>
  );
}
