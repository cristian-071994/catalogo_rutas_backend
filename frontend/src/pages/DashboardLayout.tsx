import { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, Menu, X } from 'lucide-react';
import ResumenRutasPage from './ResumenRutasPage';
import ConfiguracionPage from './ConfiguracionPage';

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { id: 'resumen', label: '📊 Resumen de Rutas', path: '/dashboard/resumen' },
    { id: 'config', label: '⚙️ Configuración', path: '/dashboard/configuracion' },
  ];

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 sticky top-0 z-40">
        <div className="px-4 py-4 flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-neutral-100 rounded-lg"
            >
              {sidebarOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
            <h1 className="text-xl font-bold text-neutral-900">Catálogo de Rutas</h1>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-neutral-900">{usuario?.nombre_completo}</p>
              <p className="text-xs text-neutral-600">{usuario?.rol.nombre}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-neutral-100 rounded-lg text-neutral-600 hover:text-neutral-900"
              title="Cerrar sesión"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 max-w-7xl mx-auto w-full">
        {/* Sidebar */}
        <aside
          className={`
            fixed lg:relative inset-y-0 left-0 w-64 bg-white border-r border-neutral-200
            transform transition-transform duration-200 ease-in-out
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            z-30 top-[65px] lg:top-0
          `}
        >
          <nav className="p-4 space-y-2">
            {menuItems.map((item) => (
              <a
                key={item.id}
                href={item.path}
                onClick={() => setSidebarOpen(false)}
                className="block px-4 py-2 rounded-lg text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
              >
                {item.label}
              </a>
            ))}
          </nav>
        </aside>

        {/* Content */}
        <main className="flex-1 p-6 lg:p-8 w-full">
          <Routes>
            <Route path="/resumen" element={<ResumenRutasPage />} />
            <Route path="/configuracion/*" element={<ConfiguracionPage />} />
            <Route path="/" element={<ResumenRutasPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
