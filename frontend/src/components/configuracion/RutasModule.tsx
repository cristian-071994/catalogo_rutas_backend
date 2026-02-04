import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataRuta {
  cliente_id: number;
  origen: string;
  destino: string;
  distancia_km: number;
}

export default function RutasModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataRuta>({
    cliente_id: 0,
    origen: '',
    destino: '',
    distancia_km: 0,
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: rutas = [], isLoading } = useQuery({
    queryKey: ['rutas'],
    queryFn: () => api.getRutas(),
  });

  const { data: clientes = [] } = useQuery({
    queryKey: ['clientes'],
    queryFn: () => api.getClientes(),
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataRuta) => api.createRuta(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rutas'] });
      setFormData({ cliente_id: 0, origen: '', destino: '', distancia_km: 0 });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear ruta');
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.cliente_id || !formData.origen || !formData.destino || formData.distancia_km <= 0) {
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
        Nueva Ruta
      </button>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nueva Ruta</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <select
              className="input-base"
              value={formData.cliente_id || ''}
              onChange={(e) => setFormData({ ...formData, cliente_id: Number(e.target.value) })}
              required
            >
              <option value="">-- Selecciona un cliente --</option>
              {clientes.map((cliente: any) => (
                <option key={cliente.id} value={cliente.id}>
                  {cliente.nombre}
                </option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Origen (ciudad o punto de partida)"
              className="input-base"
              value={formData.origen}
              onChange={(e) => setFormData({ ...formData, origen: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Destino (ciudad o punto de llegada)"
              className="input-base"
              value={formData.destino}
              onChange={(e) => setFormData({ ...formData, destino: e.target.value })}
              required
            />
            <input
              type="number"
              placeholder="Distancia total (km)"
              className="input-base"
              value={formData.distancia_km || ''}
              onChange={(e) => setFormData({ ...formData, distancia_km: parseFloat(e.target.value) })}
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
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Cliente</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Origen → Destino</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Distancia</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {rutas.map((ruta: any) => (
              <tr key={ruta.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                <td className="px-4 py-3 text-sm text-neutral-900">{ruta.cliente?.nombre}</td>
                <td className="px-4 py-3 text-sm text-neutral-600">{ruta.origen} → {ruta.destino}</td>
                <td className="px-4 py-3 text-sm text-neutral-600">{ruta.distancia_km} km</td>
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

      {rutas.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay rutas registradas. Crea una nueva para comenzar.</p>
        </div>
      )}
    </div>
  );
}
