import { useState } from 'react';
import { Star } from 'lucide-react';

export default function StarRating({ rating = 0, onRate, readonly = false, size = 'md', className = '' }) {
  const [hoverRating, setHoverRating] = useState(0);

  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const iconSize = sizes[size] || sizes.md;

  const handleClick = (value) => {
    if (!readonly && onRate) {
      onRate(value);
    }
  };

  const handleMouseEnter = (value) => {
    if (!readonly) {
      setHoverRating(value);
    }
  };

  const handleMouseLeave = () => {
    if (!readonly) {
      setHoverRating(0);
    }
  };

  return (
    <div className={`flex items-center gap-0.5 ${className}`}>
      {[1, 2, 3, 4, 5].map((star) => {
        const displayRating = hoverRating || rating;
        const isFilled = star <= displayRating;

        return (
          <button
            key={star}
            type="button"
            onClick={() => handleClick(star)}
            onMouseEnter={() => handleMouseEnter(star)}
            onMouseLeave={handleMouseLeave}
            className={`${readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110'} transition-transform focus:outline-none`}
            disabled={readonly}
          >
            {isFilled ? (
              <Star className={`${iconSize} text-yellow-400 fill-yellow-400`} />
            ) : (
              <Star className={`${iconSize} text-gray-300`} />
            )}
          </button>
        );
      })}
    </div>
  );
}
