import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Spinner from '../components/Spinner';
import EmptyState from '../components/EmptyState';
import Button from '../components/Button';
import Input from '../components/Input';
import { ordersAPI } from '../api';
import { useToast } from '../hooks/useToast';
import { ShoppingBag } from 'lucide-react';

const STATUS_OPTIONS = ['pending', 'confirmed', 'processing', 'shipped', 'completed', 'cancelled'];

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

export default function AdminOrders() {
  const { isAdmin, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);

  // Editable state per order: { [orderId]: { status, admin_notes } }
  const [edits, setEdits] = useState({});

  useEffect(() => {
    if (!authLoading && !isAdmin) {
      navigate('/');
      return;
    }
    if (isAdmin) {
      fetchOrders();
    }
  }, [isAdmin, authLoading, navigate]);

  useEffect(() => {
    if (orders.length > 0) {
      const initial = {};
      orders.forEach((o) => {
        initial[o.id] = {
          status: o.status || 'pending',
          admin_notes: o.admin_notes || '',
        };
      });
      setEdits(initial);
    }
  }, [orders]);

  async function fetchOrders() {
    setLoading(true);
    setError(null);
    try {
      const res = await ordersAPI.getAllOrders();
      setOrders(res.data || []);
    } catch (err) {
      console.error('Failed to fetch orders:', err);
      setError('Failed to load orders. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleUpdate(orderId) {
    const edit = edits[orderId];
    if (!edit) return;
    setUpdatingId(orderId);
    try {
      await ordersAPI.updateOrderStatus(orderId, {
        status: edit.status,
        admin_notes: edit.admin_notes,
      });
      showSuccess('Order status updated!');
      await fetchOrders();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to update order.');
    } finally {
      setUpdatingId(null);
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
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function handleEditChange(orderId, field, value) {
    setEdits((prev) => ({
      ...prev,
      [orderId]: { ...prev[orderId], [field]: value },
    }));
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

  if (!isAdmin) return null;

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center gap-3 mb-8">
          <ShoppingBag className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Order Management</h1>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">{error}</div>
        )}

        {loading ? (
          <div className="flex justify-center py-16"><Spinner size="lg" /></div>
        ) : orders.length === 0 ? (
          <EmptyState icon="package" title="No orders yet" description="Customer orders will appear here once placed." />
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50">
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Customer</th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Listing</th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Price</th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Date</th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Notes</th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Admin Notes</th>
                    <th className="text-right p-3 text-sm font-medium text-gray-500">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => {
                    const edit = edits[order.id] || { status: order.status, admin_notes: order.admin_notes || '' };
                    return (
                      <tr key={order.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="p-3 text-sm text-gray-900">{order.user_email || 'Unknown'}</td>
                        <td className="p-3">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-gray-900 truncate max-w-[160px]">
                              {order.listing_title || 'Unknown'}
                            </span>
                            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${LISTING_TYPE_COLORS[order.listing_type] || 'bg-gray-100 text-gray-800'}`}>
                              {order.listing_type}
                            </span>
                          </div>
                        </td>
                        <td className="p-3 text-sm font-semibold text-green-600">{formatPrice(order.listing_price)}</td>
                        <td className="p-3">
                          <span className={`text-xs font-semibold px-2 py-1 rounded-full capitalize ${STATUS_COLORS[edit.status] || 'bg-gray-100 text-gray-800'}`}>
                            {edit.status}
                          </span>
                        </td>
                        <td className="p-3 text-sm text-gray-500 whitespace-nowrap">{formatDate(order.created_at)}</td>
                        <td className="p-3 text-sm text-gray-500 max-w-[140px] truncate">
                          {order.notes || <span className="text-gray-300 italic">—</span>}
                        </td>
                        <td className="p-3">
                          <input
                            type="text"
                            value={edit.admin_notes}
                            onChange={(e) => handleEditChange(order.id, 'admin_notes', e.target.value)}
                            placeholder="Add note..."
                            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </td>
                        <td className="p-3 text-right">
                          <div className="flex items-center gap-2 justify-end">
                            <select
                              value={edit.status}
                              onChange={(e) => handleEditChange(order.id, 'status', e.target.value)}
                              className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                            >
                              {STATUS_OPTIONS.map((s) => (
                                <option key={s} value={s}>
                                  {s.charAt(0).toUpperCase() + s.slice(1)}
                                </option>
                              ))}
                            </select>
                            <Button
                              size="sm"
                              variant="primary"
                              loading={updatingId === order.id}
                              disabled={updatingId === order.id}
                              onClick={() => handleUpdate(order.id)}
                            >
                              Update
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
