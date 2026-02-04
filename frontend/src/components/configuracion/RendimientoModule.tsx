import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Loader } from 'lucide-react';

interface FormDataRendimiento {
  configuracion_id: number;
  km_por_galon: number;
}

export default function RendimientoModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataRendimiento>({
    configuracion_id: 0,
    km_por_galon: 0,
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: configs = [] } = useQuery({
    queryKey: ['configuracion-vehiculos'],
    queryFn: () => api.getConfiguracionVehiculos(),
  });

  const { isLoading } = useQuery({
    queryKey: ['rendimiento'],
    queryFn: () => api.getConfiguracionVehiculos(), // Placeholder
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataRendimiento) => api.createConfiguracionVehiculo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rendimiento'] });
      setFormData({ configuracion_id: 0, km_por_galon: 0 });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear rendimiento');
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.configuracion_id || formData.km_por_galon <= 0) {
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
        Nuevo Rendimiento
      </button>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nuevo Rendimiento</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
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
            <input
              type="number"
              placeholder="km por galón"
              className="input-base"
              value={formData.km_por_galon || ''}
              onChange={(e) => setFormData({ ...formData, km_por_galon: parseFloat(e.target.value) })}
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

      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
        💡 Define el rendimiento (km/galón) para cada configuración de vehículo
      </div>
    </div>
  );
}
