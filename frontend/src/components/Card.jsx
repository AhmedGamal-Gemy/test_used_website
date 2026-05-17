import { useState } from 'react';
import { Heart } from 'lucide-react';
import Badge from './Badge';
import { getImageUrl } from '../utils/imageUtils';

export default function Card({ image, title, price, condition, isFavorited = false, onToggleFavorite, onClick, className = '' }) {
  const [favorited, setFavorited] = useState(isFavorited);

  const handleFavorite = (e) => {
    e.stopPropagation();
    setFavorited(!favorited);
    onToggleFavorite?.();
  };

  const formatPrice = (amount) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  return (
    <div
      className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer ${className}`}
      onClick={onClick}
    >
      <div className="relative aspect-[4/3] bg-gray-100">
        {getImageUrl(image) ? (
          <img src={getImageUrl(image)} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
        <button
          onClick={handleFavorite}
          className="absolute top-2 right-2 p-1.5 bg-white/80 backdrop-blur-sm rounded-full hover:bg-white transition-colors"
        >
          <Heart className={`w-5 h-5 ${favorited ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} />
        </button>
      </div>
      <div className="p-4">
        <h3 className="font-medium text-gray-900 truncate">{title}</h3>
        <div className="flex items-center justify-between mt-2">
          <span className="text-lg font-bold text-gray-900">{formatPrice(price)}</span>
          <Badge condition={condition} />
        </div>
      </div>
    </div>
  );
}
