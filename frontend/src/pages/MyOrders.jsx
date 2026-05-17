import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Spinner from '../components/Spinner';
import EmptyState from '../components/EmptyState';
import { ordersAPI } from '../api';
import { useToast } from '../hooks/useToast';
import { Package, ChevronRight } from 'lucide-react';

const STATUS_COLORS = {
  pending: 'bg-amber-100 text-amber-800',
  confirmed: 'bg-blue-100 text-blue-800',
  processing: 'bg-indigo-100 text-indigo-800',
  shipped: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const LISTING_TYPE_COLORS = {
  laptop: 'bg-cyan-100 text-cyan-800',
  part: 'bg-orange-100 text-orange-800',
  service: 'bg-indigo-100 text-indigo-800',
};

export default function MyOrders() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
      return;
    }
    if (isAuthenticated) {
      fetchOrders();
    }
  }, [isAuthenticated, authLoading, navigate]);

  async function fetchOrders() {
    setLoading(true);
    setError(null);
    try {
      const res = await ordersAPI.getMyOrders();
      setOrders(res.data || []);
    } catch (err) {
      console.error('Failed to fetch orders:', err);
      setError('Failed to load your orders. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  }

  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center"><Spinner size="lg" /></main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-4 py-8 w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">My Orders</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">{error}</div>
        )}

        {loading ? (
          <div className="flex justify-center py-16"><Spinner size="lg" /></div>
        ) : orders.length === 0 ? (
          <EmptyState
            icon="package"
            title="No orders yet"
            description="Place an order from a listing to see it here."
            action={
              <Link
                to="/"
                className="inline-flex items-center gap-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Browse Listings
              </Link>
            }
          />
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div
                key={order.id}
                className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {order.listing_title || 'Unknown Listing'}
                      </h3>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${LISTING_TYPE_COLORS[order.listing_type] || 'bg-gray-100 text-gray-800'}`}>
                        {order.listing_type}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-600 mb-3 flex-wrap">
                      <span className="font-semibold text-green-600">{formatPrice(order.listing_price)}</span>
                      <span className="text-gray-400">|</span>
                      <span>{formatDate(order.created_at)}</span>
                    </div>

                    {order.notes && (
                      <p className="text-sm text-gray-500 bg-gray-50 rounded-lg px-3 py-2 inline-block">
                        {order.notes}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full capitalize ${STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-800'}`}>
                      {order.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
