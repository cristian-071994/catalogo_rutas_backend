import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataTramo {
  ruta_id: number;
  origen: string;
  destino: string;
  distancia_km: number;
  orden: number;
}

export default function TramosModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataTramo>({
    ruta_id: 0,
    origen: '',
    destino: '',
    distancia_km: 0,
    orden: 1,
  });
  const [error, setError] = useState('');
  const [selectedRuta, setSelectedRuta] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { data: rutas = [] } = useQuery({
    queryKey: ['rutas'],
    queryFn: () => api.getRutas(),
  });

  const { data: tramos = [], isLoading } = useQuery({
    queryKey: ['tramos', selectedRuta],
    queryFn: () => selectedRuta ? api.getTramos(selectedRuta) : Promise.resolve([]),
    enabled: !!selectedRuta,
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataTramo) => api.createTramo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tramos'] });
      setFormData({ ruta_id: 0, origen: '', destino: '', distancia_km: 0, orden: 1 });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear tramo');
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.ruta_id || !formData.origen || !formData.destino || formData.distancia_km <= 0) {
      setError('Todos los campos son requeridos');
      return;
    }
    createMutation.mutate(formData);
  };

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <select
          className="input-base flex-1"
          value={selectedRuta || ''}
          onChange={(e) => setSelectedRuta(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">-- Selecciona una ruta --</option>
          {rutas.map((ruta: any) => (
            <option key={ruta.id} value={ruta.id}>
              {ruta.origen} → {ruta.destino}
            </option>
          ))}
        </select>
        <button
          onClick={() => setShowForm(!showForm)}
          disabled={!selectedRuta}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-5 h-5" />
          Nuevo Tramo
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showForm && selectedRuta && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nuevo Tramo</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Origen del tramo"
              className="input-base"
              value={formData.origen}
              onChange={(e) => setFormData({ ...formData, origen: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Destino del tramo"
              className="input-base"
              value={formData.destino}
              onChange={(e) => setFormData({ ...formData, destino: e.target.value })}
              required
            />
            <input
              type="number"
              placeholder="Distancia (km)"
              className="input-base"
              value={formData.distancia_km || ''}
              onChange={(e) => setFormData({ ...formData, distancia_km: parseFloat(e.target.value) })}
              step="0.1"
              required
            />
            <input
              type="number"
              placeholder="Orden (1, 2, 3...)"
              className="input-base"
              value={formData.orden}
              onChange={(e) => setFormData({ ...formData, orden: Number(e.target.value) })}
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

      {isLoading && selectedRuta && (
        <div className="flex items-center justify-center py-8"><Loader className="animate-spin" /></div>
      )}

      {selectedRuta && !isLoading && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Orden</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Origen → Destino</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Distancia</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tramos.map((tramo: any) => (
                <tr key={tramo.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm font-medium text-neutral-900">#{tramo.orden}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{tramo.origen} → {tramo.destino}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{tramo.distancia_km} km</td>
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
      )}

      {selectedRuta && !isLoading && tramos.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay tramos registrados para esta ruta. Crea uno nuevo para comenzar.</p>
        </div>
      )}
    </div>
  );
}
