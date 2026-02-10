import { useState, Fragment } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { AlertCircle, Plus, Loader, X } from 'lucide-react';
import { formatKm } from '../../utils/format';
import { useAuth } from '../../context/AuthContext';

interface FormDataRuta {
  nombre: string;
  descripcion: string;
  cliente_id: number;
}

export default function RutasModule() {
  const { usuario } = useAuth();
  const canManageRutas = usuario?.rol?.nombre === 'admin' || usuario?.rol?.nombre === 'super_admin';
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataRuta>({
    nombre: '',
    descripcion: '',
    cliente_id: 0,
  });
  const [error, setError] = useState('');
  const [activeRutaId, setActiveRutaId] = useState<number | null>(null);
  const [selectedTramoId, setSelectedTramoId] = useState<number | ''>('');
  const [orden, setOrden] = useState<number>(1);
  const [tramosModalRuta, setTramosModalRuta] = useState<any | null>(null);
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

  const { data: tramos = [] } = useQuery({
    queryKey: ['tramos'],
    queryFn: async () => {
      const data = await api.getTramos();
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

  const addTramoMutation = useMutation({
    mutationFn: ({ rutaId, tramoId, orden }: { rutaId: number; tramoId: number; orden: number }) =>
      api.addTramoToRuta(rutaId, tramoId, orden),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rutas'] });
      setSelectedTramoId('');
      setOrden(1);
      setActiveRutaId(null);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al agregar tramo a la ruta');
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

  const handleAddTramo = (rutaId: number) => {
    setActiveRutaId((prev) => (prev === rutaId ? null : rutaId));
    setSelectedTramoId('');
    setOrden(1);
  };

  const handleSubmitTramo = (rutaId: number) => {
    if (!selectedTramoId) {
      setError('Selecciona un tramo');
      return;
    }
    if (!orden || orden <= 0) {
      setError('El orden debe ser mayor a 0');
      return;
    }
    addTramoMutation.mutate({ rutaId, tramoId: Number(selectedTramoId), orden });
  };

  if (isLoading) {
    return <div className="flex items-center justify-center py-8"><Loader className="animate-spin" /></div>;
  }

  return (
    <div className="space-y-6">
      {canManageRutas && (
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center gap-2"
          title="Crear ruta"
        >
          <Plus className="w-5 h-5" />
          Nueva Ruta
        </button>
      )}

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showForm && canManageRutas && (
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
              <button type="submit" className="btn-primary" disabled={createMutation.isPending} title="Guardar ruta">
                {createMutation.isPending ? 'Guardando...' : 'Guardar'}
              </button>
              <button
                type="button"
                className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                onClick={() => setShowForm(false)}
                title="Cancelar"
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
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Tramos</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Estado</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {rutas.map((ruta: any) => {
              const cliente = clientes.find((c: any) => c.id === ruta.cliente_id);
              const tramoCount = Array.isArray(ruta.tramos) ? ruta.tramos.length : 0;

              return (
                <Fragment key={ruta.id}>
                  <tr className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3 text-sm font-medium text-neutral-900">{ruta.nombre}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600">{cliente?.nombre || 'N/A'}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600">
                      <button
                        type="button"
                        className="text-blue-600 hover:text-blue-700"
                        onClick={() => setTramosModalRuta(ruta)}
                        title="Ver tramos de la ruta"
                      >
                        {tramoCount}
                      </button>
                    </td>
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
                    <td className="px-4 py-3 text-right">
                      {canManageRutas && (
                        <button
                          type="button"
                          onClick={() => handleAddTramo(ruta.id)}
                          className="text-sm text-blue-600 hover:text-blue-700"
                          title="Agregar tramo a la ruta"
                        >
                          Agregar tramo a ruta
                        </button>
                      )}
                    </td>
                  </tr>
                  {canManageRutas && activeRutaId === ruta.id && (
                    <tr className="bg-neutral-50">
                      <td colSpan={5} className="px-4 py-4">
                        <div className="grid gap-3 sm:grid-cols-4 items-center">
                          <select
                            className="input-base sm:col-span-2"
                            value={selectedTramoId}
                            onChange={(e) => setSelectedTramoId(e.target.value ? Number(e.target.value) : '')}
                          >
                            <option value="">-- Selecciona un tramo --</option>
                            {tramos.map((tramo: any) => (
                              <option key={tramo.id} value={tramo.id}>
                                {tramo.origen} → {tramo.destino}
                              </option>
                            ))}
                          </select>
                          <input
                            type="number"
                            className="input-base"
                            min={1}
                            value={orden}
                            onChange={(e) => setOrden(Number(e.target.value))}
                            placeholder="Orden"
                          />
                          <div className="flex gap-2 justify-end">
                            <button
                              type="button"
                              className="btn-primary"
                              onClick={() => handleSubmitTramo(ruta.id)}
                              disabled={addTramoMutation.isPending}
                              title="Agregar tramo"
                            >
                              {addTramoMutation.isPending ? 'Guardando...' : 'Agregar'}
                            </button>
                            <button
                              type="button"
                              className="px-3 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                              onClick={() => setActiveRutaId(null)}
                              title="Cancelar"
                            >
                              Cancelar
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
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

      {tramosModalRuta && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full">
            <div className="flex items-center justify-between border-b px-6 py-4">
              <div>
                <h3 className="text-lg font-semibold text-neutral-900">Tramos de la ruta</h3>
                <p className="text-sm text-neutral-600">{tramosModalRuta.nombre}</p>
              </div>
              <button
                type="button"
                className="text-neutral-500 hover:text-neutral-700"
                onClick={() => setTramosModalRuta(null)}
                title="Cerrar"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              {(tramosModalRuta.tramos || []).length === 0 && (
                <p className="text-sm text-neutral-600">No hay tramos asignados.</p>
              )}
              {(tramosModalRuta.tramos || [])
                .slice()
                .sort((a: any, b: any) => a.orden - b.orden)
                .map((tramoRuta: any) => (
                  <div key={tramoRuta.id} className="border border-neutral-200 rounded-lg p-3 mb-3">
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-neutral-700">
                        <span className="font-semibold">Orden {tramoRuta.orden}</span>
                        <span className="mx-2">·</span>
                        {tramoRuta.tramo?.origen} → {tramoRuta.tramo?.destino}
                      </div>
                      <div className="text-sm text-neutral-500">
                        {formatKm(
                          (tramoRuta.tramo?.detalles || []).reduce(
                            (acc: number, detalle: any) => acc + Number(detalle.kilometros || 0),
                            0
                          )
                        )}{' '}
                        km
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
