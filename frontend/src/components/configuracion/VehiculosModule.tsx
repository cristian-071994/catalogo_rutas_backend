import { useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import ConfirmDialog from '../ConfirmDialog';
import { AlertCircle, Plus, Trash2, Loader, Edit2, CheckCircle, Upload, Download } from 'lucide-react';

interface FormDataVehiculo {
  placa: string;
  configuracion_id: number;
}

export default function VehiculosModule() {
  const { usuario: currentUser } = useAuth();
  const isSuperAdmin = currentUser?.rol?.nombre === 'super_admin';
  const isAdmin = currentUser?.rol?.nombre === 'admin';
  const canManage = isAdmin || isSuperAdmin;

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedVehiculoId, setSelectedVehiculoId] = useState<number | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showActivateConfirm, setShowActivateConfirm] = useState(false);
  const [formData, setFormData] = useState<FormDataVehiculo>({
    placa: '',
    configuracion_id: 0,
  });
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  const [uploadError, setUploadError] = useState('');
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { data: vehiculos = [], isLoading } = useQuery({
    queryKey: ['vehiculos'],
    queryFn: async () => {
      const data = await api.getVehiculos(canManage);
      return data?.items || data || [];
    },
  });

  const { data: configs = [] } = useQuery({
    queryKey: ['configuracion-vehiculos'],
    queryFn: async () => {
      const data = await api.getConfiguracionVehiculos();
      return data?.items || data || [];
    },
  });

  const { data: marcas = [] } = useQuery({
    queryKey: ['marcas'],
    queryFn: async () => {
      const data = await api.getMarcas();
      return data?.items || data || [];
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: FormDataVehiculo) => api.createVehiculo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] });
      setFormData({ placa: '', configuracion_id: 0 });
      setShowForm(false);
      setEditingId(null);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al crear vehículo');
      setTimeout(() => setError(''), 10000);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: FormDataVehiculo }) => api.updateVehiculo(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] });
      setFormData({ placa: '', configuracion_id: 0 });
      setShowForm(false);
      setEditingId(null);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al actualizar vehículo');
      setTimeout(() => setError(''), 10000);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteVehiculo(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] });
      setShowDeleteConfirm(false);
      setSelectedVehiculoId(null);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al eliminar vehículo');
      setTimeout(() => setError(''), 10000);
    },
  });

  const activateMutation = useMutation({
    mutationFn: (id: number) => api.updateVehiculo(id, { estado: 'activo' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] });
      setShowActivateConfirm(false);
      setSelectedVehiculoId(null);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error al activar vehículo');
      setTimeout(() => setError(''), 10000);
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.uploadVehiculosMasivo(file),
    onSuccess: (data) => {
      setUploadResult(data);
      setUploadError('');
      setPreviewOpen(false);
      setPreviewData(null);
      setSelectedFile(null);
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] });
      queryClient.invalidateQueries({ queryKey: ['configuracion-vehiculos'] });
      queryClient.invalidateQueries({ queryKey: ['marcas'] });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    onError: (err: any) => {
      setUploadResult(null);
      setUploadError(err.response?.data?.detail || 'Error al cargar el archivo');
    },
  });

  const previewMutation = useMutation({
    mutationFn: (file: File) => api.previewVehiculosMasivo(file),
    onSuccess: (data) => {
      setPreviewData(data);
      setPreviewOpen(true);
      setUploadError('');
    },
    onError: (err: any) => {
      setPreviewData(null);
      setPreviewOpen(false);
      setUploadError(err.response?.data?.detail || 'Error al generar la vista previa');
    },
  });

  const handleDownloadTemplate = async () => {
    try {
      const blob = await api.downloadVehiculosTemplate();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'plantilla_vehiculos.xlsx';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setUploadResult(null);
      setUploadError(err.response?.data?.detail || 'Error al descargar la plantilla');
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.placa || !formData.configuracion_id) {
      setError('Todos los campos son requeridos');
      return;
    }
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: formData });
      return;
    }
    createMutation.mutate(formData);
  };

  const handleEdit = (vehiculo: any) => {
    setEditingId(vehiculo.id);
    setFormData({
      placa: vehiculo.placa,
      configuracion_id: vehiculo.configuracion_id,
    });
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({ placa: '', configuracion_id: 0 });
  };

  const handleDeleteClick = (id: number) => {
    setSelectedVehiculoId(id);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = () => {
    if (selectedVehiculoId) {
      deleteMutation.mutate(selectedVehiculoId);
    }
  };

  const handleActivateClick = (id: number) => {
    setSelectedVehiculoId(id);
    setShowActivateConfirm(true);
  };

  const confirmActivate = () => {
    if (selectedVehiculoId) {
      activateMutation.mutate(selectedVehiculoId);
    }
  };

  const isActive = (estado: any) => estado === 'activo' || estado === 1 || estado === true;

  if (isLoading) {
    return <div className="flex items-center justify-center py-8"><Loader className="animate-spin" /></div>;
  }

  return (
    <div className="space-y-6">
      {canManage && (
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => {
              if (showForm) {
                handleCancelForm();
                return;
              }
              setShowForm(true);
            }}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Nuevo Vehículo
          </button>

          <button
            type="button"
            onClick={handleDownloadTemplate}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="w-5 h-5" />
            Descargar plantilla
          </button>

          <label className="flex items-center gap-2 px-4 py-2 rounded-lg border border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100 cursor-pointer">
            <Upload className="w-5 h-5" />
            Carga masiva (Excel)
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  setSelectedFile(file);
                  previewMutation.mutate(file);
                }
              }}
            />
          </label>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {uploadError && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-600">{uploadError}</p>
        </div>
      )}

      {uploadResult && (
        <div className="border border-emerald-200 bg-emerald-50 rounded-lg p-4 text-sm text-emerald-900">
          <p className="font-semibold mb-2">Carga masiva completada</p>
          <p>Creado: {uploadResult.creados} / Total: {uploadResult.total}</p>
          {Array.isArray(uploadResult.omitidos) && uploadResult.omitidos.length > 0 && (
            <div className="mt-2">
              <p className="font-medium">Omitidos</p>
              <ul className="list-disc list-inside text-emerald-900">
                {uploadResult.omitidos.slice(0, 5).map((item: any, idx: number) => (
                  <li key={`${item.placa}-${idx}`}>
                    Fila {item.fila}: {item.placa} - {item.mensaje}
                  </li>
                ))}
              </ul>
              {uploadResult.omitidos.length > 5 && (
                <p className="text-xs text-emerald-800 mt-1">Se omitieron {uploadResult.omitidos.length} en total.</p>
              )}
            </div>
          )}
          {Array.isArray(uploadResult.errores) && uploadResult.errores.length > 0 && (
            <div className="mt-2">
              <p className="font-medium text-rose-700">Errores</p>
              <ul className="list-disc list-inside text-rose-700">
                {uploadResult.errores.slice(0, 5).map((item: any, idx: number) => (
                  <li key={`err-${idx}`}>Fila {item.fila}: {item.mensaje}</li>
                ))}
              </ul>
              {uploadResult.errores.length > 5 && (
                <p className="text-xs text-rose-600 mt-1">Hay {uploadResult.errores.length} errores en total.</p>
              )}
            </div>
          )}
        </div>
      )}

      {previewOpen && previewData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Vista previa de carga masiva</h3>
                <p className="text-sm text-gray-600">Revisa lo que se va a crear u omitir antes de continuar.</p>
              </div>
              <button
                onClick={() => {
                  setPreviewOpen(false);
                  setPreviewData(null);
                  setSelectedFile(null);
                }}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
              >
                Cerrar
              </button>
            </div>

            <div className="px-6 py-4 grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
              <div className="rounded-lg border border-gray-200 p-3">
                <p className="text-xs text-gray-500">Total</p>
                <p className="font-semibold text-gray-900">{previewData.total}</p>
              </div>
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
                <p className="text-xs text-emerald-700">Crear</p>
                <p className="font-semibold text-emerald-900">{previewData.crear}</p>
              </div>
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
                <p className="text-xs text-amber-700">Omitidos</p>
                <p className="font-semibold text-amber-900">{previewData.omitidos}</p>
              </div>
              <div className="rounded-lg border border-rose-200 bg-rose-50 p-3">
                <p className="text-xs text-rose-700">Errores</p>
                <p className="font-semibold text-rose-900">{previewData.errores}</p>
              </div>
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
                <p className="text-xs text-blue-700">Nuevas marcas/config</p>
                <p className="font-semibold text-blue-900">
                  {previewData.nuevas_marcas} / {previewData.nuevas_configuraciones}
                </p>
              </div>
            </div>

            <div className="px-6 pb-4 max-h-[360px] overflow-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-white border-b border-gray-200">
                  <tr>
                    <th className="text-left px-3 py-2">Fila</th>
                    <th className="text-left px-3 py-2">Placa</th>
                    <th className="text-left px-3 py-2">Marca</th>
                    <th className="text-left px-3 py-2">Modelo</th>
                    <th className="text-left px-3 py-2">Accion</th>
                    <th className="text-left px-3 py-2">Detalle</th>
                  </tr>
                </thead>
                <tbody>
                  {previewData.items?.map((item: any, idx: number) => (
                    <tr key={`${item.fila}-${idx}`} className="border-b border-gray-100">
                      <td className="px-3 py-2">{item.fila}</td>
                      <td className="px-3 py-2 font-semibold text-gray-900">{item.placa || '-'}</td>
                      <td className="px-3 py-2">{item.marca || '-'}</td>
                      <td className="px-3 py-2">{item.modelo || '-'}</td>
                      <td className="px-3 py-2">
                        {item.accion === 'crear' && (
                          <span className="px-2 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">Crear</span>
                        )}
                        {item.accion === 'omitir' && (
                          <span className="px-2 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">Omitir</span>
                        )}
                        {item.accion === 'error' && (
                          <span className="px-2 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800">Error</span>
                        )}
                      </td>
                      <td className="px-3 py-2 text-gray-600">{item.mensaje}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => {
                  setPreviewOpen(false);
                  setPreviewData(null);
                  setSelectedFile(null);
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={() => {
                  if (selectedFile) {
                    uploadMutation.mutate(selectedFile);
                  }
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Confirmar y cargar
              </button>
            </div>
          </div>
        </div>
      )}

      {showForm && (
        <div className="border border-neutral-200 rounded-lg p-6 bg-neutral-50">
          <h3 className="font-semibold text-neutral-900 mb-4">
            {editingId ? 'Editar Vehículo' : 'Crear Nuevo Vehículo'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Placa (ej: ABC123)"
              className="input-base"
              value={formData.placa}
              onChange={(e) => setFormData({ ...formData, placa: e.target.value.toUpperCase() })}
              required
            />
            <select
              className="input-base"
              value={formData.configuracion_id || ''}
              onChange={(e) => setFormData({ ...formData, configuracion_id: Number(e.target.value) })}
              required
            >
              <option value="">-- Selecciona una configuración --</option>
              {configs.map((config: any) => {
                const marca = marcas.find((m: any) => m.id === config.marca_id);
                return (
                  <option key={config.id} value={config.id}>
                    {marca?.nombre || 'Desconocido'} - {config.modelo}
                  </option>
                );
              })}
            </select>
            <div className="flex gap-2">
              <button
                type="submit"
                className="btn-primary"
                disabled={createMutation.isPending || updateMutation.isPending}
              >
                {createMutation.isPending || updateMutation.isPending ? 'Guardando...' : 'Guardar'}
              </button>
              <button
                type="button"
                className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                onClick={handleCancelForm}
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
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Placa</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Configuración</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Estado</th>
              {canManage && (
                <th className="px-4 py-3 text-right text-sm font-semibold text-neutral-700">Acciones</th>
              )}
            </tr>
          </thead>
          <tbody>
            {vehiculos.map((vehiculo: any) => {
              const config = configs.find((c: any) => c.id === vehiculo.configuracion_id);
              const marca = marcas.find((m: any) => m.id === config?.marca_id);
              const active = isActive(vehiculo.estado);
              
              return (
                <tr key={vehiculo.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm font-medium text-neutral-900">{vehiculo.placa}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">
                    {marca?.nombre || 'N/A'} - {config?.modelo || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {active ? (
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                        Activo
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                        Inactivo
                      </span>
                    )}
                  </td>
                  {canManage && (
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {!active ? (
                          <button
                            onClick={() => handleActivateClick(vehiculo.id)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Activar"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                        ) : (
                          <>
                            <button
                              onClick={() => handleEdit(vehiculo)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Editar"
                            >
                              <Edit2 className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleDeleteClick(vehiculo.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Eliminar"
                            >
                              <Trash2 className="w-5 h-5" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {!isLoading && vehiculos.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          No hay vehículos registrados
        </div>
      )}

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Eliminar Vehículo"
        message="¿Estás seguro de eliminar este vehículo? Esta acción lo dejará inactivo."
        type="danger"
        confirmText="Eliminar"
        cancelText="Cancelar"
        onConfirm={confirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />

      <ConfirmDialog
        isOpen={showActivateConfirm}
        title="Activar Vehículo"
        message="¿Estás seguro de activar este vehículo?"
        type="success"
        confirmText="Activar"
        cancelText="Cancelar"
        onConfirm={confirmActivate}
        onCancel={() => setShowActivateConfirm(false)}
      />
    </div>
  );
}
