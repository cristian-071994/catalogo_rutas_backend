import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataRuta {
  nombre: string;
  descripcion: string;
  cliente_id: number;
}

export default function RutasModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataRuta>({
    nombre: '',
    descripcion: '',
    cliente_id: 0,
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: rutas = [], isLoading } = useQuery({
    queryKey: ['rutas'],
    queryFn: async () => {
      const data = await api.getRutas();
      return data?.items || data || [];
    },
  });

  const { data: clientes = [] } = useQuery({
    queryKey: ['clientes'],
    queryFn: async () => {
      const data = await api.getClientes();
      return data?.items || data || [];
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataRuta) => api.createRuta(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rutas'] });
      setFormData({ nombre: '', descripcion: '', cliente_id: 0 });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear ruta');
      setTimeout(() => setError(''), 10000);
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.nombre || !formData.descripcion || !formData.cliente_id) {
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
            <input
              type="text"
              placeholder="Nombre de la ruta"
              className="input-base"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              required
            />
            <textarea
              placeholder="Descripción de la ruta"
              className="input-base"
              rows={3}
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              required
            />
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
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Nombre</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Cliente</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Estado</th>
            </tr>
          </thead>
          <tbody>
            {rutas.map((ruta: any) => {
              const cliente = clientes.find((c: any) => c.id === ruta.cliente_id);
              
              return (
                <tr key={ruta.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm font-medium text-neutral-900">{ruta.nombre}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{cliente?.nombre || 'N/A'}</td>
                  <td className="px-4 py-3 text-sm">
                    {ruta.estado === 'activo' || ruta.estado === 1 || ruta.estado === true ? (
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

      {!isLoading && rutas.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          No hay rutas registradas
        </div>
      )}
    </div>
  );
}
