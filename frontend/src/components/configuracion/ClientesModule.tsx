import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataCliente {
  nombre: string;
}

export default function ClientesModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataCliente>({
    nombre: '',
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: clientes = [], isLoading } = useQuery({
    queryKey: ['clientes'],
    queryFn: () => api.getClientes(),
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataCliente) => api.createCliente(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] });
      setFormData({ nombre: '' });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear cliente');
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.nombre) {
      setError('Nombre es requerido');
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
        Nuevo Cliente
      </button>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nuevo Cliente</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Nombre del cliente"
              className="input-base"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              required
            />
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
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Nombre</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {clientes.map((cliente: any) => (
              <tr key={cliente.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                <td className="px-4 py-3 text-sm text-neutral-900">{cliente.nombre}</td>
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

      {clientes.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay clientes registrados. Crea uno nuevo para comenzar.</p>
        </div>
      )}
    </div>
  );
}
