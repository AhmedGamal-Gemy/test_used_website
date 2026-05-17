import { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { laptopsAPI, partsAPI, servicesAPI } from '../api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Input from '../components/Input';
import Button from '../components/Button';
import Spinner from '../components/Spinner';
import ImageUpload from '../components/ImageUpload';
import { Laptop, Wrench } from 'lucide-react';

export default function EditListing() {
  const { type: typeFromParams, id } = useParams();
  const { isAuthenticated, isAdmin, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Support both /edit/services/:id and /edit/:type/:id routes
  const type = typeFromParams || location.pathname.split('/')[2];

  // Redirect non-admin users
  useEffect(() => {
    if (!isLoading && !isAdmin) {
      navigate('/');
    }
  }, [isAdmin, isLoading, navigate]);

  if (isLoading || !isAdmin) {
    return null;
  }

  const listingType = type === 'laptops' ? 'laptop' : type === 'services' ? 'service' : 'part';

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    condition: '',
    brand: '',
    category: '',
    model: '',
    ram: '',
    storage: '',
    processor: '',
    compatible_models: '',
    part_type: '',
    service_type: '',
    turnaround_time: '',
    warranty_days: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);

  const api = listingType === 'laptop' ? laptopsAPI : listingType === 'service' ? servicesAPI : partsAPI;

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchListing = async () => {
      try {
        const res = await api.get(id);
        // Services API wraps data in .data property, laptops/parts don't
        const data = res.data?.data || res.data;
        setFormData({
          title: data.title || '',
          description: data.description || '',
          price: data.price?.toString() || '',
          condition: data.condition || '',
          brand: data.brand || '',
          category: data.category || '',
          model: data.model || '',
          ram: data.ram || '',
          storage: data.storage || '',
          processor: data.processor || '',
          compatible_models: Array.isArray(data.compatible_models)
            ? data.compatible_models.join(', ')
            : data.compatible_models || '',
          part_type: data.part_type || '',
          service_type: data.service_type || '',
          turnaround_time: data.turnaround_time || '',
          warranty_days: data.warranty_days?.toString() || '',
        });
      } catch (error) {
        setFetchError(error.response?.data?.detail || 'Failed to load listing.');
      } finally {
        setFetchLoading(false);
      }
    };

    fetchListing();
  }, [id, isAuthenticated, navigate, api]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleImageUpload = (files) => {
    setSelectedFiles(files);
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) newErrors.title = 'Title is required';
    if (!formData.price) newErrors.price = 'Price is required';
    if (!formData.brand) newErrors.brand = 'Brand is required';

    if (listingType === 'laptop') {
      if (!formData.condition) newErrors.condition = 'Condition is required';
      if (!formData.model.trim()) newErrors.model = 'Model is required';
      if (!formData.ram) newErrors.ram = 'RAM is required';
      if (!formData.storage) newErrors.storage = 'Storage is required';
      if (!formData.processor.trim()) newErrors.processor = 'Processor is required';
    } else if (listingType === 'service') {
      if (!formData.service_type) newErrors.service_type = 'Service type is required';
    } else {
      if (!formData.condition) newErrors.condition = 'Condition is required';
      if (!formData.part_type) newErrors.part_type = 'Part type is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setErrors({});

    try {
      const data = {
        title: formData.title,
        description: formData.description,
        price: parseFloat(formData.price),
        condition: formData.condition,
        brand: formData.brand,
        category: formData.category,
      };

      if (listingType === 'laptop') {
        data.model = formData.model;
        data.ram = formData.ram;
        data.storage = formData.storage;
        data.processor = formData.processor;
      } else if (listingType === 'service') {
        data.service_type = formData.service_type;
        data.turnaround_time = formData.turnaround_time;
        data.warranty_days = formData.warranty_days ? parseInt(formData.warranty_days) : undefined;
      } else {
        data.compatible_models = formData.compatible_models
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean);
        data.part_type = formData.part_type;
      }

      await api.update(id, data);

      if (selectedFiles.length > 0) {
        const imgFormData = new FormData();
        selectedFiles.forEach((file) => {
          imgFormData.append('file', file);
        });
        await api.uploadImage(id, imgFormData);
      }

      navigate(`/${type}/${id}`);
    } catch (error) {
      setErrors({
        submit: error.response?.data?.detail || 'Failed to update listing. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  const conditions = ['New', 'Like New', 'Good', 'Fair'];
  const brands = ['Apple', 'Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Other'];
  const categories = ['Business', 'Gaming', 'Ultrabook', 'Budget'];
  const ramOptions = ['4GB', '8GB', '16GB', '32GB'];
  const storageOptions = ['128GB', '256GB', '512GB', '1TB'];
  const partTypes = ['Battery', 'Charger', 'Keyboard', 'Screen', 'Motherboard', 'RAM', 'Storage', 'Other'];

  if (fetchLoading) {
    return (
      <div className="min-h-screen flex flex-col overflow-x-hidden">
        <Navbar />
        <main className="flex-1 max-w-3xl mx-auto px-4 py-8 flex items-center justify-center">
          <Spinner size="lg" />
        </main>
        <Footer />
      </div>
    );
  }

  if (fetchError) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-3xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {fetchError}
          </div>
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="mt-4 text-sm text-blue-600 hover:underline"
          >
            Go Back
          </button>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-3xl mx-auto px-4 py-8 w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          {listingType === 'laptop' ? <Laptop className="w-6 h-6" /> : <Wrench className="w-6 h-6" />}
          Edit {listingType === 'laptop' ? 'Laptop' : listingType === 'service' ? 'Service' : 'Part'} Listing
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <Input
              label="Title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              error={errors.title}
              placeholder={`Enter ${listingType} title`}
              required
            />

            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Describe your item..."
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Price ($)"
                name="price"
                type="number"
                value={formData.price}
                onChange={handleChange}
                error={errors.price}
                placeholder="0.00"
                min="0"
                step="0.01"
                required
              />

              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Condition</label>
                <select
                  name="condition"
                  value={formData.condition}
                  onChange={handleChange}
                  className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.condition ? 'border-red-500' : 'border-gray-300'}`}
                >
                  <option value="">Select condition</option>
                  {conditions.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                {errors.condition && <span className="text-sm text-red-600">{errors.condition}</span>}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Brand</label>
                <select
                  name="brand"
                  value={formData.brand}
                  onChange={handleChange}
                  className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.brand ? 'border-red-500' : 'border-gray-300'}`}
                >
                  <option value="">Select brand</option>
                  {brands.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
                {errors.brand && <span className="text-sm text-red-600">{errors.brand}</span>}
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Category</label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select category</option>
                  {categories.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {listingType === 'service' && (
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Service Details</h2>

              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Service Type</label>
                <select
                  name="service_type"
                  value={formData.service_type}
                  onChange={handleChange}
                  className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.service_type ? 'border-red-500' : 'border-gray-300'}`}
                >
                  <option value="">Select service type</option>
                  <option value="screen_repair">Screen Repair</option>
                  <option value="keyboard_repair">Keyboard Repair</option>
                  <option value="battery_replacement">Battery Replacement</option>
                  <option value="software_install">Software Installation</option>
                  <option value="cleaning">Cleaning</option>
                  <option value="diagnostic">Diagnostic</option>
                  <option value="upgrade">Upgrade</option>
                  <option value="other">Other</option>
                </select>
                {errors.service_type && <span className="text-sm text-red-600">{errors.service_type}</span>}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Turnaround Time"
                  name="turnaround_time"
                  value={formData.turnaround_time}
                  onChange={handleChange}
                  placeholder="e.g., 2-3 business days"
                />
                <Input
                  label="Warranty (days)"
                  name="warranty_days"
                  type="number"
                  value={formData.warranty_days}
                  onChange={handleChange}
                  placeholder="e.g., 30"
                  min="0"
                />
              </div>
            </div>
          )}

          {listingType === 'laptop' && (
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Laptop Details</h2>

              <Input
                label="Model"
                name="model"
                value={formData.model}
                onChange={handleChange}
                error={errors.model}
                placeholder="e.g., MacBook Pro 16"
                required
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">RAM</label>
                  <select
                    name="ram"
                    value={formData.ram}
                    onChange={handleChange}
                    className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.ram ? 'border-red-500' : 'border-gray-300'}`}
                  >
                    <option value="">Select RAM</option>
                    {ramOptions.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                  {errors.ram && <span className="text-sm text-red-600">{errors.ram}</span>}
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">Storage</label>
                  <select
                    name="storage"
                    value={formData.storage}
                    onChange={handleChange}
                    className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.storage ? 'border-red-500' : 'border-gray-300'}`}
                  >
                    <option value="">Select storage</option>
                    {storageOptions.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                  {errors.storage && <span className="text-sm text-red-600">{errors.storage}</span>}
                </div>
              </div>

              <Input
                label="Processor"
                name="processor"
                value={formData.processor}
                onChange={handleChange}
                error={errors.processor}
                placeholder="e.g., Intel Core i7-12700H"
                required
              />
            </div>
          )}

          {listingType === 'part' && (
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Part Details</h2>

              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">
                  Compatible Models
                  <span className="text-gray-500 font-normal ml-1">(comma-separated)</span>
                </label>
                <input
                  type="text"
                  name="compatible_models"
                  value={formData.compatible_models}
                  onChange={handleChange}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., MacBook Pro 16, Dell XPS 15, ThinkPad X1"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Part Type</label>
                <select
                  name="part_type"
                  value={formData.part_type}
                  onChange={handleChange}
                  className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.part_type ? 'border-red-500' : 'border-gray-300'}`}
                >
                  <option value="">Select part type</option>
                  {partTypes.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
                {errors.part_type && <span className="text-sm text-red-600">{errors.part_type}</span>}
              </div>
            </div>
          )}

          {listingType !== 'service' && (
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Update Images</h2>
              <p className="text-sm text-gray-500">Upload new images to replace existing ones.</p>
              <ImageUpload onUpload={handleImageUpload} maxFiles={5} />
            </div>
          )}

          {errors.submit && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {errors.submit}
            </div>
          )}

          <div className="flex gap-4">
            <Button type="submit" variant="primary" size="lg" loading={loading} className="flex-1">
              Save Changes
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="lg"
              onClick={() => navigate(-1)}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </form>
      </main>
      <Footer />
    </div>
  );
}
