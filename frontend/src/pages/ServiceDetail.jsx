import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Wrench, Clock, Shield, MessageSquare } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Button from '../components/Button';
import Spinner from '../components/Spinner';
import { servicesAPI, ordersAPI } from '../api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/useToast';

const SERVICE_TYPES = {
  screen_repair: 'Screen Repair',
  keyboard_repair: 'Keyboard Repair',
  battery_replacement: 'Battery Replacement',
  software_install: 'Software Installation',
  cleaning: 'Cleaning',
  diagnostic: 'Diagnostic',
  upgrade: 'Upgrade',
  other: 'Other',
};

export default function ServiceDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin, isAuthenticated } = useAuth();
  const { showSuccess, showError } = useToast();
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchService();
  }, [id]);

  async function fetchService() {
    setLoading(true);
    setError(null);
    try {
      const res = await servicesAPI.get(id);
      setService(res.data?.data || res.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Service not found');
      } else {
        setError('Failed to load service');
      }
      console.error('Failed to fetch service:', err);
    }
    setLoading(false);
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to delete this service?')) return;
    try {
      await servicesAPI.delete(id);
      navigate('/services');
    } catch (err) {
      alert('Failed to delete service');
    }
  }

  async function handlePlaceOrder() {
    try {
      await ordersAPI.createOrder({ listing_id: id, listing_type: 'service' });
      showSuccess('Order placed successfully!');
      navigate('/orders');
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to place order. Please try again.');
    }
  }

  const formatPrice = (amount) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
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
        <main className="flex-1 max-w-4xl mx-auto px-4 py-8">
          <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-gray-600 hover:text-gray-900 mb-6">
            <ArrowLeft className="w-4 h-4" /> Back
          </button>
          <div className="text-center py-20">
            <p className="text-xl font-medium text-gray-900 mb-4">{error}</p>
            <Button onClick={() => navigate('/services')}>Browse Services</Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="bg-white rounded-xl border border-gray-200 p-8">
          {/* Service Type Badge */}
          <div className="flex items-center gap-2 mb-4">
            <Wrench className="w-6 h-6 text-blue-600" />
            <span className="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
              {SERVICE_TYPES[service.service_type] || service.service_type}
            </span>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-4">{service.title}</h1>

          <div className="text-3xl font-bold text-green-600 mb-6">
            {formatPrice(service.price)}
          </div>

          <p className="text-gray-700 whitespace-pre-wrap mb-8">{service.description}</p>

          {/* Info Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
            {service.brand && (
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-500 mb-1">Brand</p>
                <p className="font-medium text-gray-900">{service.brand}</p>
              </div>
            )}
            {service.turnaround_time && (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <p className="text-sm text-gray-500">Turnaround</p>
                </div>
                <p className="font-medium text-gray-900">{service.turnaround_time}</p>
              </div>
            )}
            {service.warranty_days && (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Shield className="w-4 h-4 text-gray-400" />
                  <p className="text-sm text-gray-500">Warranty</p>
                </div>
                <p className="font-medium text-gray-900">{service.warranty_days} days</p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
            <Button variant="primary" onClick={() => navigate(`/messages?listing=${id}&type=service`)}>
              <MessageSquare className="w-4 h-4 mr-1" /> Contact Us
            </Button>
            {isAuthenticated && (
              <Button variant="primary" onClick={handlePlaceOrder}>
                Place Order
              </Button>
            )}
            {isAdmin && (
              <>
                <Button variant="secondary" onClick={() => navigate(`/edit/services/${id}`)}>Edit</Button>
                <Button variant="danger" onClick={handleDelete}>Delete</Button>
              </>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
