import { useState } from "react";
import PrecioCombustibleModule from '../components/configuracion/PrecioCombustibleModule';
import ClientesModule from '../components/configuracion/ClientesModule';
import MarcasModule from '../components/configuracion/MarcasModule';
import ConfiguracionVehicleModule from '../components/configuracion/ConfiguracionVehicleModule';
import VehiculosModule from '../components/configuracion/VehiculosModule'
import RendimientoModule from '../components/configuracion/RendimientoModule';
import RutasModule from '../components/configuracion/RutasModule';
import TramosModule from '../components/configuracion/TramosModule';
import PeajesModule from '../components/configuracion/PeajesModule';

export default function ConfiguracionPage() {
  const [activeTab, setActiveTab] = useState('precio-combustible');

  const tabs = [
    { id: 'precio-combustible', label: '💰 Precio Combustible', icon: '💰' },
    { id: 'clientes', label: '👥 Clientes', icon: '👥' },
    { id: 'marcas', label: '🏷️ Marcas', icon: '🏷️' },
    { id: 'config-vehiculo', label: '⚙️ Config Vehículo', icon: '⚙️' },
    { id: 'rendimiento', label: '⛽ Rendimiento', icon: '⛽' },
    { id: 'vehiculos', label: '🚗 Vehículos', icon: '🚗' },
    { id: 'rutas', label: '🗺️ Rutas', icon: '🗺️' },
    { id: 'tramos', label: '🛣️ Tramos', icon: '🛣️' },
    { id: 'peajes', label: '🚧 Peajes', icon: '🚧' },
  ];

  return (
    <div className="space-y-6">
      <div className="px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-neutral-900">⚙️ Configuración del Sistema</h1>
        <p className="text-neutral-600 mt-1">Gestiona todos los módulos necesarios para el cálculo de rutas</p>
      </div>

      {/* Tabs */}
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="bg-white border border-neutral-200 rounded-t-lg overflow-hidden">
          <div className="tabs-container flex gap-2 sm:gap-3 overflow-x-auto">
            {tabs.map((tab) => (
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
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="bg-white border border-neutral-200 rounded-b-lg p-4 sm:p-6 lg:p-8">
          {activeTab === 'precio-combustible' && <PrecioCombustibleModule />}
          {activeTab === 'clientes' && <ClientesModule />}
          {activeTab === 'marcas' && <MarcasModule />}
          {activeTab === 'config-vehiculo' && <ConfiguracionVehicleModule />}
          {activeTab === 'rendimiento' && <RendimientoModule />}
          {activeTab === 'vehiculos' && <VehiculosModule />}
          {activeTab === 'rutas' && <RutasModule />}
          {activeTab === 'tramos' && <TramosModule />}
          {activeTab === 'peajes' && <PeajesModule />}
        </div>
      </div>

      {/* Nota sobre orden de creación */}
      <div className="px-4 sm:px-6 lg:px-8">
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
