import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Wrench } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Card from '../components/Card';
import Spinner from '../components/Spinner';
import EmptyState from '../components/EmptyState';
import Input from '../components/Input';
import Button from '../components/Button';
import { servicesAPI } from '../api';
import { getImageUrl } from '../utils/imageUtils';

const SERVICE_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'screen_repair', label: 'Screen Repair' },
  { value: 'keyboard_repair', label: 'Keyboard Repair' },
  { value: 'battery_replacement', label: 'Battery Replacement' },
  { value: 'software_install', label: 'Software Installation' },
  { value: 'cleaning', label: 'Cleaning' },
  { value: 'diagnostic', label: 'Diagnostic' },
  { value: 'upgrade', label: 'Upgrade' },
  { value: 'other', label: 'Other' },
];

export default function Services() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 12;

  const search = searchParams.get('search') || '';
  const serviceType = searchParams.get('service_type') || '';
  const minPrice = searchParams.get('min_price') || '';
  const maxPrice = searchParams.get('max_price') || '';

  useEffect(() => {
    fetchServices(true);
  }, [searchParams.toString()]);

  async function fetchServices(reset = false) {
    setLoading(true);
    setError(null);
    try {
      const params = {
        skip: reset ? 0 : skip,
        limit,
        search: search || undefined,
        service_type: serviceType || undefined,
        min_price: minPrice ? parseFloat(minPrice) : undefined,
        max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      };
      const res = await servicesAPI.list(params);
      const data = res.data?.data || [];
      if (reset) {
        setServices(data);
        setSkip(limit);
      } else {
        setServices((prev) => [...prev, ...data]);
        setSkip((prev) => prev + limit);
      }
      setHasMore(data.length === limit);
    } catch (err) {
      setError('Failed to load services');
      console.error('Failed to fetch services:', err);
    }
    setLoading(false);
  }

  function updateFilter(key, value) {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.delete('skip');
    setSearchParams(params);
  }

  function clearFilters() {
    setSearchParams(new URLSearchParams());
  }

  const formatPrice = (amount) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center gap-3 mb-6">
          <Wrench className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Repair Services</h1>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <Input
                placeholder="Search services..."
                value={search}
                onChange={(e) => updateFilter('search', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
              <select
                value={serviceType}
                onChange={(e) => updateFilter('service_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {SERVICE_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Price</label>
              <Input
                type="number"
                placeholder="Min $"
                value={minPrice}
                onChange={(e) => updateFilter('min_price', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Price</label>
              <Input
                type="number"
                placeholder="Max $"
                value={maxPrice}
                onChange={(e) => updateFilter('max_price', e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button variant="secondary" onClick={clearFilters} className="w-full">
                Clear Filters
              </Button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && services.length === 0 && (
          <div className="flex justify-center py-20">
            <Spinner size="lg" />
          </div>
        )}

        {/* Services Grid */}
        {!loading && services.length === 0 && !error && (
          <EmptyState
            title="No services found"
            description={search || serviceType ? 'Try adjusting your filters' : 'No services available yet'}
          />
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service) => (
            <div
              key={service.id}
              className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => navigate(`/services/${service.id}`)}
            >
              <div className="p-6">
                <div className="flex items-center gap-2 mb-3">
                  <Wrench className="w-5 h-5 text-blue-600" />
                  <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                    {SERVICE_TYPES.find(t => t.value === service.service_type)?.label || service.service_type}
                  </span>
                </div>
                <h3 className="font-medium text-gray-900 text-lg mb-2">{service.title}</h3>
                <p className="text-sm text-gray-500 mb-4 line-clamp-2">{service.description}</p>
                {service.brand && (
                  <p className="text-sm text-gray-600 mb-1">Brand: {service.brand}</p>
                )}
                {service.turnaround_time && (
                  <p className="text-sm text-gray-600 mb-3">Turnaround: {service.turnaround_time}</p>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-xl font-bold text-gray-900">{formatPrice(service.price)}</span>
                  {service.warranty_days && (
                    <span className="text-xs text-gray-500">{service.warranty_days} day warranty</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Load More */}
        {hasMore && services.length > 0 && (
          <div className="flex justify-center mt-8">
            <Button
              variant="secondary"
              onClick={() => fetchServices(false)}
              loading={loading}
            >
              Load More
            </Button>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
