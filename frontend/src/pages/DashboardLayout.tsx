import { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, Menu, X, BarChart3, Settings, BookOpen, Building2, Shield } from 'lucide-react';
import ResumenRutasPage from './ResumenRutasPage';
import ConfiguracionPage from './ConfiguracionPage';
import GuiaPage from './GuiaPage';
import AdminPage from './AdminPage';
import { canAccessConfig } from '../utils/permissions';

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isSuperAdmin = usuario?.rol?.nombre === 'super_admin';
  const isAdmin = usuario?.rol?.nombre === 'admin';
  const canAccessConfiguracion = canAccessConfig(usuario);

  const menuItems = [
    { 
      id: 'resumen', 
      label: 'Resumen de Rutas', 
      path: '/dashboard/resumen',
      icon: BarChart3
    },
    ...(canAccessConfiguracion ? [{ 
      id: 'config', 
      label: 'Configuración', 
      path: '/dashboard/configuracion',
      icon: Settings
    }] : []),
    ...(isSuperAdmin || isAdmin ? [{ 
      id: 'admin', 
      label: 'Administración', 
      path: '/dashboard/admin',
      icon: Shield
    }] : []),
    { 
      id: 'guia', 
      label: 'Guía de Uso', 
      path: '/dashboard/guia',
      icon: BookOpen
    },
  ];

  const isActivePath = (path: string) => {
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {sidebarOpen ? (
                <X className="w-6 h-6 text-gray-700" />
              ) : (
                <Menu className="w-6 h-6 text-gray-700" />
              )}
            </button>
            <div className="flex items-center gap-2">
              <div className="bg-blue-600 p-2 rounded-lg">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">Catálogo de Rutas</h1>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {usuario?.empresa && (
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-lg border border-blue-200">
                <Building2 className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-700">{usuario.empresa}</span>
              </div>
            )}
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium text-gray-900">{usuario?.nombre_completo}</p>
              <p className="text-xs text-gray-600 capitalize">{usuario?.rol.nombre}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-red-50 rounded-lg text-gray-600 hover:text-red-600 transition-all duration-200"
              title="Cerrar sesión"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 w-full">
        {/* Sidebar */}
        <aside
          className={`
            fixed lg:relative inset-y-0 left-0 w-64 bg-white border-r border-gray-200 shadow-lg lg:shadow-none
            transform transition-transform duration-200 ease-in-out
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            z-30 top-[65px] lg:top-0
          `}
        >
          <nav className="p-4 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = isActivePath(item.path);
              
              return (
                <a
                  key={item.id}
                  href={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200
                    ${isActive 
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50' 
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>
          
          {/* User info mobile */}
          <div className="sm:hidden p-4 border-t border-gray-200 mt-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-blue-100 p-2 rounded-lg">
                <Building2 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{usuario?.nombre_completo}</p>
                <p className="text-xs text-gray-600">{usuario?.empresa}</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Overlay para mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/10 backdrop-blur-lg z-20 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Content */}
        <main className="flex-1 w-full overflow-x-hidden">
          <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 py-4 sm:py-6 lg:py-8">
            <Routes>
              <Route path="/resumen" element={<ResumenRutasPage />} />
              {canAccessConfiguracion && <Route path="/configuracion/*" element={<ConfiguracionPage />} />}
              {(isSuperAdmin || isAdmin) && <Route path="/admin/*" element={<AdminPage />} />}
              <Route path="/guia" element={<GuiaPage />} />
              <Route path="/" element={<ResumenRutasPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}
