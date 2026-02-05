import { useState, useEffect } from 'react';
import { Shield, Plus, Edit2, Save, X, AlertCircle, CheckCircle, Trash2 } from 'lucide-react';
import axiosInstance from '../../services/axiosInstance';
import ConfirmDialog from '../ConfirmDialog';

interface Rol {
  id: number;
  nombre: string;
  descripcion: string;
  activo: boolean;
  created_at: string;
}

export default function RolesModule() {
  const [roles, setRoles] = useState<Rol[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  
  // Estados para ConfirmDialog
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  
  // Form state
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
  });

  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/roles/');
      console.log('Roles recibidos:', response.data);
      setRoles(Array.isArray(response.data) ? response.data : []);
      setError('');
    } catch (err: any) {
      console.error('Error al cargar roles:', err);
      setError(err.response?.data?.detail || 'Error al cargar roles');
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
        // Actualizar
        await axiosInstance.put(`/roles/${editingId}`, formData);
        setSuccess('Rol actualizado correctamente');
      } else {
        // Crear
        await axiosInstance.post('/roles/', formData);
        setSuccess('Rol creado correctamente');
      }

      resetForm();
      loadRoles();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar el rol');
    }
  };

  const handleEdit = (rol: Rol) => {
    setFormData({
      nombre: rol.nombre,
      descripcion: rol.descripcion,
    });
    setEditingId(rol.id);
    setShowForm(true);
  };

  const handleDeleteClick = (id: number) => {
    setSelectedId(id);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!selectedId) return;

    try {
      await axiosInstance.delete(`/roles/${selectedId}`);
      setSuccess('Rol eliminado correctamente');
      loadRoles();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar el rol');
    } finally {
      setShowDeleteConfirm(false);
      setSelectedId(null);
    }
  };

  const resetForm = () => {
    setFormData({
      nombre: '',
      descripcion: '',
    });
    setEditingId(null);
    setShowForm(false);
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-gray-600 mt-4">Cargando roles...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🛡️ Gestión de Roles</h2>
          <p className="text-gray-600 mt-1">Define los roles y sus descripciones en el sistema</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          {showForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
          {showForm ? 'Cancelar' : 'Nuevo Rol'}
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
            {editingId ? 'Editar Rol' : 'Nuevo Rol'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre del Rol *
              </label>
              <input
                type="text"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="ej: admin, usuario, operador"
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción *
              </label>
              <textarea
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                placeholder="Descripción del rol y sus responsabilidades"
                value={formData.descripcion}
                onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                rows={3}
                required
              />
            </div>

            <div className="flex gap-3 justify-end pt-2">
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
                {editingId ? 'Actualizar' : 'Crear'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de roles */}
      <div className="grid gap-4">
        {roles.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-xl p-12 text-center">
            <Shield className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No hay roles</h3>
            <p className="text-gray-600">Crea el primer rol del sistema</p>
          </div>
        ) : (
          roles.map((rol) => (
            <div
              key={rol.id}
              className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4 flex-1">
                  <div className="bg-blue-100 p-3 rounded-xl">
                    <Shield className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{rol.nombre}</h3>
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          rol.activo
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {rol.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-3">{rol.descripcion}</p>
                    <p className="text-sm text-gray-500">
                      Creado: {new Date(rol.created_at).toLocaleDateString('es-CO', {
                        timeZone: 'America/Bogota',
                        day: '2-digit',
                        month: 'long',
                        year: 'numeric'
                      })}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEdit(rol)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Editar"
                  >
                    <Edit2 className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDeleteClick(rol.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Eliminar"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {roles.length > 0 && (
        <div className="text-center text-sm text-gray-600">
          Total de roles: <span className="font-semibold">{roles.length}</span>
        </div>
      )}

      <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          Nota Importante
        </h3>
        <p className="text-sm text-blue-800">
          Los roles definen el tipo de usuario en el sistema. Después de crear un rol, 
          puedes asignarle permisos específicos en el módulo de Permisos.
        </p>
      </div>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Eliminar Rol"
        message="¿Estás seguro de eliminar este rol? Esta acción no se puede deshacer."
        type="danger"
        confirmText="Eliminar"
        cancelText="Cancelar"
        onConfirm={confirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </div>
  );
}
