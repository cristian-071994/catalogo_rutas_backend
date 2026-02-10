import type { ComponentType } from 'react';
import {
  AlertCircle,
  BarChart3,
  BookOpen,
  Building2,
  CheckCircle,
  Route,
  Settings,
  ShieldCheck,
  Truck,
  UserCog,
  Wrench
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { canAccessConfig, hasAnyPermission, hasPermission } from '../utils/permissions';

type GuiaModulo = {
  id: string;
  title: string;
  description: string;
  icon: ComponentType<{ className?: string }>;
  available: boolean;
  actions: string[];
  steps: string[];
  tips?: string[];
};

const ROLE_LABELS: Record<string, string> = {
  super_admin: 'Super Admin',
  admin: 'Administrador',
  supervisor: 'Supervisor',
  gestor_rutas: 'Gestor de Rutas',
  gestor_peajes: 'Gestor de Peajes',
  gestor_clientes: 'Gestor de Clientes',
  consultor: 'Consultor'
};

const MODULE_STYLES: Record<string, {
  header: string;
  iconBg: string;
  iconText: string;
  actionBg: string;
  actionBorder: string;
  actionTitle: string;
}> = {
  resumen: {
    header: 'from-sky-500 to-blue-600',
    iconBg: 'bg-sky-100',
    iconText: 'text-sky-700',
    actionBg: 'bg-sky-50',
    actionBorder: 'border-sky-200',
    actionTitle: 'text-sky-800'
  },
  clientes: {
    header: 'from-emerald-500 to-green-600',
    iconBg: 'bg-emerald-100',
    iconText: 'text-emerald-700',
    actionBg: 'bg-emerald-50',
    actionBorder: 'border-emerald-200',
    actionTitle: 'text-emerald-800'
  },
  vehiculos: {
    header: 'from-indigo-500 to-violet-600',
    iconBg: 'bg-indigo-100',
    iconText: 'text-indigo-700',
    actionBg: 'bg-indigo-50',
    actionBorder: 'border-indigo-200',
    actionTitle: 'text-indigo-800'
  },
  rutas: {
    header: 'from-amber-500 to-orange-600',
    iconBg: 'bg-amber-100',
    iconText: 'text-amber-700',
    actionBg: 'bg-amber-50',
    actionBorder: 'border-amber-200',
    actionTitle: 'text-amber-800'
  },
  peajes: {
    header: 'from-rose-500 to-pink-600',
    iconBg: 'bg-rose-100',
    iconText: 'text-rose-700',
    actionBg: 'bg-rose-50',
    actionBorder: 'border-rose-200',
    actionTitle: 'text-rose-800'
  },
  config: {
    header: 'from-teal-500 to-cyan-600',
    iconBg: 'bg-teal-100',
    iconText: 'text-teal-700',
    actionBg: 'bg-teal-50',
    actionBorder: 'border-teal-200',
    actionTitle: 'text-teal-800'
  },
  admin: {
    header: 'from-slate-600 to-slate-800',
    iconBg: 'bg-slate-100',
    iconText: 'text-slate-700',
    actionBg: 'bg-slate-50',
    actionBorder: 'border-slate-200',
    actionTitle: 'text-slate-800'
  }
};

export default function GuiaPage() {
  const { usuario } = useAuth();

  const roleName = usuario?.rol?.nombre ?? 'usuario';
  const roleLabel = ROLE_LABELS[roleName] ?? roleName;

  const canManageUsers = hasAnyPermission(usuario, [
    'ver_usuarios',
    'crear_usuario',
    'editar_usuario',
    'eliminar_usuario',
    'cambiar_rol_usuario'
  ]);

  const canManageRoles = hasAnyPermission(usuario, ['gestionar_roles', 'gestionar_permisos']);
  const canManageClientes = hasAnyPermission(usuario, ['ver_clientes', 'crear_cliente', 'editar_cliente', 'eliminar_cliente']);
  const canManageVehiculos = hasAnyPermission(usuario, ['ver_vehiculos', 'crear_vehiculo', 'editar_vehiculo', 'eliminar_vehiculo']);
  const canManageRutas = hasAnyPermission(usuario, ['ver_rutas', 'crear_ruta', 'editar_ruta', 'eliminar_ruta']);
  const canManageTramos = hasAnyPermission(usuario, ['ver_tramos', 'crear_tramo', 'editar_tramo', 'eliminar_tramo']);
  const canManageTramoDetalle = hasAnyPermission(usuario, [
    'ver_tramo_detalle',
    'ver_tramo_detalles',
    'crear_tramo_detalle',
    'editar_tramo_detalle',
    'eliminar_tramo_detalle'
  ]);
  const canManagePeajes = hasAnyPermission(usuario, ['ver_peajes', 'crear_peaje', 'editar_peaje', 'eliminar_peaje']);
  const canSeeResumen = hasAnyPermission(usuario, [
    'ver_rutas',
    'ver_tramos',
    'ver_tramo_detalle',
    'ver_tramo_detalles',
    'ver_vehiculos',
    'ver_clientes',
    'ver_peajes'
  ]);
  const canManageConfig = canAccessConfig(usuario) || hasPermission(usuario, 'editar_configuracion');

  const modules: GuiaModulo[] = [
    {
      id: 'resumen',
      title: 'Resumen de rutas',
      description: 'Calcula costos por ruta y obten el desglose detallado por tramos, peajes y combustible.',
      icon: BarChart3,
      available: canSeeResumen,
      actions: [
        'Calcular el costo total por ruta',
        'Ver consumo y galones por tramo',
        'Analizar peajes y costos de combustible'
      ],
      steps: [
        'Ir a Dashboard > Resumen de rutas',
        'Seleccionar cliente, vehiculo y ruta',
        'Ingresar precio del galon si es necesario',
        'Hacer clic en Calcular Resumen'
      ]
    },
    {
      id: 'clientes',
      title: 'Clientes',
      description: 'Registra y administra clientes con su informacion comercial.',
      icon: Building2,
      available: canManageClientes,
      actions: [
        'Crear, editar y eliminar clientes',
        'Ver los clientes de tu empresa'
      ],
      steps: [
        'Ir a Dashboard > Clientes',
        'Crear un nuevo cliente con NIT y contacto',
        'Actualizar datos cuando cambien'
      ]
    },
    {
      id: 'vehiculos',
      title: 'Vehiculos',
      description: 'Gestiona la flota y su configuracion tecnica para los calculos.',
      icon: Truck,
      available: canManageVehiculos,
      actions: [
        'Registrar vehiculos y su configuracion',
        'Actualizar rendimientos segun el terreno'
      ],
      steps: [
        'Ir a Dashboard > Vehiculos',
        'Crear el vehiculo con placa y configuracion',
        'Verificar rendimientos asignados'
      ]
    },
    {
      id: 'rutas',
      title: 'Rutas y tramos',
      description: 'Define rutas por cliente y agrega tramos con su detalle operativo.',
      icon: Route,
      available: canManageRutas || canManageTramos || canManageTramoDetalle,
      actions: [
        'Crear rutas por cliente',
        'Agregar tramos y detalles por terreno',
        'Mantener orden y distancias'
      ],
      steps: [
        'Ir a Dashboard > Rutas',
        'Crear la ruta y asociarla a un cliente',
        'Agregar tramos y sus detalles de terreno'
      ],
      tips: ['Mantener las distancias exactas mejora el calculo de consumo.']
    },
    {
      id: 'peajes',
      title: 'Peajes',
      description: 'Administra peajes y su costo para cada tramo.',
      icon: Wrench,
      available: canManagePeajes,
      actions: [
        'Crear y actualizar peajes',
        'Asignar peajes a tramos'
      ],
      steps: [
        'Ir a Dashboard > Peajes',
        'Crear o actualizar los costos',
        'Relacionar peajes con los tramos'
      ]
    },
    {
      id: 'config',
      title: 'Configuracion del sistema',
      description: 'Ajusta valores globales que afectan los calculos.',
      icon: Settings,
      available: canManageConfig,
      actions: [
        'Actualizar precio del galon',
        'Administrar marcas y configuraciones',
        'Definir rendimientos por terreno'
      ],
      steps: [
        'Ir a Dashboard > Configuracion',
        'Actualizar precio del galon cuando cambie',
        'Mantener marcas y rendimientos al dia'
      ]
    },
    {
      id: 'admin',
      title: 'Administracion',
      description: 'Gestiona usuarios, roles y permisos del sistema.',
      icon: ShieldCheck,
      available: canManageUsers || canManageRoles,
      actions: [
        'Crear y aprobar usuarios',
        'Asignar roles y permisos',
        'Revisar accesos por empresa'
      ],
      steps: [
        'Ir a Dashboard > Administracion',
        'Crear usuarios y definir roles',
        'Ajustar permisos segun funciones'
      ]
    }
  ];

  const availableModules = modules.filter((module) => module.available);
  const lockedModules = modules.filter((module) => !module.available);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 mb-8">
          <div className="flex items-center gap-4">
            <div className="bg-blue-100 p-3 rounded-xl">
              <BookOpen className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Guia de uso por rol</h1>
              <p className="text-gray-600 mt-1">
                Instrucciones enfocadas en lo que tu rol puede hacer dentro del sistema.
              </p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-gray-200 p-4 bg-gray-50">
              <p className="text-xs uppercase tracking-widest text-gray-500">Rol actual</p>
              <p className="text-lg font-semibold text-gray-900 mt-1">{roleLabel}</p>
            </div>
            <div className="rounded-xl border border-gray-200 p-4 bg-gray-50">
              <p className="text-xs uppercase tracking-widest text-gray-500">Permisos activos</p>
              <p className="text-lg font-semibold text-gray-900 mt-1">{usuario?.permisos?.length ?? 0}</p>
            </div>
            <div className="rounded-xl border border-gray-200 p-4 bg-gray-50">
              <p className="text-xs uppercase tracking-widest text-gray-500">Acceso</p>
              <p className="text-lg font-semibold text-gray-900 mt-1">
                {usuario ? 'Habilitado' : 'Sin sesion'}
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {availableModules.map((module) => {
            const Icon = module.icon;
            const styles = MODULE_STYLES[module.id] ?? MODULE_STYLES.resumen;
            return (
              <div key={module.id} className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className={`px-6 py-4 border-b border-gray-200 bg-gradient-to-r ${styles.header}`}>
                  <div className="flex items-center gap-3">
                    <div className={`${styles.iconBg} p-2 rounded-lg`}
                    >
                      <Icon className={`w-5 h-5 ${styles.iconText}`} />
                    </div>
                    <div>
                      <h2 className="text-lg font-bold text-white">{module.title}</h2>
                      <p className="text-sm text-white/85">{module.description}</p>
                    </div>
                  </div>
                </div>
                <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className={`rounded-xl border ${styles.actionBorder} ${styles.actionBg} p-4`}>
                    <h3 className={`text-sm font-semibold ${styles.actionTitle} mb-3`}>Que puedes hacer</h3>
                    <ul className="space-y-2 text-gray-700">
                      {module.actions.map((action) => (
                        <li key={action} className="flex items-start gap-2">
                          <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className={`rounded-xl border ${styles.actionBorder} ${styles.actionBg} p-4`}>
                    <h3 className={`text-sm font-semibold ${styles.actionTitle} mb-3`}>Como hacerlo</h3>
                    <ol className="space-y-2 text-gray-700 list-decimal list-inside">
                      {module.steps.map((step) => (
                        <li key={step}>{step}</li>
                      ))}
                    </ol>
                    {module.tips && (
                      <div className="mt-4 rounded-lg bg-blue-50 border border-blue-200 p-3 text-sm text-blue-700">
                        {module.tips.map((tip) => (
                          <p key={tip}>{tip}</p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {lockedModules.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6 mt-8">
            <div className="flex items-center gap-3 mb-4">
              <UserCog className="w-5 h-5 text-amber-500" />
              <h3 className="text-lg font-bold text-gray-900">Accesos restringidos</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Estos modulos requieren permisos adicionales. Si necesitas acceso, contacta a tu administrador.
            </p>
            <div className="flex flex-wrap gap-2">
              {lockedModules.map((module) => (
                <span key={module.id} className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-600">
                  {module.title}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 mt-8">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-blue-600 mt-0.5" />
            <div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">Buenas practicas</h3>
              <ul className="space-y-2 text-blue-800">
                <li>Trabaja siempre con datos de tu empresa; el sistema aplica aislamiento por empresa.</li>
                <li>Actualiza el precio del galon cuando cambie para mantener calculos precisos.</li>
                <li>Verifica que los tramos tengan distancias reales para resultados confiables.</li>
                <li>Si algo no aparece en el menu, revisa los permisos asignados a tu rol.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
