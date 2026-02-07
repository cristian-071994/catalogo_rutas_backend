import { useEffect, useState } from "react";
import { useAuth } from '../context/AuthContext';
import PrecioCombustibleModule from '../components/configuracion/PrecioCombustibleModule';
import ClientesModule from '../components/configuracion/ClientesModule';
import MarcasModule from '../components/configuracion/MarcasModule';
import ConfiguracionVehicleModule from '../components/configuracion/ConfiguracionVehicleModule';
import VehiculosModule from '../components/configuracion/VehiculosModule'
import RendimientoModule from '../components/configuracion/RendimientoModule';
import RutasModule from '../components/configuracion/RutasModule';
import TramosModule from '../components/configuracion/TramosModule';
import PeajesModule from '../components/configuracion/PeajesModule';
import { hasAnyPermission } from '../utils/permissions';

export default function ConfiguracionPage() {
  const { usuario } = useAuth();
  const [activeTab, setActiveTab] = useState('precio-combustible');

  const tabs = [
    { id: 'precio-combustible', label: '💰 Precio Combustible', icon: '💰', permissions: ['editar_configuracion'] },
    { id: 'clientes', label: '👥 Clientes', icon: '👥', permissions: ['ver_clientes', 'crear_cliente', 'editar_cliente', 'eliminar_cliente'] },
    { id: 'marcas', label: '🏷️ Marcas', icon: '🏷️', permissions: ['ver_marcas', 'crear_marca', 'editar_marca', 'eliminar_marca'] },
    { id: 'config-vehiculo', label: '⚙️ Config Vehículo', icon: '⚙️', permissions: ['ver_configuracion_vehiculos', 'crear_configuracion_vehiculo', 'editar_configuracion_vehiculo', 'eliminar_configuracion_vehiculo'] },
    { id: 'rendimiento', label: '⛽ Rendimiento', icon: '⛽', permissions: ['ver_rendimiento', 'crear_rendimiento', 'editar_rendimiento', 'eliminar_rendimiento'] },
    { id: 'vehiculos', label: '🚗 Vehículos', icon: '🚗', permissions: ['ver_vehiculos', 'crear_vehiculo', 'editar_vehiculo', 'eliminar_vehiculo'] },
    { id: 'rutas', label: '🗺️ Rutas', icon: '🗺️', permissions: ['ver_rutas', 'crear_ruta', 'editar_ruta', 'eliminar_ruta'] },
    { id: 'tramos', label: '🛣️ Tramos', icon: '🛣️', permissions: ['ver_tramos', 'crear_tramo', 'editar_tramo', 'eliminar_tramo', 'ver_tramo_detalle', 'crear_tramo_detalle', 'editar_tramo_detalle', 'eliminar_tramo_detalle'] },
    { id: 'peajes', label: '🚧 Peajes', icon: '🚧', permissions: ['ver_peajes', 'crear_peaje', 'editar_peaje', 'eliminar_peaje'] },
  ];

  const availableTabs = tabs.filter((tab) => hasAnyPermission(usuario, tab.permissions));

  useEffect(() => {
    if (availableTabs.length === 0) {
      return;
    }

    const isActiveAvailable = availableTabs.some((tab) => tab.id === activeTab);
    if (!isActiveAvailable) {
      setActiveTab(availableTabs[0].id);
    }
  }, [activeTab, availableTabs]);

  return (
    <div className="w-full min-w-0 space-y-6 overflow-x-hidden">
      <div>
        <h1 className="text-3xl font-bold text-neutral-900">⚙️ Configuración del Sistema</h1>
        <p className="text-neutral-600 mt-1">Gestiona todos los módulos necesarios para el cálculo de rutas</p>
      </div>

      {/* Tabs */}
      <div className="w-full min-w-0 overflow-hidden">
        <div className="bg-white border border-neutral-200 rounded-t-lg">
          <div className="tabs-container flex gap-2 sm:gap-3 overflow-x-auto">
            {availableTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-button whitespace-nowrap px-4 py-3 text-sm font-medium transition-all duration-200 border-b-2 ${
                  activeTab === tab.id
                    ? 'text-blue-600 border-blue-600 bg-blue-50'
                    : 'text-gray-600 border-transparent hover:text-gray-900 hover:bg-gray-50'
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
          {availableTabs.length === 0 ? (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-900">
              No tienes permisos para acceder a los modulos de configuracion.
            </div>
          ) : (
            <>
              {activeTab === 'precio-combustible' && <PrecioCombustibleModule />}
              {activeTab === 'clientes' && <ClientesModule />}
              {activeTab === 'marcas' && <MarcasModule />}
              {activeTab === 'config-vehiculo' && <ConfiguracionVehicleModule />}
              {activeTab === 'rendimiento' && <RendimientoModule />}
              {activeTab === 'vehiculos' && <VehiculosModule />}
              {activeTab === 'rutas' && <RutasModule />}
              {activeTab === 'tramos' && <TramosModule />}
              {activeTab === 'peajes' && <PeajesModule />}
            </>
          )}
        </div>
      </div>

      {/* Nota sobre orden de creación */}
      <div>
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-900 font-medium mb-2">💡 Recomendación de orden:</p>
          <p className="text-sm text-blue-800">
            1. Precio Combustible → 2. Clientes → 3. Marcas → 4. Config Vehículo → 5. Rendimiento → 6. Vehículos → 7. Rutas → 8. Tramos → 9. Peajes
          </p>
        </div>
      </div>
    </div>
  );
}
