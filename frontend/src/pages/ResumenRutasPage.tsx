import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import type { Cliente, Vehiculo, Ruta, ResumenRutaDetallado } from '../types/index';
import { AlertCircle, Loader } from 'lucide-react';

export default function ResumenRutasPage() {
  const [selectedCliente, setSelectedCliente] = useState<number | null>(null);
  const [selectedVehiculo, setSelectedVehiculo] = useState<number | null>(null);
  const [selectedRuta, setSelectedRuta] = useState<number | null>(null);
  const [resumen, setResumen] = useState<ResumenRutaDetallado | null>(null);
  const [error, setError] = useState('');
  const [isLoadingResumen, setIsLoadingResumen] = useState(false);

  const { data: clientes } = useQuery({
    queryKey: ['clientes'],
    queryFn: () => api.getClientes(),
  });

  const { data: vehiculos } = useQuery({
    queryKey: ['vehiculos'],
    queryFn: () => api.getVehiculos(),
  });

  const { data: rutas } = useQuery({
    queryKey: ['rutas'],
    queryFn: () => api.getRutas(),
  });

  const rutasDelCliente = rutas?.filter((r: Ruta) => r.cliente_id === selectedCliente) || [];

  const handleCalcularResumen = async () => {
    if (!selectedRuta || !selectedVehiculo) {
      setError('Selecciona una ruta y un vehículo');
      return;
    }

    setIsLoadingResumen(true);
    setError('');

    try {
      const data = await api.getResumenRuta(selectedRuta, selectedVehiculo);
      setResumen(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al calcular el resumen');
    } finally {
      setIsLoadingResumen(false);
    }
  };

  return (
    <div className="w-full min-w-0 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-neutral-900">📊 Resumen de Rutas</h1>
        <p className="text-neutral-600 mt-1">Selecciona un cliente, vehículo y ruta para ver el desglose de costos</p>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Selectores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Cliente */}
        <div className="card">
          <label className="label-base">Cliente</label>
          <select
            value={selectedCliente || ''}
            onChange={(e) => {
              setSelectedCliente(e.target.value ? Number(e.target.value) : null);
              setSelectedRuta(null);
            }}
            className="input-base"
          >
            <option value="">-- Selecciona un cliente --</option>
            {clientes?.map((c: Cliente) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
        </div>

        {/* Vehículo */}
        <div className="card">
          <label className="label-base">Vehículo</label>
          <select
            value={selectedVehiculo || ''}
            onChange={(e) => setSelectedVehiculo(e.target.value ? Number(e.target.value) : null)}
            className="input-base"
          >
            <option value="">-- Selecciona un vehículo --</option>
            {vehiculos?.map((v: Vehiculo) => (
              <option key={v.id} value={v.id}>
                {v.placa}
              </option>
            ))}
          </select>
        </div>

        {/* Ruta */}
        <div className="card">
          <label className="label-base">Ruta</label>
          <select
            value={selectedRuta || ''}
            onChange={(e) => setSelectedRuta(e.target.value ? Number(e.target.value) : null)}
            disabled={!selectedCliente}
            className="input-base disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="">-- Selecciona una ruta --</option>
            {rutasDelCliente.map((r: Ruta) => (
              <option key={r.id} value={r.id}>
                {r.origen} → {r.destino}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Botón Calcular */}
      <button
        onClick={handleCalcularResumen}
        disabled={!selectedRuta || !selectedVehiculo || isLoadingResumen}
        className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
      >
        {isLoadingResumen ? (
          <>
            <Loader className="w-4 h-4 animate-spin" />
            Calculando...
          </>
        ) : (
          'Calcular Resumen'
        )}
      </button>

      {/* Resumen */}
      {resumen && (
        <div className="space-y-6">
          {/* Información General */}
          <div className="card">
            <h2 className="text-lg font-bold text-neutral-900 mb-4">Información de la Ruta</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-neutral-600">Cliente</p>
                <p className="font-medium text-neutral-900">{resumen.cliente_nombre}</p>
              </div>
              <div>
                <p className="text-sm text-neutral-600">Recorrido</p>
                <p className="font-medium text-neutral-900">
                  {resumen.origen} → {resumen.destino}
                </p>
              </div>
              <div>
                <p className="text-sm text-neutral-600">Distancia Total</p>
                <p className="font-medium text-neutral-900">{resumen.distancia_total_km} km</p>
              </div>
              <div>
                <p className="text-sm text-neutral-600">Vehículo</p>
                <p className="font-medium text-neutral-900">{resumen.vehiculo_placa}</p>
              </div>
            </div>
          </div>

          {/* Resumen de Costos */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card">
              <p className="text-sm text-neutral-600 mb-1">Consumo</p>
              <p className="text-2xl font-bold text-neutral-900">{resumen.consumo_galones.toFixed(2)}</p>
              <p className="text-xs text-neutral-500">galones</p>
            </div>
            <div className="card">
              <p className="text-sm text-neutral-600 mb-1">Costo Combustible</p>
              <p className="text-2xl font-bold text-neutral-900">$ {resumen.costo_combustible.toFixed(2)}</p>
            </div>
            <div className="card">
              <p className="text-sm text-neutral-600 mb-1">Costo Peajes</p>
              <p className="text-2xl font-bold text-neutral-900">$ {resumen.costo_peajes_total.toFixed(2)}</p>
            </div>
          </div>

          {/* Costo Total */}
          <div className="card bg-neutral-900 text-white">
            <p className="text-sm opacity-90 mb-2">COSTO TOTAL DE LA RUTA</p>
            <p className="text-4xl font-bold">$ {resumen.costo_total.toFixed(2)}</p>
          </div>

          {/* Detalles de Tramos */}
          <div className="card">
            <h2 className="text-lg font-bold text-neutral-900 mb-4">Detalles por Tramo</h2>
            <div className="space-y-4">
              {resumen.tramos.map((tramo, idx) => (
                <div key={idx} className="border border-neutral-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="text-sm font-medium text-neutral-600">Tramo {idx + 1}</p>
                      <p className="font-medium text-neutral-900">
                        {tramo.origen} → {tramo.destino}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-neutral-600">{tramo.distancia_km} km</p>
                    </div>
                  </div>
                  
                  {tramo.peajes.length > 0 && (
                    <div className="mt-3 p-3 bg-neutral-50 rounded-lg">
                      <p className="text-xs font-medium text-neutral-700 mb-2">Peajes en este tramo:</p>
                      <div className="space-y-1">
                        {tramo.peajes.map((peaje, pIdx) => (
                          <div key={pIdx} className="flex justify-between text-sm">
                            <span className="text-neutral-600">{peaje.nombre} ({peaje.sector})</span>
                            <span className="font-medium text-neutral-900">$ {peaje.valor.toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                      <div className="border-t border-neutral-200 mt-2 pt-2 flex justify-between font-medium">
                        <span>Subtotal peajes:</span>
                        <span>$ {tramo.costo_peajes.toFixed(2)}</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
