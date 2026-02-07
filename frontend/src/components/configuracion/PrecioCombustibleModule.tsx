import { useState, useEffect } from 'react';
import { DollarSign, Save, AlertCircle, CheckCircle } from 'lucide-react';
import axiosInstance from '../../services/axiosInstance';
import api from '../../services/api';
import { formatCOP, formatDateTime } from '../../utils/format';

export default function PrecioCombustibleModule() {
  const [precio, setPrecio] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [existingConfig, setExistingConfig] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    loadPrecioCombustible();
    loadHistorial();
  }, []);

  const loadPrecioCombustible = async () => {
    try {
      setLoadingData(true);
      const response = await axiosInstance.get('/configuracion/precio_galon');
      setExistingConfig(response.data);
      setPrecio(response.data.valor);
      setDescripcion(response.data.descripcion || '');
    } catch (err: any) {
      // Si no existe, no pasa nada, se puede crear
      if (err.response?.status !== 404) {
        console.error('Error al cargar precio:', err);
      }
    } finally {
      setLoadingData(false);
    }
  };

  const loadHistorial = async () => {
    try {
      const data = await api.getConfiguraciones();
      const items = (data?.items || data || []).filter((item: any) => item.clave !== 'precio_galon');
      const sorted = items.sort((a: any, b: any) => {
        const aDate = new Date(a.updated_at || a.created_at || 0).getTime();
        const bDate = new Date(b.updated_at || b.created_at || 0).getTime();
        return bDate - aDate;
      });
      setHistory(sorted);
    } catch (err) {
      setHistory([]);
    }
  };

  const getNextPrecioKey = (items: any[]) => {
    const max = items.reduce((acc, item) => {
      const match = typeof item.clave === 'string' ? item.clave.match(/^precio_(\d+)$/) : null;
      if (!match) return acc;
      const value = Number(match[1]);
      return Number.isFinite(value) && value > acc ? value : acc;
    }, 0);
    return `precio_${max + 1}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const data = await api.getConfiguraciones();
      const items = data?.items || data || [];
      const newKey = getNextPrecioKey(items);
      const valorNumerico = String(precioValue);

      await axiosInstance.post('/configuracion/', {
        clave: newKey,
        valor: valorNumerico,
        descripcion: descripcion || 'Precio del galón de combustible'
      });

      await axiosInstance.put('/configuracion/precio_galon', {
        valor: valorNumerico,
        descripcion: descripcion
      });

      setSuccess('Precio actualizado exitosamente');
      
      // Recargar datos
      await loadPrecioCombustible();
      await loadHistorial();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar el precio');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (value: string) => {
    // Remover todo excepto números
    const numbers = value.replace(/[^0-9]/g, '');
    // Formatear con separadores de miles
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  const handlePrecioChange = (value: string) => {
    const formatted = formatNumber(value);
    setPrecio(formatted);
  };

  const precioValue = Number(precio.replace(/[^0-9]/g, ''));

  if (loadingData) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-gray-600 mt-4">Cargando configuración...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">💰 Precio del Combustible</h2>
        <p className="text-gray-600">
          Configura el precio actual del galón de combustible. Este valor se usará para calcular 
          los costos de todas las rutas.
        </p>
      </div>

      {error && (
        <div className="mb-6 flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-xl">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
          <p className="text-sm text-green-600">{success}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="bg-blue-600 p-4 rounded-xl">
              <DollarSign className="w-8 h-8 text-white" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Precio por Galón
              </label>
              <p className="text-xs text-gray-500">En pesos colombianos (COP)</p>
            </div>
          </div>

          <div className="relative">
            <span className="absolute left-4 top-4 text-3xl font-bold text-gray-400">$</span>
            <input
              type="text"
              className="w-full pl-14 pr-6 py-4 text-3xl font-bold border-2 border-blue-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white"
              placeholder="9,500"
              value={precio}
              onChange={(e) => handlePrecioChange(e.target.value)}
              required
            />
          </div>

          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              Valor actual: <span className="font-bold text-blue-700 text-lg">{formatCOP(precioValue)}</span>
            </p>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Descripción (Opcional)
          </label>
          <textarea
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 resize-none"
            placeholder="Ej: Precio actualizado según la estación de servicio XYZ"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            rows={3}
          />
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            {existingConfig ? (
              <>
                <span className="font-medium">Última actualización:</span>{' '}
                {formatDateTime(existingConfig.updated_at || existingConfig.created_at)}
              </>
            ) : (
              'No hay precio configurado aún'
            )}
          </p>

          <button
            type="submit"
            disabled={loading || !precio}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold px-6 py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
          >
            <Save className="w-5 h-5" />
            {loading ? 'Guardando...' : existingConfig ? 'Actualizar Precio' : 'Guardar Precio'}
          </button>
        </div>
      </form>

      {/* Información adicional */}
      <div className="mt-8 p-5 bg-amber-50 border-l-4 border-amber-500 rounded-lg">
        <h3 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          Importante
        </h3>
        <ul className="text-sm text-amber-800 space-y-2">
          <li>• El precio se aplicará automáticamente a todos los cálculos de rutas</li>
          <li>• Puedes actualizar este valor cuando cambien los precios del combustible</li>
          <li>• Solo tu empresa verá y podrá modificar este valor</li>
          <li>• Los cálculos existentes se actualizarán con el nuevo precio</li>
        </ul>
      </div>

      <div className="mt-10">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Historial de actualizaciones</h3>
        <div className="border border-neutral-200 rounded-lg overflow-hidden max-h-[320px] overflow-y-auto">
          <table className="w-full">
            <thead className="bg-white">
              <tr className="border-b border-neutral-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Fecha de actualización</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Valor</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-700">Descripción</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="px-4 py-3 text-sm text-neutral-600">
                    {formatDateTime(item.updated_at || item.created_at)}
                  </td>
                  <td className="px-4 py-3 text-sm text-neutral-900">{formatCOP(item.valor)}</td>
                  <td className="px-4 py-3 text-sm text-neutral-600">{item.descripcion || 'N/A'}</td>
                </tr>
              ))}
              {history.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-4 py-4 text-sm text-neutral-500">
                    No hay historial disponible.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
