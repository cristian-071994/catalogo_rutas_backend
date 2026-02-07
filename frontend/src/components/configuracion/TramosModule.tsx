import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { formatKm } from '../../utils/format';
import { AlertCircle, Plus, Loader, X, Edit2, Save } from 'lucide-react';

interface FormDataTramo {
  origen: string;
  destino: string;
}

interface TramoDetalleDraft {
  tipo_carga: string;
  tipo_terreno: string;
  kilometros: number | '';
}

const tipoCargaOptions = ['VACIO', 'CARGADO'];
const tipoTerrenoOptions = ['PLANO', 'ONDULADO', 'MONTAÑA', 'URBANO'];

export default function TramosModule() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormDataTramo>({
    origen: '',
    destino: '',
  });
  const [detalleDrafts, setDetalleDrafts] = useState<TramoDetalleDraft[]>([
    { tipo_carga: 'VACIO', tipo_terreno: 'PLANO', kilometros: '' },
  ]);
  const [peajeQuery, setPeajeQuery] = useState('');
  const [selectedPeajes, setSelectedPeajes] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [detailsTramo, setDetailsTramo] = useState<any | null>(null);
  const [editDetalleId, setEditDetalleId] = useState<number | null>(null);
  const [editDetalleData, setEditDetalleData] = useState<TramoDetalleDraft>({
    tipo_carga: 'VACIO',
    tipo_terreno: 'PLANO',
    kilometros: '',
  });
  const [editingTramo, setEditingTramo] = useState<any | null>(null);
  const [editTramoData, setEditTramoData] = useState<FormDataTramo>({
    origen: '',
    destino: '',
  });
  const queryClient = useQueryClient();

  const { data: tramos = [], isLoading } = useQuery({
    queryKey: ['tramos'],
    queryFn: async () => {
      const data = await api.getTramos();
      return data?.items || data || [];
    },
  });

  const { data: peajesSearch = [], isLoading: isSearchingPeajes } = useQuery({
    queryKey: ['peajes-search', peajeQuery],
    queryFn: () => api.buscarPeajesPorNombre(peajeQuery, 100),
    enabled: peajeQuery.trim().length > 0,
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createTramo(data),
  });

  const updateTramoMutation = useMutation({
    mutationFn: ({ tramoId, data }: { tramoId: number; data: FormDataTramo }) => api.updateTramo(tramoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tramos'] });
      setEditingTramo(null);
      setEditTramoData({ origen: '', destino: '' });
      setSuccess('Tramo actualizado exitosamente');
      setTimeout(() => setSuccess(''), 5000);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al actualizar tramo');
    },
  });

  const updateDetalleMutation = useMutation({
    mutationFn: ({ detalleId, data }: { detalleId: number; data: any }) => api.updateTramoDetalle(detalleId, data),
    onSuccess: (updatedDetalle) => {
      queryClient.invalidateQueries({ queryKey: ['tramos'] });
      if (detailsTramo) {
        setDetailsTramo({
          ...detailsTramo,
          detalles: (detailsTramo.detalles || []).map((detalle: any) =>
            detalle.id === updatedDetalle.id ? updatedDetalle : detalle
          ),
        });
      }
      setEditDetalleId(null);
      setSuccess('Detalle actualizado exitosamente');
      setTimeout(() => setSuccess(''), 5000);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al actualizar detalle');
    },
  });

  const handleAddDetalle = () => {
    if (detalleDrafts.length >= 4) return;
    setDetalleDrafts((prev) => [...prev, { tipo_carga: 'VACIO', tipo_terreno: 'PLANO', kilometros: '' }]);
  };

  const handleRemoveDetalle = (index: number) => {
    setDetalleDrafts((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleSelectPeaje = (peaje: any) => {
    if (selectedPeajes.some((item) => item.id === peaje.id)) return;
    setSelectedPeajes((prev) => [...prev, peaje]);
    setPeajeQuery('');
  };

  const handleRemovePeaje = (id: number) => {
    setSelectedPeajes((prev) => prev.filter((item) => item.id !== id));
  };

  const handleCancel = () => {
    setShowForm(false);
    setFormData({ origen: '', destino: '' });
    setDetalleDrafts([{ tipo_carga: 'VACIO', tipo_terreno: 'PLANO', kilometros: '' }]);
    setSelectedPeajes([]);
    setPeajeQuery('');
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.origen || !formData.destino) {
      setError('Origen y destino son requeridos');
      return;
    }
    if (detalleDrafts.length === 0) {
      setError('Debes agregar al menos un detalle de tramo');
      return;
    }

    for (const detalle of detalleDrafts) {
      if (!detalle.kilometros || Number(detalle.kilometros) <= 0) {
        setError('Cada detalle debe tener kilómetros mayores a 0');
        return;
      }
    }

    try {
      setError('');
      const nuevoTramo = await createMutation.mutateAsync({
        origen: formData.origen,
        destino: formData.destino,
        peaje_ids: selectedPeajes.map((peaje) => peaje.id),
      });

      await Promise.all(
        detalleDrafts.map((detalle) =>
          api.createTramoDetalle({
            tramo_id: nuevoTramo.id,
            tipo_carga: detalle.tipo_carga,
            tipo_terreno: detalle.tipo_terreno,
            kilometros: Number(detalle.kilometros),
          })
        )
      );

      queryClient.invalidateQueries({ queryKey: ['tramos'] });
      setSuccess('Tramo guardado exitosamente');
      setTimeout(() => setSuccess(''), 5000);
      handleCancel();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear tramo');
    }
  };

  const getDistanceKm = (detalles: any[]) => {
    const total = detalles.reduce((acc, detalle) => {
      const raw = detalle?.kilometros;
      const parsed = typeof raw === 'number' ? raw : Number(raw);
      const safe = Number.isFinite(parsed) ? parsed : parseFloat(String(raw));
      return acc + (Number.isFinite(safe) ? safe : 0);
    }, 0);
    return Number.isFinite(total) ? total : 0;
  };

  const handleOpenDetails = (tramo: any) => {
    setDetailsTramo(tramo);
    setEditDetalleId(null);
  };

  const handleEditDetalle = (detalle: any) => {
    setEditDetalleId(detalle.id);
    setEditDetalleData({
      tipo_carga: detalle.tipo_carga,
      tipo_terreno: detalle.tipo_terreno,
      kilometros: Number(detalle.kilometros),
    });
  };

  const handleSaveDetalle = (tramoId: number, detalleId: number) => {
    if (!editDetalleData.kilometros || Number(editDetalleData.kilometros) <= 0) {
      setError('Los kilómetros deben ser mayores a 0');
      return;
    }
    updateDetalleMutation.mutate({
      detalleId,
      data: {
        tramo_id: tramoId,
        tipo_carga: editDetalleData.tipo_carga,
        tipo_terreno: editDetalleData.tipo_terreno,
        kilometros: Number(editDetalleData.kilometros),
      },
    });
  };

  const handleEditTramo = (tramo: any) => {
    setEditingTramo(tramo);
    setEditTramoData({ origen: tramo.origen, destino: tramo.destino });
  };

  const handleSaveTramo = () => {
    if (!editingTramo) return;
    if (!editTramoData.origen || !editTramoData.destino) {
      setError('Origen y destino son requeridos');
      return;
    }
    updateTramoMutation.mutate({ tramoId: editingTramo.id, data: editTramoData });
  };

  return (
    <div className="space-y-6">
      <button
        onClick={() => setShowForm(!showForm)}
        className="btn-primary flex items-center gap-2"
        title="Crear tramo"
      >
        <Plus className="w-5 h-5" />
        Nuevo Tramo
      </button>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-green-600" />
          <p className="text-sm text-green-600">{success}</p>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nuevo Tramo</h3>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2">
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
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">Peajes del tramo</label>
              <input
                type="text"
                placeholder="Escribe para buscar peajes"
                className="input-base"
                value={peajeQuery}
                onChange={(e) => setPeajeQuery(e.target.value)}
              />
              {peajeQuery.trim().length > 0 && (
                <div className="max-h-48 overflow-y-auto border border-neutral-200 rounded-lg bg-white text-neutral-900 shadow-sm">
                  {isSearchingPeajes ? (
                    <div className="p-3 text-sm text-neutral-500">Buscando...</div>
                  ) : (
                    peajesSearch.map((peaje: any) => (
                      <button
                        type="button"
                        key={peaje.id}
                        onClick={() => handleSelectPeaje(peaje)}
                        className="w-full px-4 py-2 text-left text-sm !bg-white !text-neutral-900 hover:!bg-neutral-100"
                        style={{ backgroundColor: '#ffffff', color: '#111827' }}
                        title="Agregar peaje"
                      >
                        {peaje.nombre_peaje || 'Sin nombre'}
                      </button>
                    ))
                  )}
                  {!isSearchingPeajes && peajesSearch.length === 0 && (
                    <div className="p-3 text-sm text-neutral-500">Sin resultados</div>
                  )}
                </div>
              )}

              {selectedPeajes.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {selectedPeajes.map((peaje: any) => (
                    <span
                      key={peaje.id}
                      className="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium bg-blue-50 text-blue-700 rounded-full"
                    >
                      {peaje.nombre_peaje || 'Sin nombre'}
                      <button type="button" onClick={() => handleRemovePeaje(peaje.id)} title="Quitar peaje">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="block text-sm font-medium text-gray-700">Detalles del tramo</label>
                <button
                  type="button"
                  className="text-sm text-blue-600 hover:text-blue-700 disabled:text-gray-400"
                  onClick={handleAddDetalle}
                  disabled={detalleDrafts.length >= 4}
                  title="Agregar detalle"
                >
                  + Agregar detalle
                </button>
              </div>

              {detalleDrafts.map((detalle, index) => (
                <div key={index} className="grid gap-3 sm:grid-cols-4 items-center">
                  <select
                    className="input-base"
                    value={detalle.tipo_carga}
                    onChange={(e) => {
                      const value = e.target.value;
                      setDetalleDrafts((prev) =>
                        prev.map((item, idx) => (idx === index ? { ...item, tipo_carga: value } : item))
                      );
                    }}
                  >
                    {tipoCargaOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                  <select
                    className="input-base"
                    value={detalle.tipo_terreno}
                    onChange={(e) => {
                      const value = e.target.value;
                      setDetalleDrafts((prev) =>
                        prev.map((item, idx) => (idx === index ? { ...item, tipo_terreno: value } : item))
                      );
                    }}
                  >
                    {tipoTerrenoOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    placeholder="Kilómetros"
                    className="input-base"
                    value={detalle.kilometros}
                    onChange={(e) => {
                      const value = e.target.value ? Number(e.target.value) : '';
                      setDetalleDrafts((prev) =>
                        prev.map((item, idx) => (idx === index ? { ...item, kilometros: value } : item))
                      );
                    }}
                    step="0.1"
                    min="0"
                  />
                  <div className="flex justify-end">
                    <button
                      type="button"
                      className="text-sm text-red-600 hover:text-red-700 disabled:text-gray-400"
                      onClick={() => handleRemoveDetalle(index)}
                      disabled={detalleDrafts.length === 1}
                      title="Quitar detalle"
                    >
                      Quitar
                    </button>
                  </div>
                </div>
              ))}
              <p className="text-xs text-neutral-500">Máximo 4 detalles por tramo.</p>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="btn-primary"
                disabled={createMutation.isPending}
                title="Guardar tramo"
              >
                {createMutation.isPending ? 'Guardando...' : 'Guardar'}
              </button>
              <button
                type="button"
                className="px-3 py-2 border border-gray-300 !bg-white !text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                onClick={handleCancel}
                title="Cancelar"
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
        <div className="max-h-[400px] overflow-y-auto border border-neutral-200 rounded-lg">
          <table className="w-full">
            <thead className="sticky top-0 bg-white">
              <tr className="border-b border-neutral-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Origen → Destino</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Distancia (km)</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Detalles</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tramos.map((tramo: any) => {
                const distancia = getDistanceKm(tramo.detalles || []);
                return (
                  <tr key={tramo.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3 text-sm text-neutral-900">
                      {tramo.origen} → {tramo.destino}
                    </td>
                    <td className="px-4 py-3 text-sm text-neutral-600">{formatKm(distancia)} km</td>
                    <td className="px-4 py-3 text-sm text-neutral-600">
                      <button
                        type="button"
                        className="text-blue-600 hover:text-blue-700"
                        onClick={() => handleOpenDetails(tramo)}
                        title="Ver detalles del tramo"
                      >
                        {tramo.detalles?.length || 0} detalle(s)
                      </button>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        type="button"
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        onClick={() => handleEditTramo(tramo)}
                        title="Editar tramo"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {!isLoading && tramos.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay tramos registrados. Crea uno nuevo para comenzar.</p>
        </div>
      )}

      {detailsTramo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full">
            <div className="flex items-center justify-between border-b px-6 py-4">
              <div>
                <h3 className="text-lg font-semibold text-neutral-900">Detalles del tramo</h3>
                <p className="text-sm text-neutral-600">
                  {detailsTramo.origen} → {detailsTramo.destino}
                </p>
              </div>
              <button
                type="button"
                className="text-neutral-500 hover:text-neutral-700"
                onClick={() => setDetailsTramo(null)}
                title="Cerrar"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              {(detailsTramo.detalles || []).length === 0 && (
                <p className="text-sm text-neutral-600">No hay detalles registrados.</p>
              )}
              {(detailsTramo.detalles || []).map((detalle: any) => (
                <div key={detalle.id} className="border border-neutral-200 rounded-lg p-4">
                  {editDetalleId === detalle.id ? (
                    <div className="grid gap-3 sm:grid-cols-4 items-center">
                      <select
                        className="input-base"
                        value={editDetalleData.tipo_carga}
                        onChange={(e) => setEditDetalleData((prev) => ({ ...prev, tipo_carga: e.target.value }))}
                      >
                        {tipoCargaOptions.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                      <select
                        className="input-base"
                        value={editDetalleData.tipo_terreno}
                        onChange={(e) => setEditDetalleData((prev) => ({ ...prev, tipo_terreno: e.target.value }))}
                      >
                        {tipoTerrenoOptions.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        className="input-base"
                        value={editDetalleData.kilometros}
                        onChange={(e) =>
                          setEditDetalleData((prev) => ({
                            ...prev,
                            kilometros: e.target.value ? Number(e.target.value) : '',
                          }))
                        }
                        step="0.1"
                        min="0"
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          className="btn-primary"
                          onClick={() => handleSaveDetalle(detailsTramo.id, detalle.id)}
                          title="Guardar detalle"
                        >
                          <Save className="w-4 h-4" />
                        </button>
                        <button
                          type="button"
                          className="px-3 py-2 border border-gray-300 !bg-white !text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                          onClick={() => setEditDetalleId(null)}
                          title="Cancelar"
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-neutral-700">
                        <span className="font-medium">{detalle.tipo_carga}</span> · {detalle.tipo_terreno} · {formatKm(detalle.kilometros)} km
                      </div>
                      <button
                        type="button"
                        className="text-blue-600 hover:text-blue-700"
                        onClick={() => handleEditDetalle(detalle)}
                        title="Editar detalle"
                      >
                        Editar
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {editingTramo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full">
            <div className="flex items-center justify-between border-b px-6 py-4">
              <h3 className="text-lg font-semibold text-neutral-900">Editar tramo</h3>
              <button
                type="button"
                className="text-neutral-500 hover:text-neutral-700"
                onClick={() => setEditingTramo(null)}
                title="Cerrar"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <input
                type="text"
                className="input-base"
                value={editTramoData.origen}
                onChange={(e) => setEditTramoData((prev) => ({ ...prev, origen: e.target.value }))}
                placeholder="Origen"
              />
              <input
                type="text"
                className="input-base"
                value={editTramoData.destino}
                onChange={(e) => setEditTramoData((prev) => ({ ...prev, destino: e.target.value }))}
                placeholder="Destino"
              />
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  className="btn-primary"
                  onClick={handleSaveTramo}
                  title="Guardar cambios"
                >
                  Guardar
                </button>
                <button
                  type="button"
                  className="px-3 py-2 border border-gray-300 !bg-white !text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                  onClick={() => setEditingTramo(null)}
                  title="Cancelar"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
