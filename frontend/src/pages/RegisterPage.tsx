import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, User, AlertCircle, Building2, CheckCircle } from 'lucide-react';
import PasswordInput from '../components/PasswordInput';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nombreCompleto, setNombreCompleto] = useState('');
  const [empresaNit, setEmpresaNit] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      const result = await register(email, password, nombreCompleto, empresaNit);
      setSuccess(result.mensaje);
      
      // Redirigir al login después de 10 segundos
      setTimeout(() => {
        navigate('/login');
      }, 10000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrarse');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md mx-auto">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-blue-600 p-2 rounded-lg">
              <User className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Crear Cuenta</h1>
          </div>
          <p className="text-gray-600 mb-8">Regístrate para unirte a tu empresa</p>

          {error && (
            <div className="mb-6 flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-6 flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-xl">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-green-800">{success}</p>
                <p className="text-xs text-green-600 mt-1">Serás redirigido al login...</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre Completo
              </label>
              <div className="relative">
                <User className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Juan Pérez"
                  value={nombreCompleto}
                  onChange={(e) => setNombreCompleto(e.target.value)}
                  required
                  disabled={isLoading || !!success}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Correo Electrónico
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="tu@empresa.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={isLoading || !!success}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                NIT de la Empresa
              </label>
              <div className="relative">
                <Building2 className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="900123456"
                  value={empresaNit}
                  onChange={(e) => setEmpresaNit(e.target.value.replace(/[^0-9]/g, ''))}
                  required
                  disabled={isLoading || !!success}
                  minLength={5}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Solo números, sin guiones</p>
            </div>

            <div>
              <PasswordInput
                label="Contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
                className={isLoading || !!success ? 'opacity-50 cursor-not-allowed' : ''}
              />
              <p className="text-xs text-gray-500 mt-1">Mínimo 6 caracteres</p>
            </div>

            <button
              type="submit"
              disabled={isLoading || !!success}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02] disabled:transform-none"
            >
              {isLoading ? 'Registrando...' : success ? 'Registro Exitoso ✓' : 'Crear Cuenta'}
            </button>
          </form>

          <p className="mt-6 text-center text-gray-600 text-sm">
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" className="text-blue-600 font-semibold hover:text-blue-700 hover:underline">
              Inicia sesión
            </Link>
          </p>

          {/* Información */}
          <div className="mt-8 p-5 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Nota:</strong> Tu cuenta quedará pendiente de aprobación por un administrador de tu empresa. 
              Recibirás acceso una vez sea aprobada.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
