import { useState, useEffect } from 'react';
import { Building2, Plus, Edit2, Save, X, AlertCircle, CheckCircle, Trash2, Users, RefreshCw } from 'lucide-react';
import axiosInstance from '../../services/axiosInstance';
import ConfirmDialog from '../ConfirmDialog';
import PasswordInput from '../PasswordInput';


interface Empresa {
  id: number;
  nombre: string;
  nit: string;
  direccion: string;
  telefono: string;
  email: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

export default function EmpresasModule() {
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  
  // Estados para ConfirmDialog
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showActivateConfirm, setShowActivateConfirm] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  
  // Form state
  const [formData, setFormData] = useState({
    empresa_nombre: '',
    empresa_nit: '',
    empresa_contacto: '',
    empresa_telefono: '',
    empresa_email: '',
    admin_nombre: '',
    admin_email: '',
    admin_password: '',
  });

  useEffect(() => {
    loadEmpresas();
  }, []);

  const loadEmpresas = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/empresas/');
      console.log('Empresas recibidas:', response.data);
      setEmpresas(Array.isArray(response.data) ? response.data : []);
      setError('');
    } catch (err: any) {
      console.error('Error al cargar empresas:', err);
      setError(err.response?.data?.detail || 'Error al cargar empresas');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingId) {
        // Actualizar - solo datos de la empresa
        const updatePayload = {
          nombre: formData.empresa_nombre,
          nit: formData.empresa_nit,
          contacto: formData.empresa_contacto,
          telefono: formData.empresa_telefono,
          email: formData.empresa_email,
        };
        await axiosInstance.put(`/empresas/${editingId}`, updatePayload);
        setSuccess('Empresa actualizada correctamente');
      } else {
        // Crear - requiere datos del admin también
        await axiosInstance.post('/empresas/', formData);
        setSuccess('Empresa y administrador creados correctamente');
      }

      resetForm();
      loadEmpresas();
    } catch (err: any) {
      console.error('Error al guardar empresa:', err.response?.data);
      setError(err.response?.data?.detail || 'Error al guardar la empresa');
    }
  };

  const handleEdit = (empresa: Empresa) => {
    setFormData({
      empresa_nombre: empresa.nombre,
      empresa_nit: empresa.nit,
      empresa_contacto: empresa.direccion,
      empresa_telefono: empresa.telefono,
      empresa_email: empresa.email,
      admin_nombre: '',
      admin_email: '',
      admin_password: '',
    });
    setEditingId(empresa.id);
    setShowForm(true);
  };

  const handleDeleteClick = (id: number) => {
    setSelectedId(id);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!selectedId) return;

    try {
      await axiosInstance.delete(`/empresas/${selectedId}`);
      setSuccess('Empresa desactivada correctamente');
      loadEmpresas();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al desactivar la empresa');
    } finally {
      setShowDeleteConfirm(false);
      setSelectedId(null);
    }
  };

  const handleActivateClick = (id: number) => {
    setSelectedId(id);
    setShowActivateConfirm(true);
  };

  const confirmActivate = async () => {
    if (!selectedId) return;

    try {
      await axiosInstance.put(`/empresas/${selectedId}`, { activo: true });
      setSuccess('Empresa reactivada correctamente');
      loadEmpresas();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al reactivar la empresa');
    } finally {
      setShowActivateConfirm(false);
      setSelectedId(null);
    }
  };

  const resetForm = () => {
    setFormData({
      empresa_nombre: '',
      empresa_nit: '',
      empresa_contacto: '',
      empresa_telefono: '',
      empresa_email: '',
      admin_nombre: '',
      admin_email: '',
      admin_password: '',
    });
    setEditingId(null);
    setShowForm(false);
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-gray-600 mt-4">Cargando empresas...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🏢 Gestión de Empresas</h2>
          <p className="text-gray-600 mt-1">Administra las empresas registradas en el sistema</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          {showForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
          {showForm ? 'Cancelar' : 'Nueva Empresa'}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-xl">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
          <p className="text-sm text-green-600">{success}</p>
        </div>
      )}

      {/* Formulario */}
      {showForm && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingId ? 'Editar Empresa' : 'Nueva Empresa con Administrador'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Datos de la Empresa */}
            <div>
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Building2 className="w-5 h-5" />
                Datos de la Empresa
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de la Empresa *
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={formData.empresa_nombre}
                    onChange={(e) => setFormData({ ...formData, empresa_nombre: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    NIT *
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={formData.empresa_nit}
                    onChange={(e) => setFormData({ ...formData, empresa_nit: e.target.value })}
                    required
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Persona de Contacto
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={formData.empresa_contacto}
                    onChange={(e) => setFormData({ ...formData, empresa_contacto: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Teléfono *
                  </label>
                  <input
                    type="tel"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={formData.empresa_telefono}
                    onChange={(e) => setFormData({ ...formData, empresa_telefono: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={formData.empresa_email}
                    onChange={(e) => setFormData({ ...formData, empresa_email: e.target.value })}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Datos del Administrador - solo al crear */}
            {!editingId && (
              <div>
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Datos del Primer Administrador
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nombre Completo *
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      value={formData.admin_nombre}
                      onChange={(e) => setFormData({ ...formData, admin_nombre: e.target.value })}
                      required={!editingId}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      value={formData.admin_email}
                      onChange={(e) => setFormData({ ...formData, admin_email: e.target.value })}
                      required={!editingId}
                    />
                  </div>

                  <div className="md:col-span-2">
                    <PasswordInput
                      label="Contraseña"
                      value={formData.admin_password}
                      onChange={(e) => setFormData({ ...formData, admin_password: e.target.value })}
                      required={!editingId}
                      minLength={6}
                    />
                  </div>
                </div>
              </div>
            )}

            <div className="md:col-span-2 flex gap-3 justify-end">
              <button
                type="button"
                onClick={resetForm}
                className="px-5 py-2.5 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-colors"
              >
                <Save className="w-5 h-5" />
                {editingId ? 'Actualizar' : 'Guardar'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tabla de empresas */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Empresa
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  NIT
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contacto
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {empresas.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    <Building2 className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                    <p>No hay empresas registradas</p>
                  </td>
                </tr>
              ) : (
                empresas.map((empresa) => (
                  <tr key={empresa.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="bg-blue-100 p-2 rounded-lg">
                          <Building2 className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">{empresa.nombre}</p>
                          <p className="text-sm text-gray-500">{empresa.direccion}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-700">{empresa.nit}</td>
                    <td className="px-6 py-4">
                      <p className="text-gray-700">{empresa.telefono}</p>
                      <p className="text-sm text-gray-500">{empresa.email}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          empresa.activo
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {empresa.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {!empresa.activo && (
                          <button
                            onClick={() => handleActivateClick(empresa.id)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Reactivar"
                          >
                            <RefreshCw className="w-5 h-5" />
                          </button>
                        )}
                        <button
                          onClick={() => handleEdit(empresa)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Editar"
                        >
                          <Edit2 className="w-5 h-5" />
                        </button>
                        {empresa.activo && (
                          <button
                            onClick={() => handleDeleteClick(empresa.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Desactivar"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {empresas.length > 0 && (
        <div className="text-center text-sm text-gray-600">
          Total de empresas: <span className="font-semibold">{empresas.length}</span>
        </div>
      )}

      {/* Diálogos de Confirmación */}
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Desactivar Empresa"
        message="¿Estás seguro de desactivar esta empresa? Los usuarios asociados no podrán iniciar sesión hasta que sea reactivada."
        type="danger"
        confirmText="Desactivar"
        cancelText="Cancelar"
        onConfirm={confirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />

      <ConfirmDialog
        isOpen={showActivateConfirm}
        title="Reactivar Empresa"
        message="¿Estás seguro de reactivar esta empresa? Los usuarios asociados podrán volver a iniciar sesión."
        type="success"
        confirmText="Reactivar"
        cancelText="Cancelar"
        onConfirm={confirmActivate}
        onCancel={() => setShowActivateConfirm(false)}
      />
    </div>
  );
}
