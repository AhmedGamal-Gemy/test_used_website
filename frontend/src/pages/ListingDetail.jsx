import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, MessageSquare, Heart, Phone, MapPin, User, Laptop, Wrench, Pencil, Trash2 } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Badge from '../components/Badge';
import Button from '../components/Button';
import Spinner from '../components/Spinner';
import StarRating from '../components/StarRating';
import { laptopsAPI, partsAPI, reviewsAPI, favoritesAPI, ordersAPI } from '../api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/useToast';
import { getImageUrl } from '../utils/imageUtils';

export default function ListingDetail() {
  const { type, id } = useParams(); // type = 'laptops' or 'parts'
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [sellerRating, setSellerRating] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const navigate = useNavigate();
  const { user, isAuthenticated, isAdmin } = useAuth();
  const { showSuccess, showError } = useToast();

  const isLaptop = type === 'laptops';
  const isOwnListing = user && listing && user._id === listing.seller_id;

  useEffect(() => {
    async function fetchListing() {
      setLoading(true);
      setError(null);
      try {
        const api = isLaptop ? laptopsAPI : partsAPI;
        const res = await api.get(id);
        setListing(res.data);

        // Fetch seller reviews
        if (res.data?.seller_id) {
          const reviewsRes = await reviewsAPI.getSellerReviews(res.data.seller_id);
          const reviewsData = reviewsRes.data || {};
          setReviews(reviewsData.reviews || []);
          setSellerRating({
            average: reviewsData.average_rating || 0,
            total: reviewsData.total_reviews || 0,
          });
        }
      } catch (err) {
        if (err.response?.status === 404) {
          setError('Listing not found');
        } else {
          setError('Failed to load listing');
        }
      } finally {
        setLoading(false);
      }
    }
    fetchListing();
  }, [type, id, isLaptop]);

  const handleFavorite = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    try {
      if (isFavorite) {
        if (isLaptop) {
          await favoritesAPI.removeLaptop(id);
        } else {
          await favoritesAPI.removePart(id);
        }
        showSuccess('Removed from favorites');
      } else {
        if (isLaptop) {
          await favoritesAPI.addLaptop(id);
        } else {
          await favoritesAPI.addPart(id);
        }
        showSuccess('Added to favorites');
      }
      setIsFavorite(!isFavorite);
    } catch (err) {
      console.error('Failed to update favorite:', err);
      showError('Failed to update favorites. Please try again.');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this listing?')) return;
    try {
      const api = isLaptop ? laptopsAPI : partsAPI;
      await api.delete(id);
      showSuccess('Listing deleted successfully');
      navigate(`/${type}`);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to delete listing');
    }
  };

  const handlePlaceOrder = async () => {
    try {
      const listingType = isLaptop ? 'laptop' : 'part';
      await ordersAPI.createOrder({ listing_id: id, listing_type: listingType });
      showSuccess('Order placed successfully!');
      navigate('/orders');
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to place order. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <Spinner size="lg" />
        </main>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">{error}</h2>
            <Button onClick={() => navigate(-1)}>Go Back</Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const mainImage = getImageUrl(listing.image_url);

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        {/* Two-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Left Column - Image Gallery */}
          <div>
            <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
              {mainImage ? (
                <img
                  src={mainImage}
                  alt={listing.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-200">
                  {isLaptop ? (
                    <Laptop className="w-24 h-24 text-gray-400" />
                  ) : (
                    <Wrench className="w-24 h-24 text-gray-400" />
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Details */}
          <div>
            <div className="flex items-start justify-between mb-4">
              <h1 className="text-3xl font-bold text-gray-900">{listing.title}</h1>
              <Badge condition={listing.condition} />
            </div>

            <p className="text-2xl text-green-600 font-bold mb-6">
              {formatPrice(listing.price)}
            </p>

            <div className="space-y-4 mb-6">
              <div className="flex items-center gap-2 text-gray-600">
                <span className="font-medium">Brand:</span>
                <span>{listing.brand}</span>
              </div>

              <div className="flex items-center gap-2 text-gray-600">
                <span className="font-medium">Category:</span>
                <span>{listing.category}</span>
              </div>

              {/* Laptop-specific fields */}
              {isLaptop && (
                <>
                  {listing.model && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <span className="font-medium">Model:</span>
                      <span>{listing.model}</span>
                    </div>
                  )}
                  {listing.ram && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <span className="font-medium">RAM:</span>
                      <span>{listing.ram}</span>
                    </div>
                  )}
                  {listing.storage && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <span className="font-medium">Storage:</span>
                      <span>{listing.storage}</span>
                    </div>
                  )}
                  {listing.processor && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <span className="font-medium">Processor:</span>
                      <span>{listing.processor}</span>
                    </div>
                  )}
                </>
              )}

              {/* Part-specific fields */}
              {!isLaptop && (
                <>
                  {listing.compatible_models && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <span className="font-medium">Compatible Models:</span>
                      <span>{listing.compatible_models}</span>
                    </div>
                  )}
                  {listing.part_type && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <span className="font-medium">Part Type:</span>
                      <span>{listing.part_type}</span>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Description */}
            {listing.description && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Description</h3>
                <p className="text-gray-600 whitespace-pre-wrap">{listing.description}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              {!isOwnListing && isAuthenticated && (
                <Button
                  variant="primary"
                  onClick={() => navigate(`/messages?listing=${id}&type=${type}`)}
                >
                  <MessageSquare className="w-4 h-4" />
                  Contact Us
                </Button>
              )}
              {!isOwnListing && isAuthenticated && (
                <Button
                  variant="primary"
                  onClick={handlePlaceOrder}
                >
                  Place Order
                </Button>
              )}
              <Button
                variant="secondary"
                onClick={handleFavorite}
                className="flex items-center gap-2"
              >
                <Heart className={`w-4 h-4 ${isFavorite ? 'fill-red-500 text-red-500' : ''}`} />
                {isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
              </Button>
            </div>
            </div>

            {/* Admin Actions */}
            {isAdmin && (
              <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200">
                <Link
                  to={`/edit/${type}/${id}`}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <Pencil className="w-4 h-4" />
                  Edit
                </Link>
                <button
                  onClick={handleDelete}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 border border-red-300 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            )}
          </div>

        {/* Seller Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-12">
          <h2 className="text-xl font-bold mb-4">Seller Information</h2>
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-gray-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-semibold text-lg">{listing.seller_name || 'Seller'}</h3>
                {sellerRating && sellerRating.total > 0 && (
                  <div className="flex items-center gap-1">
                    <StarRating rating={sellerRating.average} readonly size="sm" />
                    <span className="text-sm text-gray-600">
                      ({sellerRating.total} reviews)
                    </span>
                  </div>
                )}
              </div>

              {listing.seller_phone && (
                <div className="flex items-center gap-2 text-gray-600 mb-1">
                  <Phone className="w-4 h-4" />
                  <span>{listing.seller_phone}</span>
                </div>
              )}

              {listing.seller_location && (
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin className="w-4 h-4" />
                  <span>{listing.seller_location}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Reviews Section */}
        {reviews.length > 0 && (
          <div className="mb-12">
            <h2 className="text-xl font-bold mb-6">Seller Reviews</h2>
            <div className="space-y-4">
              {reviews.map((review, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <StarRating rating={review.rating} readonly size="sm" />
                    <span className="text-sm text-gray-600">
                      by {review.reviewer_name || 'Anonymous'}
                    </span>
                  </div>
                  {review.comment && (
                    <p className="text-gray-600">{review.comment}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
