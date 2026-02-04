import { CheckCircle, AlertCircle, ArrowRight, BookOpen } from 'lucide-react';

export default function GuiaPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="bg-blue-100 p-3 rounded-xl">
              <BookOpen className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Guía de Configuración del Sistema
              </h1>
              <p className="text-gray-600 mt-1">
                Paso a paso para configurar tu empresa y comenzar a gestionar rutas
              </p>
            </div>
          </div>
        </div>

        {/* Pasos */}
        <div className="space-y-6">
          {/* Paso 1 */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="bg-white rounded-full w-10 h-10 flex items-center justify-center">
                  <span className="text-blue-600 font-bold text-lg">1</span>
                </div>
                <h2 className="text-xl font-bold text-white">
                  Configuración Inicial
                </h2>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Precio del Combustible
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Ve a <span className="font-semibold text-blue-600">Configuración {'>'} Precio Combustible</span>
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
                    <li>Ingresa el precio actual del galón de combustible (ej: $9,500)</li>
                    <li>Este valor se usará para calcular costos de todas las rutas</li>
                    <li>Puedes actualizarlo cuando cambien los precios</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Paso 2 */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="bg-white rounded-full w-10 h-10 flex items-center justify-center">
                  <span className="text-indigo-600 font-bold text-lg">2</span>
                </div>
                <h2 className="text-xl font-bold text-white">
                  Crear Clientes
                </h2>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Registro de Clientes
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Ve a <span className="font-semibold text-indigo-600">Dashboard {'>'} Clientes</span>
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
                    <li>Haz clic en <span className="font-semibold">"Nuevo Cliente"</span></li>
                    <li>Completa: NIT, nombre, teléfono, email, dirección</li>
                    <li>Los clientes se asociarán automáticamente a tu empresa</li>
                    <li>Solo verás y podrás gestionar los clientes de tu empresa</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Paso 3 */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="bg-white rounded-full w-10 h-10 flex items-center justify-center">
                  <span className="text-purple-600 font-bold text-lg">3</span>
                </div>
                <h2 className="text-xl font-bold text-white">
                  Configurar Vehículos
                </h2>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Registro de Vehículos de tu Flota
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Ve a <span className="font-semibold text-purple-600">Dashboard {'>'} Vehículos</span>
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
                    <li>Haz clic en <span className="font-semibold">"Nuevo Vehículo"</span></li>
                    <li>Ingresa placa, marca, modelo, tipo de carga</li>
                    <li>El sistema ya tiene precargadas las marcas y rendimientos estándar</li>
                    <li>Cada vehículo tendrá rendimientos según su configuración (tipo de terreno y carga)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Paso 4 */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="bg-white rounded-full w-10 h-10 flex items-center justify-center">
                  <span className="text-green-600 font-bold text-lg">4</span>
                </div>
                <h2 className="text-xl font-bold text-white">
                  Crear Rutas
                </h2>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Definir Rutas para tus Clientes
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Ve a <span className="font-semibold text-green-600">Dashboard {'>'} Rutas</span>
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
                    <li>Haz clic en <span className="font-semibold">"Nueva Ruta"</span></li>
                    <li>Selecciona el cliente (solo verás tus clientes)</li>
                    <li>Define nombre y descripción de la ruta</li>
                    <li>La ruta se asocia automáticamente a tu empresa</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Paso 5 */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-amber-500 to-amber-600 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="bg-white rounded-full w-10 h-10 flex items-center justify-center">
                  <span className="text-amber-600 font-bold text-lg">5</span>
                </div>
                <h2 className="text-xl font-bold text-white">
                  Agregar Tramos a las Rutas
                </h2>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Configurar Segmentos de la Ruta
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Desde la vista de detalle de una ruta
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
                    <li>Cada tramo es un segmento del recorrido</li>
                    <li>Define: origen, destino, distancia (km), tipo de terreno</li>
                    <li>Tipo de terreno: <span className="font-semibold">plano, montaña, mixto</span></li>
                    <li>El sistema calculará automáticamente el consumo según el vehículo</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Paso 6 */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-rose-500 to-rose-600 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="bg-white rounded-full w-10 h-10 flex items-center justify-center">
                  <span className="text-rose-600 font-bold text-lg">6</span>
                </div>
                <h2 className="text-xl font-bold text-white">
                  Calcular Costos
                </h2>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Generar Resumen de Costos
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Ve a <span className="font-semibold text-rose-600">Dashboard {'>'} Resumen de Rutas</span>
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
                    <li>Selecciona una ruta y un vehículo</li>
                    <li>El sistema calculará:
                      <ul className="list-circle list-inside ml-6 mt-2 space-y-1">
                        <li>Consumo total de combustible</li>
                        <li>Costo total de combustible</li>
                        <li>Costos de peajes (si aplican)</li>
                        <li>Costo total del viaje</li>
                      </ul>
                    </li>
                    <li>Podrás exportar o imprimir el resumen</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Notas Importantes */}
          <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-bold text-blue-900 mb-3 text-lg">
                  Notas Importantes
                </h3>
                <ul className="space-y-3 text-blue-800">
                  <li className="flex items-start gap-2">
                    <ArrowRight className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    <span>
                      <strong>Multi-tenancy:</strong> Solo verás y podrás gestionar datos de tu empresa. No tendrás acceso a información de otras empresas.
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ArrowRight className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    <span>
                      <strong>Peajes automáticos:</strong> El sistema sincroniza peajes desde la base de datos oficial de ANI cada día a las 3:00 AM.
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ArrowRight className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    <span>
                      <strong>Sesión segura:</strong> Tu sesión expira en 30 minutos de inactividad, pero se renueva automáticamente mientras trabajas.
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ArrowRight className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    <span>
                      <strong>Roles y permisos:</strong> Tu administrador asigna permisos específicos. Si no puedes acceder a algo, contacta a tu admin.
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl shadow-lg p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-3">
              ¿Listo para comenzar?
            </h2>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Sigue estos pasos en orden y tendrás tu sistema completamente configurado en minutos.
              Cualquier duda, consulta con tu administrador del sistema.
            </p>
            <button 
              onClick={() => window.location.href = '/dashboard'}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              Ir al Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
