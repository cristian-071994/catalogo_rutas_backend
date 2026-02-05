import { useState, useEffect } from 'react';
import { Lock, Plus, AlertCircle, CheckCircle, Trash2, Shield } from 'lucide-react';
import axiosInstance from '../../services/axiosInstance';
import ConfirmDialog from '../ConfirmDialog';

interface Permiso {
  id: number;
  rol_id: number;
  recurso: string;
  accion: string;
  rol: {
    id: number;
    nombre: string;
  };
}

interface Rol {
  id: number;
  nombre: string;
  descripcion: string;
}

export default function PermisosModule() {
  const [permisos, setPermisos] = useState<Permiso[]>([]);
  const [roles, setRoles] = useState<Rol[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  
  // Estados para ConfirmDialog
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  
  // Form state
  const [formData, setFormData] = useState({
    rol_id: '',
    recurso: '',
    accion: '',
  });

  // Recursos y acciones disponibles
  const recursos = [
    'clientes', 'vehiculos', 'rutas', 'tramos', 'peajes',
    'marcas_vehiculos', 'configuracion_vehiculos', 'rendimiento_configuracion',
    'empresas', 'usuarios', 'roles', 'permisos', 'configuracion'
  ];

  const acciones = ['crear', 'leer', 'actualizar', 'eliminar', 'aprobar'];

  useEffect(() => {
    loadPermisos();
    loadRoles();
  }, []);

  const loadPermisos = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/permisos/');
      console.log('Permisos recibidos:', response.data);
      // Manejar tanto array directo como objeto con items
      const data = response.data.items || response.data;
      setPermisos(Array.isArray(data) ? data : []);
      setError('');
    } catch (err: any) {
      console.error('Error al cargar permisos:', err);
      setError(err.response?.data?.detail || 'Error al cargar permisos');
    } finally {
      setLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const response = await axiosInstance.get('/roles/');
      console.log('Roles para permisos:', response.data);
      const data = response.data.items || response.data;
      setRoles(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error al cargar roles:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await axiosInstance.post('/permisos/', {
        rol_id: parseInt(formData.rol_id),
        recurso: formData.recurso,
        accion: formData.accion,
      });
      
      setSuccess('Permiso creado correctamente');
      resetForm();
      loadPermisos();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear el permiso');
    }
  };

  const handleDeleteClick = (id: number) => {
    setSelectedId(id);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!selectedId) return;

    try {
      await axiosInstance.delete(`/permisos/${selectedId}`);
      setSuccess('Permiso eliminado correctamente');
      loadPermisos();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar el permiso');
    } finally {
      setShowDeleteConfirm(false);
      setSelectedId(null);
    }
  };

  const resetForm = () => {
    setFormData({
      rol_id: '',
      recurso: '',
      accion: '',
    });
    setShowForm(false);
  };

  // Agrupar permisos por rol
  const permisosPorRol = permisos.reduce((acc, permiso) => {
    const rolNombre = permiso.rol.nombre;
    if (!acc[rolNombre]) {
      acc[rolNombre] = [];
    }
    acc[rolNombre].push(permiso);
    return acc;
  }, {} as Record<string, Permiso[]>);

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-gray-600 mt-4">Cargando permisos...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🔐 Gestión de Permisos</h2>
          <p className="text-gray-600 mt-1">Asigna permisos específicos a cada rol del sistema</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          {showForm ? 'Cancelar' : <><Plus className="w-5 h-5" /> Nuevo Permiso</>}
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
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Nuevo Permiso</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                    {rol.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recurso *
              </label>
              <select
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={formData.recurso}
                onChange={(e) => setFormData({ ...formData, recurso: e.target.value })}
                required
              >
                <option value="">Seleccionar recurso</option>
                {recursos.map((recurso) => (
                  <option key={recurso} value={recurso}>
                    {recurso}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Acción *
              </label>
              <select
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={formData.accion}
                onChange={(e) => setFormData({ ...formData, accion: e.target.value })}
                required
              >
                <option value="">Seleccionar acción</option>
                {acciones.map((accion) => (
                  <option key={accion} value={accion}>
                    {accion}
                  </option>
                ))}
              </select>
            </div>

            <div className="md:col-span-3 flex gap-3 justify-end">
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
                <Plus className="w-5 h-5" />
                Crear Permiso
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Permisos agrupados por rol */}
      <div className="space-y-6">
        {Object.keys(permisosPorRol).length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-xl p-12 text-center">
            <Lock className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No hay permisos</h3>
            <p className="text-gray-600">Crea el primer permiso del sistema</p>
          </div>
        ) : (
          Object.entries(permisosPorRol).map(([rolNombre, permisosRol]) => (
            <div key={rolNombre} className="bg-white border border-gray-200 rounded-xl overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
                <div className="flex items-center gap-3">
                  <Shield className="w-6 h-6 text-white" />
                  <h3 className="text-xl font-bold text-white">{rolNombre}</h3>
                  <span className="ml-auto bg-white/20 text-white text-sm px-3 py-1 rounded-full font-semibold">
                    {permisosRol.length} permiso{permisosRol.length !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>

              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {permisosRol.map((permiso) => (
                    <div
                      key={permiso.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="bg-blue-100 p-2 rounded-lg">
                          <Lock className="w-4 h-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900 text-sm">{permiso.recurso}</p>
                          <p className="text-xs text-gray-600">{permiso.accion}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteClick(permiso.id)}
                        className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {permisos.length > 0 && (
        <div className="text-center text-sm text-gray-600">
          Total de permisos: <span className="font-semibold">{permisos.length}</span>
        </div>
      )}

      <div className="p-4 bg-amber-50 border-l-4 border-amber-500 rounded-lg">
        <h3 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          Guía de Permisos
        </h3>
        <ul className="text-sm text-amber-800 space-y-1">
          <li>• <strong>crear:</strong> Permite crear nuevos registros</li>
          <li>• <strong>leer:</strong> Permite ver/listar registros</li>
          <li>• <strong>actualizar:</strong> Permite modificar registros existentes</li>
          <li>• <strong>eliminar:</strong> Permite eliminar registros</li>
          <li>• <strong>aprobar:</strong> Permite aprobar usuarios pendientes</li>
        </ul>
      </div>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Eliminar Permiso"
        message="¿Estás seguro de eliminar este permiso? El rol perderá este acceso."
        type="danger"
        confirmText="Eliminar"
        cancelText="Cancelar"
        onConfirm={confirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </div>
  );
}
