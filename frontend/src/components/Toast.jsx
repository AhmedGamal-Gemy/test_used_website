import { X } from 'lucide-react';

export default function Toast({ toasts, removeToast }) {
  if (!toasts || toasts.length === 0) return null;

  const typeStyles = {
    success: {
      bg: 'bg-green-50 border-green-200 text-green-800',
      icon: '✓',
      iconBg: 'bg-green-100 text-green-600',
    },
    error: {
      bg: 'bg-red-50 border-red-200 text-red-800',
      icon: '✕',
      iconBg: 'bg-red-100 text-red-600',
    },
    info: {
      bg: 'bg-blue-50 border-blue-200 text-blue-800',
      icon: 'ℹ',
      iconBg: 'bg-blue-100 text-blue-600',
    },
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80 max-w-[calc(100vw-2rem)]">
      {toasts.map((toast) => {
        const style = typeStyles[toast.type] || typeStyles.info;
        return (
          <div
            key={toast.id}
            className={`${style.bg} border rounded-lg p-4 shadow-lg flex items-start gap-3 animate-slide-in`}
            role="alert"
          >
            <div className={`w-6 h-6 rounded-full ${style.iconBg} flex items-center justify-center flex-shrink-0 text-sm font-bold`}>
              {style.icon}
            </div>
            <p className="flex-1 text-sm font-medium">{toast.message}</p>
            <button
              onClick={() => removeToast(toast.id)}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Dismiss"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
