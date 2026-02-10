import { useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { formatCOP, formatKm } from '../utils/format';
import type { Cliente, Vehiculo, Ruta, ResumenRutaDetallado, ResumenTramoDetalle } from '../types/index';
import { AlertCircle, Loader, Package, Route, Truck } from 'lucide-react';

export default function ResumenRutasPage() {
  const [selectedCliente, setSelectedCliente] = useState<number | null>(null);
  const [selectedVehiculo, setSelectedVehiculo] = useState<number | null>(null);
  const [selectedRuta, setSelectedRuta] = useState<number | null>(null);
  const [clienteSearch, setClienteSearch] = useState('');
  const [vehiculoSearch, setVehiculoSearch] = useState('');
  const [rutaSearch, setRutaSearch] = useState('');
  const [clienteOpen, setClienteOpen] = useState(false);
  const [vehiculoOpen, setVehiculoOpen] = useState(false);
  const [rutaOpen, setRutaOpen] = useState(false);
  const clienteButtonRef = useRef<HTMLButtonElement | null>(null);
  const vehiculoButtonRef = useRef<HTMLButtonElement | null>(null);
  const rutaButtonRef = useRef<HTMLButtonElement | null>(null);
  const [clienteDropdownStyle, setClienteDropdownStyle] = useState<Record<string, number>>({});
  const [vehiculoDropdownStyle, setVehiculoDropdownStyle] = useState<Record<string, number>>({});
  const [rutaDropdownStyle, setRutaDropdownStyle] = useState<Record<string, number>>({});
  const [clienteListHeight, setClienteListHeight] = useState(320);
  const [vehiculoListHeight, setVehiculoListHeight] = useState(320);
  const [rutaListHeight, setRutaListHeight] = useState(320);
  const [precioGalon, setPrecioGalon] = useState<number | ''>('');
  const [resumen, setResumen] = useState<ResumenRutaDetallado | null>(null);
  const [error, setError] = useState('');
  const [isLoadingResumen, setIsLoadingResumen] = useState(false);

  const { data: clientes = [] } = useQuery({
    queryKey: ['clientes'],
    queryFn: async () => {
      const data = await api.getClientes();
      return data?.items || data || [];
    },
  });

  const { data: vehiculos = [] } = useQuery({
    queryKey: ['vehiculos'],
    queryFn: async () => {
      const data = await api.getVehiculos();
      return data?.items || data || [];
    },
  });

  const { data: rutas = [] } = useQuery({
    queryKey: ['rutas'],
    queryFn: async () => {
      const data = await api.getRutas();
      return data?.items || data || [];
    },
  });

  const rutasDelCliente = rutas?.filter((r: Ruta) => r.cliente_id === selectedCliente) || [];

  const clientesFiltrados = useMemo(() => {
    const term = clienteSearch.trim().toLowerCase();
    if (!term) {
      return clientes;
    }
    return clientes.filter((c: Cliente) => c.nombre?.toLowerCase().includes(term));
  }, [clientes, clienteSearch]);

  const vehiculosFiltrados = useMemo(() => {
    const term = vehiculoSearch.trim().toLowerCase();
    if (!term) {
      return vehiculos;
    }
    return vehiculos.filter((v: Vehiculo) => v.placa?.toLowerCase().includes(term));
  }, [vehiculos, vehiculoSearch]);

  const rutasFiltradas = useMemo(() => {
    const term = rutaSearch.trim().toLowerCase();
    if (!term) {
      return rutasDelCliente;
    }
    return rutasDelCliente.filter((r: Ruta) => {
      const nombre = (r.nombre || '').toLowerCase();
      const origenDestino = `${r.origen || ''} ${r.destino || ''}`.trim().toLowerCase();
      return nombre.includes(term) || origenDestino.includes(term);
    });
  }, [rutasDelCliente, rutaSearch]);

  const rutasOrdenadas = useMemo(() => {
    return [...rutasDelCliente].sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''));
  }, [rutasDelCliente]);

  const clienteSeleccionado = useMemo(() => {
    return clientes.find((c: Cliente) => c.id === selectedCliente) || null;
  }, [clientes, selectedCliente]);

  const vehiculoSeleccionado = useMemo(() => {
    return vehiculos.find((v: Vehiculo) => v.id === selectedVehiculo) || null;
  }, [vehiculos, selectedVehiculo]);

  const rutaSeleccionada = useMemo(() => {
    return rutasDelCliente.find((r: Ruta) => r.id === selectedRuta) || null;
  }, [rutasDelCliente, selectedRuta]);

  const getTiposCarga = (tramo: ResumenTramoDetalle) => {
    const cargas = new Set(tramo.detalles.map((detalle) => detalle.tipo_carga));
    const orden = ['VACIO', 'CARGADO'];
    return Array.from(cargas).sort((a, b) => orden.indexOf(a) - orden.indexOf(b));
  };

  const getDropdownMaxHeight = useCallback(
    (rect: DOMRect) => {
      const available = window.innerHeight - rect.bottom - 16;
      const base = Math.max(220, available);
      if (resumen) {
        return Math.min(base, 360);
      }
      return base;
    },
    [resumen]
  );

  const updateClienteDropdown = useCallback(() => {
    if (!clienteButtonRef.current) {
      return;
    }
    const rect = clienteButtonRef.current.getBoundingClientRect();
    setClienteDropdownStyle({
      top: rect.bottom + 8,
      left: rect.left,
      width: rect.width,
    });
    setClienteListHeight(getDropdownMaxHeight(rect));
  }, [getDropdownMaxHeight]);

  const updateVehiculoDropdown = useCallback(() => {
    if (!vehiculoButtonRef.current) {
      return;
    }
    const rect = vehiculoButtonRef.current.getBoundingClientRect();
    setVehiculoDropdownStyle({
      top: rect.bottom + 8,
      left: rect.left,
      width: rect.width,
    });
    setVehiculoListHeight(getDropdownMaxHeight(rect));
  }, [getDropdownMaxHeight]);

  const updateRutaDropdown = useCallback(() => {
    if (!rutaButtonRef.current) {
      return;
    }
    const rect = rutaButtonRef.current.getBoundingClientRect();
    setRutaDropdownStyle({
      top: rect.bottom + 8,
      left: rect.left,
      width: rect.width,
    });
    setRutaListHeight(getDropdownMaxHeight(rect));
  }, [getDropdownMaxHeight]);

  useEffect(() => {
    if (!clienteOpen) {
      return;
    }
    updateClienteDropdown();
    const handler = () => updateClienteDropdown();
    window.addEventListener('resize', handler);
    window.addEventListener('scroll', handler, true);
    return () => {
      window.removeEventListener('resize', handler);
      window.removeEventListener('scroll', handler, true);
    };
  }, [clienteOpen, updateClienteDropdown]);

  useEffect(() => {
    if (!vehiculoOpen) {
      return;
    }
    updateVehiculoDropdown();
    const handler = () => updateVehiculoDropdown();
    window.addEventListener('resize', handler);
    window.addEventListener('scroll', handler, true);
    return () => {
      window.removeEventListener('resize', handler);
      window.removeEventListener('scroll', handler, true);
    };
  }, [vehiculoOpen, updateVehiculoDropdown]);

  useEffect(() => {
    if (!rutaOpen) {
      return;
    }
    updateRutaDropdown();
    const handler = () => updateRutaDropdown();
    window.addEventListener('resize', handler);
    window.addEventListener('scroll', handler, true);
    return () => {
      window.removeEventListener('resize', handler);
      window.removeEventListener('scroll', handler, true);
    };
  }, [rutaOpen, updateRutaDropdown]);

  const handleCalcularResumen = async () => {
    if (!selectedRuta || !selectedVehiculo) {
      setError('Selecciona una ruta y un vehículo');
      return;
    }

    setIsLoadingResumen(true);
    setError('');

    try {
      const data = await api.getResumenRuta(
        selectedRuta,
        selectedVehiculo,
        precioGalon ? Number(precioGalon) : undefined
      );
      setResumen(data);
      if (!precioGalon) {
        setPrecioGalon(data?.resumen_combustible?.precio_galon || '');
      }
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
      <div className="relative z-40 grid grid-cols-1 md:grid-cols-4 gap-4 overflow-visible">
        {/* Cliente */}
        <div
          className="card relative overflow-visible"
          tabIndex={0}
          onBlur={(e) => {
            if (!e.currentTarget.contains(e.relatedTarget as Node)) {
              setClienteOpen(false);
            }
          }}
        >
          <label className="label-base">Cliente</label>
          <button
            type="button"
            className="input-base flex items-center justify-between bg-white text-neutral-900"
            onClick={() => {
              setVehiculoOpen(false);
              setRutaOpen(false);
              if (!clienteOpen) {
                updateClienteDropdown();
              }
              setClienteOpen((prev) => !prev);
            }}
            ref={clienteButtonRef}
          >
            <span className={clienteSeleccionado ? 'text-neutral-900' : 'text-neutral-400'}>
              {clienteSeleccionado?.nombre || '-- Selecciona un cliente --'}
            </span>
            <span className="text-neutral-400">▾</span>
          </button>
          {clienteOpen && (
            <div
              className="fixed z-50 rounded-lg border border-neutral-200 bg-white shadow-lg"
              style={clienteDropdownStyle}
            >
              <div className="p-2">
                <input
                  type="text"
                  placeholder="Buscar cliente..."
                  className="input-base bg-white text-neutral-900"
                  value={clienteSearch}
                  onChange={(e) => setClienteSearch(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="dropdown-list bg-white" style={{ maxHeight: clienteListHeight }}>
                {clientesFiltrados.length === 0 ? (
                  <div className="px-3 py-2 text-sm text-neutral-500">Sin resultados</div>
                ) : (
                  clientesFiltrados.map((c: Cliente) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => {
                        setSelectedCliente(c.id);
                        setSelectedRuta(null);
                        setRutaSearch('');
                        setClienteSearch('');
                        setClienteOpen(false);
                      }}
                      className="dropdown-option w-full px-3 py-2 text-left text-sm"
                    >
                      {c.nombre}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Vehículo */}
        <div
          className="card relative overflow-visible"
          tabIndex={0}
          onBlur={(e) => {
            if (!e.currentTarget.contains(e.relatedTarget as Node)) {
              setVehiculoOpen(false);
            }
          }}
        >
          <label className="label-base">Vehículo</label>
          <button
            type="button"
            className="input-base flex items-center justify-between bg-white text-neutral-900"
            onClick={() => {
              setClienteOpen(false);
              setRutaOpen(false);
              if (!vehiculoOpen) {
                updateVehiculoDropdown();
              }
              setVehiculoOpen((prev) => !prev);
            }}
            ref={vehiculoButtonRef}
          >
            <span className={vehiculoSeleccionado ? 'text-neutral-900' : 'text-neutral-400'}>
              {vehiculoSeleccionado?.placa || '-- Selecciona un vehículo --'}
            </span>
            <span className="text-neutral-400">▾</span>
          </button>
          {vehiculoOpen && (
            <div
              className="fixed z-50 rounded-lg border border-neutral-200 bg-white shadow-lg"
              style={vehiculoDropdownStyle}
            >
              <div className="p-2">
                <input
                  type="text"
                  placeholder="Buscar vehículo..."
                  className="input-base bg-white text-neutral-900"
                  value={vehiculoSearch}
                  onChange={(e) => setVehiculoSearch(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="dropdown-list bg-white" style={{ maxHeight: vehiculoListHeight }}>
                {vehiculosFiltrados.length === 0 ? (
                  <div className="px-3 py-2 text-sm text-neutral-500">Sin resultados</div>
                ) : (
                  vehiculosFiltrados.map((v: Vehiculo) => (
                    <button
                      key={v.id}
                      type="button"
                      onClick={() => {
                        setSelectedVehiculo(v.id);
                        setVehiculoSearch('');
                        setVehiculoOpen(false);
                      }}
                      className="dropdown-option w-full px-3 py-2 text-left text-sm"
                    >
                      {v.placa}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Ruta */}
        <div
          className="card relative overflow-visible"
          tabIndex={0}
          onBlur={(e) => {
            if (!e.currentTarget.contains(e.relatedTarget as Node)) {
              setRutaOpen(false);
            }
          }}
        >
          <label className="label-base">Ruta</label>
          <button
            type="button"
            className="input-base flex items-center justify-between bg-white text-neutral-900 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={() => {
              if (!selectedCliente) {
                return;
              }
              setClienteOpen(false);
              setVehiculoOpen(false);
              if (!rutaOpen) {
                updateRutaDropdown();
              }
              setRutaOpen((prev) => !prev);
            }}
            disabled={!selectedCliente}
            ref={rutaButtonRef}
          >
            <span className={rutaSeleccionada ? 'text-neutral-900' : 'text-neutral-400'}>
              {rutaSeleccionada
                ? rutaSeleccionada.nombre || `${rutaSeleccionada.origen || ''} → ${rutaSeleccionada.destino || ''}`.trim()
                : '-- Selecciona una ruta --'}
            </span>
            <span className="text-neutral-400">▾</span>
          </button>
          {selectedCliente && rutaOpen && (
            <div
              className="fixed z-50 rounded-lg border border-neutral-200 bg-white shadow-lg"
              style={rutaDropdownStyle}
            >
              <div className="p-2">
                <input
                  type="text"
                  placeholder="Buscar ruta..."
                  className="input-base bg-white text-neutral-900"
                  value={rutaSearch}
                  onChange={(e) => setRutaSearch(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="dropdown-list bg-white" style={{ maxHeight: rutaListHeight }}>
                {rutasFiltradas.length === 0 ? (
                  <div className="px-3 py-2 text-sm text-neutral-500">Sin resultados</div>
                ) : (
                  rutasOrdenadas
                    .filter((r: Ruta) => rutasFiltradas.some((rf: Ruta) => rf.id === r.id))
                    .map((r: Ruta) => (
                      <button
                        key={r.id}
                        type="button"
                        onClick={() => {
                          setSelectedRuta(r.id);
                          setRutaSearch('');
                          setRutaOpen(false);
                        }}
                        className="dropdown-option w-full px-3 py-2 text-left text-sm"
                      >
                        {r.nombre || `${r.origen || ''} → ${r.destino || ''}`.trim()}
                      </button>
                    ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Precio Galon */}
        <div className="card">
          <label className="label-base">Precio del galón (opcional)</label>
          <input
            type="number"
            min={1}
            placeholder="Ej: 9500"
            value={precioGalon}
            onChange={(e) => setPrecioGalon(e.target.value ? Number(e.target.value) : '')}
            className="input-base"
          />
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
          {/* Header Resumen */}
          <div className="relative overflow-hidden rounded-2xl border border-neutral-200 bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-700 text-white">
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.35),transparent_55%)]"></div>
            <div className="relative p-6 md:p-8">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-widest text-neutral-300">Costo por rutas</p>
                  <h2 className="text-2xl md:text-3xl font-bold mt-1">{resumen.ruta.nombre}</h2>
                  <p className="text-neutral-300 mt-1">Cliente: {resumen.ruta.cliente}</p>
                </div>
                <div className="flex items-center gap-3 bg-white/10 border border-white/10 rounded-xl px-4 py-3">
                  <Truck className="w-5 h-5 text-neutral-200" />
                  <div>
                    <p className="text-xs text-neutral-300">Vehículo</p>
                    <p className="font-semibold">{resumen.vehiculo.placa}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-7 gap-3 mt-6">
                <div className="rounded-xl bg-white/10 border border-white/10 p-3">
                  <p className="text-xs text-neutral-300">KM Totales</p>
                  <p className="text-lg font-semibold">{formatKm(resumen.resumen_distancia.km_totales)} km</p>
                </div>
                <div className="rounded-xl bg-white/10 border border-white/10 p-3">
                  <p className="text-xs text-neutral-300">Galones</p>
                  <p className="text-lg font-semibold">{resumen.resumen_combustible.galones_totales_requeridos.toFixed(2)}</p>
                </div>
                <div className="rounded-xl bg-white/10 border border-white/10 p-3">
                  <p className="text-xs text-neutral-300">Precio galón</p>
                  <p className="text-lg font-semibold">{formatCOP(resumen.resumen_combustible.precio_galon)}</p>
                </div>
                <div className="rounded-xl bg-white/10 border border-white/10 p-3">
                  <p className="text-xs text-neutral-300">Costo combustible</p>
                  <p className="text-lg font-semibold">{formatCOP(resumen.resumen_combustible.costo_total_combustible)}</p>
                </div>
                <div className="rounded-xl bg-white/10 border border-white/10 p-3">
                  <p className="text-xs text-neutral-300">Costo peajes</p>
                  <p className="text-lg font-semibold">{formatCOP(resumen.resumen_peajes.costo_total_peajes)}</p>
                </div>
                <div className="rounded-xl bg-amber-500/15 border border-amber-300/30 p-3 md:col-span-2 shadow-[0_0_24px_rgba(251,191,36,0.25)]">
                  <p className="text-xs text-neutral-300">Costo total</p>
                  <p className="text-3xl md:text-4xl font-bold tracking-tight text-amber-300 drop-shadow-sm">
                    {formatCOP(resumen.costo_total_ruta.costo_total)}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Linea de ruta */}
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <Route className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-bold text-neutral-900">Línea de Ruta</h3>
            </div>
            <div className="rounded-2xl overflow-hidden border border-neutral-200 bg-neutral-50">
              <div className="px-3 pt-3 pb-4">
                <div className="flex w-full gap-3 items-stretch">
                  {resumen.tramos_detalle.map((tramo: ResumenTramoDetalle) => (
                    <div
                      key={tramo.tramo_id}
                      className="flex flex-col"
                      style={{ flex: `${Math.max(tramo.km_totales, 1)} 1 0%` }}
                    >
                      <div className="relative text-white bg-gradient-to-br from-blue-600 via-blue-500 to-sky-400 p-4 rounded-2xl shadow-lg h-full min-h-[210px]">
                        <p className="text-xs uppercase tracking-widest text-white/80">Tramo {tramo.orden}</p>
                        <p className="text-base font-semibold mt-1 line-clamp-2">{tramo.nombre}</p>
                        <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                          <div className="bg-white/15 rounded-lg p-2">
                            <p className="text-white/80">KM</p>
                            <p className="font-semibold">{formatKm(tramo.km_totales)}</p>
                          </div>
                          <div className="bg-white/15 rounded-lg p-2">
                            <p className="text-white/80">Gal</p>
                            <p className="font-semibold">{tramo.galones_totales.toFixed(2)}</p>
                          </div>
                          <div className="bg-white/15 rounded-lg p-2 col-span-2">
                            <p className="text-white/80">Peajes</p>
                            <p className="font-semibold">{tramo.cantidad_peajes} · {formatCOP(tramo.costo_peajes)}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="relative mt-4">
                  <div className="h-1 bg-gradient-to-r from-blue-300 via-blue-200 to-blue-300 rounded-full"></div>
                  <div className="absolute inset-0 flex">
                    {resumen.tramos_detalle.map((tramo: ResumenTramoDetalle, index: number) => (
                      <div
                        key={`marker-${tramo.tramo_id}`}
                        className="relative"
                        style={{ flex: `${Math.max(tramo.km_totales, 1)} 1 0%` }}
                      >
                        {index === 0 && (
                          <div className="absolute left-0 -top-1 w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_0_3px_rgba(191,219,254,0.6)]"></div>
                        )}
                        {index < resumen.tramos_detalle.length - 1 && (
                          <div className="absolute right-0 -top-1 w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_0_3px_rgba(191,219,254,0.6)]"></div>
                        )}
                        {index === resumen.tramos_detalle.length - 1 && (
                          <div className="absolute right-0 -top-1 w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_0_3px_rgba(191,219,254,0.6)]"></div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-3 flex">
                  {resumen.tramos_detalle.map((tramo: ResumenTramoDetalle) => (
                    <div
                      key={`carga-${tramo.tramo_id}`}
                      className="flex justify-center"
                      style={{ flex: `${Math.max(tramo.km_totales, 1)} 1 0%` }}
                    >
                      <div className="flex flex-wrap items-center justify-center gap-2">
                        {getTiposCarga(tramo).map((tipo) => {
                          const isCargado = tipo === 'CARGADO';
                          const Icon = isCargado ? Package : Truck;
                          const label = isCargado ? 'Cargado' : 'Vacio';
                          return (
                            <span
                              key={`${tramo.tramo_id}-${tipo}`}
                              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs md:text-sm font-semibold tracking-wide bg-blue-50 text-blue-700 border border-blue-200 shadow-sm"
                            >
                              <Icon className="w-4 h-4" />
                              {label}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Detalles de Tramos */}
          <div className="card">
            <h2 className="text-lg font-bold text-neutral-900 mb-4">Detalles por Tramo</h2>
            <div className="w-full bg-neutral-50 rounded-xl border border-neutral-200 p-4 mb-4">
              <p className="text-sm font-semibold text-neutral-600 mb-3">Rendimiento del vehiculo</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                {Object.entries(resumen.configuracion_vehiculo.rendimientos_configurados || {}).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between bg-white rounded-md px-2 py-1 border border-neutral-200">
                    <span className="text-neutral-500">{key.replace('-', ' · ')}</span>
                    <span className="font-semibold text-neutral-900">{Number(value).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-4">
              {resumen.tramos_detalle.map((tramo) => (
                <div key={tramo.tramo_id} className="border border-neutral-200 rounded-xl p-4">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-widest text-neutral-500">Tramo {tramo.orden}</p>
                      <p className="font-semibold text-neutral-900">{tramo.nombre}</p>
                    </div>
                    <div className="flex flex-wrap gap-3 text-sm text-neutral-600">
                      <span>KM: <strong className="text-neutral-900">{formatKm(tramo.km_totales)}</strong></span>
                      <span>Gal: <strong className="text-neutral-900">{tramo.galones_totales.toFixed(2)}</strong></span>
                      <span>Peajes: <strong className="text-neutral-900">{tramo.cantidad_peajes}</strong></span>
                      <span>Costo peajes: <strong className="text-neutral-900">{formatCOP(tramo.costo_peajes)}</strong></span>
                    </div>
                  </div>

                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-neutral-50 rounded-lg p-3">
                      <p className="text-xs font-semibold text-neutral-600 mb-2">Detalle de consumo</p>
                      <div className="space-y-2">
                        {tramo.detalles.map((detalle, idx) => (
                          <div key={idx} className="flex items-center justify-between text-sm">
                            <span className="text-neutral-600">{detalle.tipo_carga} · {detalle.tipo_terreno} · {formatKm(detalle.kilometros)} km</span>
                            <span className="font-medium text-neutral-900">{detalle.galones_necesarios.toFixed(2)} gal</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-neutral-50 rounded-lg p-3">
                      <p className="text-xs font-semibold text-neutral-600 mb-2">Peajes en este tramo</p>
                      {tramo.peajes.length === 0 ? (
                        <p className="text-sm text-neutral-500">Sin peajes asociados</p>
                      ) : (
                        <div className="space-y-2">
                          {tramo.peajes.map((peaje) => (
                            <div key={peaje.peaje_id} className="flex items-center justify-between text-sm">
                              <span className="text-neutral-600">{peaje.nombre}{peaje.sector ? ` (${peaje.sector})` : ''}</span>
                              <span className="font-medium text-neutral-900">{formatCOP(peaje.costo)}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
