import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Trash2, Loader } from 'lucide-react';

interface FormDataPeaje {
  nombre: string;
  sector: string;
  valor: number;
}

export default function PeajesModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataPeaje>({
    nombre: '',
    sector: '',
    valor: 0,
  });
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: peajes = [], isLoading } = useQuery({
    queryKey: ['peajes'],
    queryFn: () => api.getPeajes(),
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataPeaje) => api.createPeaje(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['peajes'] });
      setFormData({ nombre: '', sector: '', valor: 0 });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear peaje');
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.nombre || !formData.sector || formData.valor <= 0) {
      setError('Todos los campos son requeridos');
      return;
    }
    createMutation.mutate(formData);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-neutral-900">Peajes</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Nuevo Peaje
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nuevo Peaje</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Nombre del peaje"
              className="input-base"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Sector o ruta donde aplica"
              className="input-base"
              value={formData.sector}
              onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
              required
            />
            <input
              type="number"
              placeholder="Valor del peaje (COP)"
              className="input-base"
              value={formData.valor || ''}
              onChange={(e) => setFormData({ ...formData, valor: parseFloat(e.target.value) })}
              step="0.01"
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

      {isLoading && (
        <div className="flex items-center justify-center py-8"><Loader className="animate-spin" /></div>
      )}

      {!isLoading && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Nombre</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Sector</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Valor</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {peajes.map((peaje: any) => (
                <tr key={peaje.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm font-medium text-neutral-900">{peaje.nombre}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{peaje.sector}</td>
                  <td className="px-4 py-3 text-sm font-medium text-neutral-900">
                    ${peaje.valor.toLocaleString('es-CO', { minimumFractionDigits: 2 })}
                  </td>
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

      {!isLoading && peajes.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay peajes registrados. Crea uno nuevo para comenzar.</p>
        </div>
      )}
    </div>
  );
}
