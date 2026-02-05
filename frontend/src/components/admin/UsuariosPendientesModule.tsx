import { useState, useEffect } from 'react';
import { UserCheck, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import axiosInstance from '../../services/axiosInstance';

interface UsuarioPendiente {
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

export default function UsuariosPendientesModule() {
  const [usuarios, setUsuarios] = useState<UsuarioPendiente[]>([]);
  const [roles, setRoles] = useState<Rol[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Estados para ConfirmDialog y aprobación
  const [showApproveConfirm, setShowApproveConfirm] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selectedRol, setSelectedRol] = useState<string>('');

  useEffect(() => {
    loadUsuariosPendientes();
    loadRoles();
  }, []);

  const loadUsuariosPendientes = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await axiosInstance.get('/usuarios/pendientes');
      console.log('Respuesta completa de API pendientes:', response.data);
      // La API devuelve { items: [], total: ... }
      const items = response.data.items || [];
      console.log('Items extraídos:', items);
      console.log('Cantidad de usuarios pendientes:', items.length);
      setUsuarios(Array.isArray(items) ? items : []);
    } catch (err: any) {
      console.error('Error cargando usuarios pendientes:', err);
      setError(err.response?.data?.detail || 'Error al cargar usuarios pendientes');
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
      // Si falla, establecer array vacío
      setRoles([]);
    }
  };

  const handleAprobarClick = (usuarioId: number, rolSugerido: string) => {
    setSelectedId(usuarioId);
    // Preseleccionar el rol sugerido o el primero disponible
    setSelectedRol(rolSugerido || (roles.length > 0 ? roles[0].nombre : ''));
    setShowApproveConfirm(true);
  };

  const confirmAprobar = async () => {
    if (!selectedId || !selectedRol) {
      setError('Debe seleccionar un rol para aprobar el usuario');
      return;
    }

    try {
      await axiosInstance.post(`/usuarios/${selectedId}/aprobar`, {
        rol_nombre: selectedRol
      });
      setSuccess('Usuario aprobado correctamente');
      loadUsuariosPendientes();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al aprobar usuario');
    } finally {
      setShowApproveConfirm(false);
      setSelectedId(null);
      setSelectedRol('');
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-gray-600 mt-4">Cargando usuarios pendientes...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">⏳ Usuarios Pendientes de Aprobación</h2>
        <p className="text-gray-600 mt-1">Revisa y aprueba los usuarios que esperan acceso al sistema</p>
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

      {/* Lista de usuarios */}
      <div className="grid gap-4">
        {!usuarios || usuarios.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-xl p-12 text-center">
            <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">¡Todo al día!</h3>
            <p className="text-gray-600">No hay usuarios pendientes de aprobación</p>
          </div>
        ) : (
          usuarios.map((usuario) => (
            <div
              key={usuario.id}
              className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4 flex-1">
                  <div className="bg-amber-100 p-3 rounded-xl">
                    <Clock className="w-6 h-6 text-amber-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{usuario.nombre}</h3>
                    <p className="text-gray-600 mb-3">{usuario.email}</p>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-gray-500">Empresa:</span>
                        <p className="font-semibold text-gray-900">
                          {usuario.empresa_nombre}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Rol solicitado:</span>
                        <p className="font-semibold text-gray-900">{usuario.rol}</p>
                      </div>
                      <div className="sm:col-span-2">
                        <span className="text-gray-500">Fecha de registro:</span>
                        <p className="font-semibold text-gray-900">
                          {new Date(usuario.created_at).toLocaleString('es-CO', {
                            timeZone: 'America/Bogota',
                            day: '2-digit',
                            month: 'long',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleAprobarClick(usuario.id, usuario.rol)}
                  className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl whitespace-nowrap"
                >
                  <UserCheck className="w-5 h-5" />
                  Aprobar
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {usuarios.length > 0 && (
        <div className="p-4 bg-amber-50 border-l-4 border-amber-500 rounded-lg">
          <p className="text-sm text-amber-800">
            <strong>Nota:</strong> Al aprobar un usuario, este podrá acceder al sistema con su rol asignado.
            Tienes <strong>{usuarios.length}</strong> usuario{usuarios.length !== 1 ? 's' : ''} pendiente{usuarios.length !== 1 ? 's' : ''} de aprobación.
          </p>
        </div>
      )}

      {/* Modal personalizado con selector de rol */}
      {showApproveConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/10 backdrop-blur-lg animate-fadeIn">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full animate-scaleIn">
            {/* Header */}
            <div className="bg-green-50 border-green-200 border-b px-6 py-4 rounded-t-2xl">
              <div className="flex items-center gap-3">
                <div className="bg-green-100 p-2 rounded-xl">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Aprobar Usuario</h3>
              </div>
            </div>

            {/* Body */}
            <div className="px-6 py-6 space-y-4">
              <p className="text-gray-700">
                ¿Estás seguro de aprobar este usuario? Tendrá acceso inmediato al sistema.
              </p>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Selecciona el rol para este usuario *
                </label>
                <select
                  value={selectedRol}
                  onChange={(e) => setSelectedRol(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  required
                >
                  <option value="">Selecciona un rol</option>
                  {roles.map((rol) => (
                    <option key={rol.id} value={rol.nombre}>
                      {rol.nombre} - {rol.descripcion}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 bg-gray-50 rounded-b-2xl flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowApproveConfirm(false);
                  setSelectedRol('');
                }}
                className="px-5 py-2.5 border border-gray-300 text-gray-600 font-medium rounded-xl hover:bg-gray-100 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={confirmAprobar}
                disabled={!selectedRol}
                className="px-5 py-2.5 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors shadow-lg"
              >
                Aprobar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
