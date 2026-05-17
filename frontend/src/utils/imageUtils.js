/**
 * Convert relative image URL to full backend URL
 * @param {string} imageUrl - Image URL from API (e.g., "/uploads/abc123.jpg")
 * @returns {string} - Full URL (e.g., "http://127.0.0.1:8001/uploads/abc123.jpg")
 */
export function getImageUrl(imageUrl) {
  if (!imageUrl) return null;
  
  // If already a full URL, return as-is
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  
  // Prepend backend base URL
  const backendUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';
  return `${backendUrl}${imageUrl}`;
}
