const colors = {
  'New': 'bg-green-100 text-green-800',
  'Like New': 'bg-blue-100 text-blue-800',
  'Good': 'bg-yellow-100 text-yellow-800',
  'Fair': 'bg-red-100 text-red-800',
};

export default function Badge({ condition }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[condition] || 'bg-gray-100 text-gray-800'}`}>
      {condition}
    </span>
  );
}
