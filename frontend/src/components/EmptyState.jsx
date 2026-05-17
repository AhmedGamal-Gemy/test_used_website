import { PackageX, Inbox } from 'lucide-react';

export default function EmptyState({ icon = 'package', title, description, action, className = '' }) {
  const Icon = icon === 'inbox' ? Inbox : PackageX;

  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 ${className}`}>
      <div className="bg-gray-100 p-4 rounded-full mb-4">
        <Icon className="w-10 h-10 text-gray-400" />
      </div>
      {title && <h3 className="text-lg font-medium text-gray-900 mb-1">{title}</h3>}
      {description && <p className="text-sm text-gray-500 text-center max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
