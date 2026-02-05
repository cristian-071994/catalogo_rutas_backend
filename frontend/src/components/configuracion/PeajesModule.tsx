import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, RefreshCw, Loader } from 'lucide-react';

export default function PeajesModule() {
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const queryClient = useQueryClient();

  const { data: peajes = [], isLoading } = useQuery({
    queryKey: ['peajes'],
    queryFn: async () => {
      const response = await api.getPeajes();
      return response.data?.items || response.data || [];
    },
  });

  const sincronizarMutation = useMutation({
    mutationFn: () => api.sincronizarPeajes(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['peajes'] });
      setSuccessMessage('Sincronización completada exitosamente');
      setError('');
      setTimeout(() => setSuccessMessage(''), 5000);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al sincronizar con la ANI');
      setTimeout(() => setError(''), 10000);
    },
  });

  const handleSincronizar = () => {
    sincronizarMutation.mutate();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-neutral-900">Peajes</h3>
        <button
          onClick={handleSincronizar}
          className="btn-primary flex items-center gap-2"
          disabled={sincronizarMutation.isPending}
        >
          <RefreshCw className={`w-5 h-5 ${sincronizarMutation.isPending ? 'animate-spin' : ''}`} />
          {sincronizarMutation.isPending ? 'Sincronizando...' : 'Consultar ANI'}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {successMessage && (
        <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-green-600" />
          <p className="text-sm text-green-600">{successMessage}</p>
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader className="animate-spin" />
        </div>
      )}

      {!isLoading && (
        <div className="max-h-[400px] overflow-y-auto border border-neutral-200 rounded-lg">
          <table className="w-full">
            <thead className="sticky top-0 bg-white">
              <tr className="border-b border-neutral-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Nombre Peaje</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Categoría Tarifa</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Costo</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Última Actualización</th>
              </tr>
            </thead>
            <tbody>
              {peajes.map((peaje: any) => (
                <tr key={peaje.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm font-medium text-neutral-900">{peaje.nombre_peaje || 'N/A'}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{peaje.categoria_tarifa || 'N/A'}</td>
                  <td className="px-4 py-3 text-right text-sm font-medium text-neutral-900">
                    ${(peaje.costo || 0).toLocaleString('es-CO', { minimumFractionDigits: 0 })}
                  </td>
                  <td className="px-4 py-3 text-sm text-neutral-600">
                    {peaje.ultima_actualizacion 
                      ? new Date(peaje.ultima_actualizacion).toLocaleString('es-CO', {
                          timeZone: 'America/Bogota',
                          year: 'numeric',
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        })
                      : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!isLoading && peajes.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          No hay peajes registrados. Haz clic en "Consultar ANI" para sincronizar.
        </div>
      )}
    </div>
  );
}
