import { useState } from "react";
import ClientesModule from '../components/configuracion/ClientesModule';
import MarcasModule from '../components/configuracion/MarcasModule';
import ConfiguracionVehicleModule from '../components/configuracion/ConfiguracionVehicleModule';
import VehiculosModule from '../components/configuracion/VehiculosModule'
import RendimientoModule from '../components/configuracion/RendimientoModule';
import RutasModule from '../components/configuracion/RutasModule';
import TramosModule from '../components/configuracion/TramosModule';
import PeajesModule from '../components/configuracion/PeajesModule';

export default function ConfiguracionPage() {
  const [activeTab, setActiveTab] = useState('clientes');

  const tabs = [
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
      <div>
        <h1 className="text-3xl font-bold text-neutral-900">⚙️ Configuración del Sistema</h1>
        <p className="text-neutral-600 mt-1">Gestiona todos los módulos necesarios para el cálculo de rutas</p>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-neutral-200 rounded-t-lg overflow-x-auto">
        <div className="tabs-container px-4 flex gap-0 border-b-0">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab-button whitespace-nowrap ${activeTab === tab.id ? 'active' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="bg-white border border-neutral-200 rounded-b-lg p-6">
        {activeTab === 'clientes' && <ClientesModule />}
        {activeTab === 'marcas' && <MarcasModule />}
        {activeTab === 'config-vehiculo' && <ConfiguracionVehicleModule />}
        {activeTab === 'rendimiento' && <RendimientoModule />}
        {activeTab === 'vehiculos' && <VehiculosModule />}
        {activeTab === 'rutas' && <RutasModule />}
        {activeTab === 'tramos' && <TramosModule />}
        {activeTab === 'peajes' && <PeajesModule />}
      </div>

      {/* Nota sobre orden de creación */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900 font-medium mb-2">💡 Recomendación de orden:</p>
        <p className="text-sm text-blue-800">
          1. Clientes → 2. Marcas → 3. Config Vehículo → 4. Rendimiento → 5. Vehículos → 6. Rutas → 7. Tramos → 8. Peajes
        </p>
      </div>
    </div>
  );
}
