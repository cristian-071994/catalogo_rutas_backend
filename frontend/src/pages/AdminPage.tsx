import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import EmpresasModule from '../components/admin/EmpresasModule';
import UsuariosPendientesModule from '../components/admin/UsuariosPendientesModule';
import UsuariosModule from '../components/admin/UsuariosModule';
import RolesModule from '../components/admin/RolesModule';
import PermisosModule from '../components/admin/PermisosModule';

export default function AdminPage() {
  const { usuario } = useAuth();
  const [activeTab, setActiveTab] = useState('usuarios-pendientes');

  const isSuperAdmin = usuario?.rol?.nombre === 'super_admin';
  const isAdmin = usuario?.rol?.nombre === 'admin';

  // Redirigir si no es admin o super_admin
  if (!isSuperAdmin && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  // Tabs según el rol
  const tabs = [
    ...(isSuperAdmin || isAdmin ? [{ id: 'usuarios-pendientes', label: '⏳ Pendientes', icon: '⏳' }] : []),
    { id: 'usuarios', label: '👥 Usuarios', icon: '👥' },
    ...(isSuperAdmin ? [{ id: 'empresas', label: '🏢 Empresas', icon: '🏢' }] : []),
    ...(isSuperAdmin ? [{ id: 'roles', label: '🛡️ Roles', icon: '🛡️' }] : []),
    ...(isSuperAdmin ? [{ id: 'permisos', label: '🔐 Permisos', icon: '🔐' }] : []),
  ];

  return (
    <div className="w-full min-w-0 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-neutral-900">⚙️ Administración</h1>
        <p className="text-neutral-600 mt-1">Panel de control administrativo del sistema</p>
      </div>

      {/* Tabs */}
      <div className="w-full min-w-0">
        <div className="bg-white border border-neutral-200 rounded-t-lg overflow-hidden">
          <div className="tabs-container flex gap-2 sm:gap-3 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-button whitespace-nowrap px-4 py-3 text-sm font-medium transition-all duration-200 border-b-2 ${
                  activeTab === tab.id
                    ? 'text-blue-600 border-blue-600 bg-blue-50'
                    : 'text-gray-500 border-transparent hover:text-blue-600 hover:bg-gray-50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="w-full min-w-0">
        <div className="bg-white border border-neutral-200 rounded-b-lg p-4 sm:p-6 lg:p-8">
          {activeTab === 'usuarios-pendientes' && (isSuperAdmin || isAdmin) && <UsuariosPendientesModule />}
          {activeTab === 'usuarios' && <UsuariosModule />}
          {activeTab === 'empresas' && isSuperAdmin && <EmpresasModule />}
          {activeTab === 'roles' && isSuperAdmin && <RolesModule />}
          {activeTab === 'permisos' && isSuperAdmin && <PermisosModule />}
        </div>
      </div>
    </div>
  );
}
