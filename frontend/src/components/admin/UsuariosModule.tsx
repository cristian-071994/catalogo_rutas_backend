import { useState, useEffect } from 'react';
import { Users, Plus, Edit2, Save, X, AlertCircle, CheckCircle, Trash2, Key } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import axiosInstance from '../../services/axiosInstance';
import ConfirmDialog from '../ConfirmDialog';
import PasswordInput from '../PasswordInput';

interface Usuario {
  id: number;
  email: string;
  nombre: string;
  empresa_id: number;
  empresa_nombre: string;
  rol: string;
  activo: number;
  aprobado: number;
  created_at: string;
  updated_at: string;
}

interface Rol {
  id: number;
  nombre: string;
  descripcion: string;
}

interface Empresa {
  id: number;
  nombre: string;
}

export default function UsuariosModule() {
  const { usuario: currentUser } = useAuth();
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [roles, setRoles] = useState<Rol[]>([]);
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  
  // Estados para ConfirmDialog
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showActivateConfirm, setShowActivateConfirm] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  
  const isAdmin = currentUser?.rol?.nombre === 'admin';
  const isSuperAdmin = currentUser?.rol?.nombre === 'super_admin';
  const canManageUsers = isAdmin || isSuperAdmin;

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    nombre: '',
    password: '',
    rol_id: '',
    empresa_id: '',
  });

  // Password change form
  const [passwordData, setPasswordData] = useState({
    password_actual: '',
    password_nueva: '',
    password_confirmar: '',
  });

  useEffect(() => {
    if (canManageUsers) {
      loadUsuarios();
      // Cargar roles de forma independiente para que no bloquee la carga de usuarios
      loadRoles().catch(() => {
        console.log('No se pudieron cargar los roles, continuando sin ellos');
      });
      if (isSuperAdmin) {
        loadEmpresas().catch(() => {
          console.log('No se pudieron cargar las empresas, continuando sin ellas');
        });
      }
    }
  }, [canManageUsers]);

  const loadUsuarios = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/usuarios/');
      console.log('Respuesta completa de API usuarios:', response.data);
      // Manejar tanto array directo como objeto con items
      const data = response.data.items || response.data;
      console.log('Usuarios extraídos:', data);
      console.log('Cantidad de usuarios:', Array.isArray(data) ? data.length : 0);
      setUsuarios(Array.isArray(data) ? data : []);
      setError('');
    } catch (err: any) {
      console.error('Error al cargar usuarios:', err);
      setError(err.response?.data?.detail || 'Error al cargar usuarios');
    } finally {
      setLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const response = await axiosInstance.get('/roles/');
      const data = response.data.items || response.data;
      setRoles(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error al cargar roles:', err);
      // Si falla por permisos (403), establecer array vacío pero no mostrar error al usuario
      setRoles([]);
    }
  };

  const loadEmpresas = async () => {
    try {
      const response = await axiosInstance.get('/empresas/');
      const data = response.data.items || response.data;
      setEmpresas(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error al cargar empresas:', err);
      setEmpresas([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (isSuperAdmin && !editingId && !formData.empresa_id) {
      setError('Selecciona una empresa para el nuevo usuario');
      return;
    }

    try {
      const rolSeleccionado = roles.find((rol) => String(rol.id) === formData.rol_id);
      const payload = {
        email: formData.email,
        nombre: formData.nombre,
        ...(formData.password && { password: formData.password }),
        ...(formData.rol_id && { rol_id: parseInt(formData.rol_id) }),
        ...(rolSeleccionado && { rol: rolSeleccionado.nombre }),
        ...(isSuperAdmin && formData.empresa_id && { empresa_id: parseInt(formData.empresa_id) }),
      };

      if (editingId) {
        // Actualizar
        await axiosInstance.put(`/usuarios/${editingId}`, payload);
        setSuccess('Usuario actualizado correctamente');
      } else {
        // Crear
        await axiosInstance.post('/usuarios/', { ...payload, password: formData.password });
        setSuccess('Usuario creado correctamente');
      }

      resetForm();
      loadUsuarios();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar el usuario');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (passwordData.password_nueva !== passwordData.password_confirmar) {
      setError('Las contraseñas no coinciden');
      return;
    }

    try {
      await axiosInstance.put('/usuarios/cambiar-contraseña', {
        password_actual: passwordData.password_actual,
        password_nueva: passwordData.password_nueva,
        password_confirmar: passwordData.password_confirmar,
      });
      setSuccess('Contraseña actualizada correctamente');
      setPasswordData({ password_actual: '', password_nueva: '', password_confirmar: '' });
      setShowPasswordForm(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cambiar la contraseña');
    }
  };

  const handleEdit = (usuario: Usuario) => {
    setFormData({
      email: usuario.email,
      nombre: usuario.nombre,
      password: '',
      rol_id: '', // El rol_id no viene en la respuesta, lo dejamos vacío
      empresa_id: isSuperAdmin ? String(usuario.empresa_id) : '',
    });
    setEditingId(usuario.id);
    setShowForm(true);
  };

  const handleDeleteClick = (id: number) => {
    setSelectedId(id);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!selectedId) return;

    try {
      await axiosInstance.delete(`/usuarios/${selectedId}`);
      setSuccess('Usuario eliminado correctamente');
      loadUsuarios();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar el usuario');
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
      await axiosInstance.put(`/usuarios/${selectedId}`, {
        activo: 1
      });
      setSuccess('Usuario activado correctamente');
      loadUsuarios();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al activar el usuario');
    } finally {
      setShowActivateConfirm(false);
      setSelectedId(null);
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      nombre: '',
      password: '',
      rol_id: '',
      empresa_id: '',
    });
    setEditingId(null);
    setShowForm(false);
  };

  if (loading && canManageUsers) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-gray-600 mt-4">Cargando usuarios...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">👥 Gestión de Usuarios</h2>
          <p className="text-gray-600 mt-1">
            {canManageUsers ? 'Administra los usuarios del sistema' : 'Gestiona tu perfil y contraseña'}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowPasswordForm(!showPasswordForm)}
            className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <Key className="w-5 h-5" />
            Cambiar Contraseña
          </button>
          {canManageUsers && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              {showForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
              {showForm ? 'Cancelar' : 'Nuevo Usuario'}
            </button>
          )}
        </div>
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

      {/* Formulario de cambio de contraseña */}
      {showPasswordForm && (
        <div className="bg-white/90 backdrop-blur-md border border-gray-200 rounded-2xl p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cambiar Mi Contraseña</h3>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <PasswordInput
              label="Contraseña Actual *"
              value={passwordData.password_actual}
              onChange={(e) => setPasswordData({ ...passwordData, password_actual: e.target.value })}
              required
            />

            <PasswordInput
              label="Nueva Contraseña *"
              value={passwordData.password_nueva}
              onChange={(e) => setPasswordData({ ...passwordData, password_nueva: e.target.value })}
              required
              minLength={6}
            />

            <PasswordInput
              label="Confirmar Nueva Contraseña *"
              value={passwordData.password_confirmar}
              onChange={(e) => setPasswordData({ ...passwordData, password_confirmar: e.target.value })}
              required
              minLength={6}
            />

            <div className="flex gap-3 justify-end pt-2">
              <button
                type="button"
                onClick={() => setShowPasswordForm(false)}
                className="px-5 py-2.5 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-colors"
              >
                <Save className="w-5 h-5" />
                Actualizar Contraseña
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Formulario de usuario (solo admin/super_admin) */}
      {showForm && canManageUsers && (
        <div className="bg-white/90 backdrop-blur-md border border-blue-200 rounded-2xl p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingId ? 'Editar Usuario' : 'Nuevo Usuario'}
          </h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre Completo *
              </label>
              <input
                type="text"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
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
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            {isSuperAdmin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Empresa *
                </label>
                <select
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={formData.empresa_id}
                  onChange={(e) => setFormData({ ...formData, empresa_id: e.target.value })}
                  required={!editingId}
                >
                  <option value="">Seleccionar empresa</option>
                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>
                      {empresa.nombre}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <PasswordInput
              label={`Contraseña ${editingId ? '(dejar vacío para no cambiar)' : '*'}`}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required={!editingId}
              minLength={6}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rol *
              </label>
              <select
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={formData.rol_id}
                onChange={(e) => setFormData({ ...formData, rol_id: e.target.value })}
                required
              >
                <option value="">Seleccionar rol</option>
                {roles.map((rol) => (
                  <option key={rol.id} value={rol.id}>
                    {rol.nombre} - {rol.descripcion}
                  </option>
                ))}
              </select>
            </div>

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
                {editingId ? 'Actualizar' : 'Crear'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tabla de usuarios (solo admin/super_admin) */}
      {canManageUsers && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Usuario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Empresa
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rol
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
                {usuarios.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                      <Users className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                      <p>No hay usuarios registrados</p>
                    </td>
                  </tr>
                ) : (
                  usuarios.map((usuario) => (
                    <tr key={usuario.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-semibold text-gray-900">{usuario.nombre}</p>
                          <p className="text-sm text-gray-500">{usuario.email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-700">{usuario.empresa_nombre}</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {usuario.rol}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full w-fit ${
                              usuario.activo === 1
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {usuario.activo === 1 ? 'Activo' : 'Inactivo'}
                          </span>
                          {usuario.aprobado !== 1 && (
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 w-fit">
                              Pendiente
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {usuario.activo === 0 ? (
                            <button
                              onClick={() => handleActivateClick(usuario.id)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Activar"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                          ) : (
                            <>
                              <button
                                onClick={() => handleEdit(usuario)}
                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="Editar"
                              >
                                <Edit2 className="w-5 h-5" />
                              </button>
                              <button
                                onClick={() => handleDeleteClick(usuario.id)}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Eliminar"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            </>
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
      )}

      {/* Info para usuarios no admin */}
      {!canManageUsers && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h3 className="font-semibold text-blue-900 mb-2">Información de tu cuenta</h3>
          <div className="space-y-2 text-sm text-blue-800">
            <p><strong>Nombre:</strong> {currentUser?.nombre_completo}</p>
            <p><strong>Email:</strong> {currentUser?.email}</p>
            <p><strong>Rol:</strong> {currentUser?.rol?.nombre}</p>
            <p><strong>Empresa:</strong> {currentUser?.empresa}</p>
          </div>
        </div>
      )}

      {canManageUsers && usuarios.length > 0 && (
        <div className="text-center text-sm text-gray-600">
          Total de usuarios: <span className="font-semibold">{usuarios.length}</span>
        </div>
      )}

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Eliminar Usuario"
        message="¿Estás seguro de eliminar este usuario? Esta acción no se puede deshacer."
        type="danger"
        confirmText="Eliminar"
        cancelText="Cancelar"
        onConfirm={confirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />

      <ConfirmDialog
        isOpen={showActivateConfirm}
        title="Activar Usuario"
        message="¿Estás seguro de activar este usuario? Volverá a tener acceso al sistema."
        type="success"
        confirmText="Activar"
        cancelText="Cancelar"
        onConfirm={confirmActivate}
        onCancel={() => setShowActivateConfirm(false)}
      />
    </div>
  );
}
