import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import StarRating from '../components/StarRating';
import Button from '../components/Button';
import Spinner from '../components/Spinner';
import EmptyState from '../components/EmptyState';
import { reviewsAPI } from '../api';
import { User, MapPin, Phone, Calendar } from 'lucide-react';

export default function SellerProfile() {
  const { sellerId } = useParams();
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  const navigate = useNavigate();

  const [sellerData, setSellerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [reviewError, setReviewError] = useState(null);
  const [reviewSuccess, setReviewSuccess] = useState(null);

  // Review form state
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');

  // Check if current user has already reviewed this seller
  const hasReviewed = sellerData?.reviews?.some(
    (review) => review.reviewer_id === user?._id
  );
  const isOwnProfile = user?._id === sellerId;

  useEffect(() => {
    if (sellerId) {
      fetchSellerReviews();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sellerId]);

  async function fetchSellerReviews() {
    setLoading(true);
    setError(null);
    try {
      const { data } = await reviewsAPI.getSellerReviews(sellerId);
      setSellerData(data);
    } catch (err) {
      console.error('Failed to fetch seller reviews:', err);
      setError('Failed to load seller profile. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitReview(e) {
    e.preventDefault();
    if (rating === 0 || !comment.trim()) return;

    setSubmitting(true);
    setReviewError(null);
    setReviewSuccess(null);

    try {
      await reviewsAPI.createReview(sellerId, {
        rating,
        comment: comment.trim(),
      });
      setReviewSuccess('Review submitted successfully!');
      setRating(0);
      setComment('');
      // Refresh reviews to show the new review
      await fetchSellerReviews();
    } catch (err) {
      console.error('Failed to submit review:', err);
      const detail = err.response?.data?.detail || 'Failed to submit review. Please try again.';
      setReviewError(detail);
    } finally {
      setSubmitting(false);
    }
  }

  function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  // Get seller name from reviews data (first review's reviewer info or fallback)
  // The API might return seller info in the response
  const sellerName = sellerData?.seller_name || sellerData?.reviews?.[0]?.seller_name || 'Seller';

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-4xl mx-auto px-4 py-8 flex items-center justify-center">
          <Spinner size="lg" />
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-4 py-8">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-gray-600 hover:text-gray-900 transition-colors mb-6 inline-flex items-center gap-1"
        >
          ← Back
        </button>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm p-4 mb-6">
            {error}
          </div>
        )}

        {/* Seller Info Card */}
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 mb-8">
          <div className="flex items-start gap-4">
            {/* Avatar */}
            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
              <User className="w-8 h-8 text-blue-600" />
            </div>

            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">{sellerName}</h1>

              {/* Rating Summary */}
              {sellerData && (
                <div className="flex items-center gap-3 mt-2">
                  <StarRating
                    rating={sellerData.average_rating || 0}
                    readonly
                    size="md"
                  />
                  <span className="text-sm text-gray-600">
                    {sellerData.average_rating
                      ? `${sellerData.average_rating.toFixed(1)} (${sellerData.total_reviews || 0} review${sellerData.total_reviews !== 1 ? 's' : ''})`
                      : 'No ratings yet'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Write a Review Section */}
        {isAuthenticated && !isOwnProfile && !hasReviewed && (
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Write a Review</h2>

            {reviewError && (
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm p-4 mb-4">
                {reviewError}
              </div>
            )}

            {reviewSuccess && (
              <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm p-4 mb-4">
                {reviewSuccess}
              </div>
            )}

            <form onSubmit={handleSubmitReview} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rating
                </label>
                <StarRating
                  rating={rating}
                  onRate={setRating}
                  size="lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Comment
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Share your experience with this seller..."
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <Button
                type="submit"
                variant="primary"
                loading={submitting}
                disabled={rating === 0 || !comment.trim()}
              >
                Submit Review
              </Button>
            </form>
          </div>
        )}

        {/* Messages for review restrictions */}
        {isAuthenticated && isOwnProfile && (
          <div className="bg-blue-50 border border-blue-200 text-blue-700 rounded-lg text-sm p-4 mb-8">
            You cannot review your own profile.
          </div>
        )}

        {isAuthenticated && !isOwnProfile && hasReviewed && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 rounded-lg text-sm p-4 mb-8">
            You have already reviewed this seller.
          </div>
        )}

        {!isAuthenticated && (
          <div className="bg-gray-50 border border-gray-200 text-gray-700 rounded-lg text-sm p-4 mb-8">
            <button
              onClick={() => navigate('/login')}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Log in
            </button>{' '}
            to write a review.
          </div>
        )}

        {/* Reviews List */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Reviews ({sellerData?.total_reviews || 0})
          </h2>

          {!sellerData?.reviews || sellerData.reviews.length === 0 ? (
            <EmptyState
              icon="inbox"
              title="No reviews yet"
              description="This seller hasn't received any reviews yet."
            />
          ) : (
            <div className="space-y-4">
              {sellerData.reviews.map((review) => (
                <div
                  key={review._id}
                  className="bg-white border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                        <User className="w-4 h-4 text-gray-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {review.reviewer_name || 'Anonymous'}
                        </p>
                        <div className="flex items-center gap-2">
                          <StarRating
                            rating={review.rating}
                            readonly
                            size="sm"
                          />
                        </div>
                      </div>
                    </div>
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(review.created_at)}
                    </span>
                  </div>
                  {review.comment && (
                    <p className="text-sm text-gray-600 mt-2 whitespace-pre-wrap">
                      {review.comment}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
