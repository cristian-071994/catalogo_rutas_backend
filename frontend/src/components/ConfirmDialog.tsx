import { AlertTriangle, CheckCircle } from 'lucide-react';

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'success' | 'warning';
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  type = 'warning',
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const getColors = () => {
    switch (type) {
      case 'danger':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: 'text-red-600',
          iconBg: 'bg-red-100',
          button: 'bg-red-600 hover:bg-red-700',
        };
      case 'success':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: 'text-green-600',
          iconBg: 'bg-green-100',
          button: 'bg-green-600 hover:bg-green-700',
        };
      default:
        return {
          bg: 'bg-amber-50',
          border: 'border-amber-200',
          icon: 'text-amber-600',
          iconBg: 'bg-amber-100',
          button: 'bg-amber-600 hover:bg-amber-700',
        };
    }
  };

  const colors = getColors();
  const Icon = type === 'success' ? CheckCircle : AlertTriangle;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/10 backdrop-blur-lg animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full animate-scaleIn">
        {/* Header */}
        <div className={`${colors.bg} ${colors.border} border-b px-6 py-4 rounded-t-2xl`}>
          <div className="flex items-center gap-3">
            <div className={`${colors.iconBg} p-2 rounded-xl`}>
              <Icon className={`w-6 h-6 ${colors.icon}`} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-6">
          <p className="text-gray-700">{message}</p>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 rounded-b-2xl flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-5 py-2.5 border border-gray-300 text-gray-600 font-medium rounded-xl hover:bg-gray-100 transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`px-5 py-2.5 ${colors.button} text-white font-semibold rounded-xl transition-colors shadow-lg`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
