import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { AlertCircle, Plus, Loader, Edit2, Save, X } from 'lucide-react';

interface FormDataRendimiento {
  configuracion_id: number | '';
  tipo_carga: string;
  tipo_terreno: string;
  rendimiento_km_galon: number | '';
}

export default function RendimientoModule() {
  const { usuario: currentUser } = useAuth();
  const isSuperAdmin = currentUser?.rol?.nombre === 'super_admin';
  
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editRendimiento, setEditRendimiento] = useState<number | ''>('');
  const [formData, setFormData] = useState<FormDataRendimiento>({
    configuracion_id: '',
    tipo_carga: 'VACIO',
    tipo_terreno: 'PLANO',
    rendimiento_km_galon: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const queryClient = useQueryClient();

  const { data: configs = [] } = useQuery({
    queryKey: ['configuracion-vehiculos'],
    queryFn: () => api.getConfiguracionVehiculos(),
  });

  const { data: marcas = [] } = useQuery({
    queryKey: ['marcas'],
    queryFn: () => api.getMarcas(),
  });

  const { data: rendimientos = [], isLoading } = useQuery({
    queryKey: ['rendimiento'],
    queryFn: () => api.getRendimientos(),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createRendimiento(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rendimiento'] });
      setFormData({ configuracion_id: '', tipo_carga: 'VACIO', tipo_terreno: 'PLANO', rendimiento_km_galon: '' });
      setShowForm(false);
      setError('');
      setSuccess('Rendimiento creado correctamente');
      setTimeout(() => setSuccess(''), 5000);
    },
    onError: (err: any) => {
      if (err.response?.status === 403) {
        setError('No estás autorizado para ejecutar esta acción');
      } else {
        setError(err.response?.data?.detail || 'Error al crear rendimiento');
      }
      setTimeout(() => setError(''), 10000);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => api.updateRendimiento(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rendimiento'] });
      setEditingId(null);
      setEditRendimiento('');
      setError('');
      setSuccess('Rendimiento actualizado correctamente');
      setTimeout(() => setSuccess(''), 5000);
    },
    onError: (err: any) => {
      if (err.response?.status === 403) {
        setError('No estás autorizado para ejecutar esta acción. Solo super administradores pueden editar.');
      } else {
        setError(err.response?.data?.detail || 'Error al actualizar rendimiento');
      }
      setTimeout(() => setError(''), 10000);
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.configuracion_id || !formData.rendimiento_km_galon) {
      setError('Todos los campos son requeridos');
      setTimeout(() => setError(''), 10000);
      return;
    }
    createMutation.mutate({
      configuracion_id: Number(formData.configuracion_id),
      tipo_carga: formData.tipo_carga,
      tipo_terreno: formData.tipo_terreno,
      rendimiento_km_galon: Number(formData.rendimiento_km_galon)
    });
  };

  const handleEdit = (id: number, currentRendimiento: number) => {
    setEditingId(id);
    setEditRendimiento(currentRendimiento);
  };

  const handleSaveEdit = (id: number) => {
    if (!editRendimiento) {
      setError('El rendimiento es requerido');
      setTimeout(() => setError(''), 10000);
      return;
    }
    updateMutation.mutate({ 
      id, 
      data: { rendimiento_km_galon: Number(editRendimiento) } 
    });
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditRendimiento('');
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

      {success && (
        <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-green-600" />
          <p className="text-sm text-green-600">{success}</p>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">Crear Nuevo Rendimiento</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Configuración *</label>
              <select
                className="input-base"
                value={formData.configuracion_id}
                onChange={(e) => setFormData({ ...formData, configuracion_id: e.target.value ? Number(e.target.value) : '' })}
                required
              >
                <option value="">Selecciona una configuración</option>
                {configs.map((config: any) => {
                  const marca = marcas.find((m: any) => m.id === config.marca_id);
                  return (
                    <option key={config.id} value={config.id}>
                      {marca?.nombre || 'Desconocida'} - Modelo {config.modelo}
                    </option>
                  );
                })}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Carga *</label>
              <select
                className="input-base"
                value={formData.tipo_carga}
                onChange={(e) => setFormData({ ...formData, tipo_carga: e.target.value })}
                required
              >
                <option value="VACIO">VACÍO</option>
                <option value="CARGADO">CARGADO</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Terreno *</label>
              <select
                className="input-base"
                value={formData.tipo_terreno}
                onChange={(e) => setFormData({ ...formData, tipo_terreno: e.target.value })}
                required
              >
                <option value="PLANO">PLANO</option>
                <option value="ONDULADO">ONDULADO</option>
                <option value="MONTAÑA">MONTAÑA</option>
                <option value="URBANO">URBANO</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Rendimiento (km/galón) *</label>
              <input
                type="number"
                placeholder="12.5"
                className="input-base"
                value={formData.rendimiento_km_galon || ''}
                onChange={(e) => setFormData({ ...formData, rendimiento_km_galon: e.target.value ? Number(e.target.value) : '' })}
                step="0.1"
                min="0"
                required
              />
            </div>
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
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Configuración</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Carga</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Terreno</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Rendimiento (km/gal)</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Estado</th>
              {isSuperAdmin && (
                <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
              )}
            </tr>
          </thead>
          <tbody>
            {rendimientos.map((rendimiento: any) => {
              const config = configs.find((c: any) => c.id === rendimiento.configuracion_id);
              const marca = marcas.find((m: any) => m.id === config?.marca_id);
              const isEditing = editingId === rendimiento.id;
              
              return (
                <tr key={rendimiento.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm text-neutral-900">
                    {marca?.nombre || 'Desconocida'} - Modelo {config?.modelo || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{rendimiento.tipo_carga}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{rendimiento.tipo_terreno}</td>
                  <td className="px-4 py-3 text-sm text-neutral-900">
                    {isEditing ? (
                      <input
                        type="number"
                        className="w-24 px-2 py-1 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500"
                        value={editRendimiento}
                        onChange={(e) => setEditRendimiento(e.target.value ? Number(e.target.value) : '')}
                        step="0.1"
                        min="0"
                      />
                    ) : (
                      parseFloat(rendimiento.rendimiento_km_galon).toFixed(1)
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      rendimiento.estado === 'activo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {rendimiento.estado}
                    </span>
                  </td>
                  {isSuperAdmin && (
                    <td className="px-4 py-3 text-right">
                      {isEditing ? (
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => handleSaveEdit(rendimiento.id)}
                            className="p-1 text-green-600 hover:bg-green-50 rounded"
                            title="Guardar"
                          >
                            <Save className="w-4 h-4" />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="p-1 text-gray-600 hover:bg-gray-50 rounded"
                            title="Cancelar"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleEdit(rendimiento.id, parseFloat(rendimiento.rendimiento_km_galon))}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                          title="Editar"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {rendimientos.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No hay rendimientos registrados. Crea uno nuevo para comenzar.</p>
        </div>
      )}
    </div>
  );
}
