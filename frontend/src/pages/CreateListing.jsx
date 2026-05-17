import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { laptopsAPI, partsAPI, servicesAPI } from '../api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Input from '../components/Input';
import Button from '../components/Button';
import ImageUpload from '../components/ImageUpload';
import { Laptop, Wrench } from 'lucide-react';

export default function CreateListing() {
  const { isAuthenticated, isAdmin, isLoading } = useAuth();
  const navigate = useNavigate();

  // Redirect non-admin users
  useEffect(() => {
    if (!isLoading && !isAdmin) {
      navigate('/');
    }
  }, [isAdmin, isLoading, navigate]);

  if (isLoading || !isAdmin) {
    return null;
  }

  const [listingType, setListingType] = useState('laptop');
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
    estimated_duration: '',
    warranty_days: '',
    service_type: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

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
    if (listingType !== 'service' && !formData.condition) newErrors.condition = 'Condition is required';
    if (!formData.brand) newErrors.brand = 'Brand is required';

    if (listingType === 'laptop') {
      if (!formData.model.trim()) newErrors.model = 'Model is required';
      if (!formData.ram) newErrors.ram = 'RAM is required';
      if (!formData.storage) newErrors.storage = 'Storage is required';
      if (!formData.processor.trim()) newErrors.processor = 'Processor is required';
    } else if (listingType === 'part') {
      if (!formData.part_type) newErrors.part_type = 'Part type is required';
    } else if (listingType === 'service') {
      if (!formData.service_type) newErrors.service_type = 'Service type is required';
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
      if (listingType === 'service') {
        const data = {
          title: formData.title,
          description: formData.description,
          price: parseFloat(formData.price),
          service_type: formData.service_type,
          brand: formData.brand || undefined,
          estimated_duration: formData.estimated_duration || undefined,
          warranty_days: formData.warranty_days ? parseInt(formData.warranty_days) : undefined,
        };
        const res = await servicesAPI.create(data);
        navigate(`/services/${res.data.data.id}`);
        return;
      }

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
      } else {
        data.compatible_models = formData.compatible_models
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean);
        data.part_type = formData.part_type;
      }

      const api = listingType === 'laptop' ? laptopsAPI : partsAPI;
      const { data: created } = await api.create(data);
      const listingId = created.id || created._id;

      if (selectedFiles.length > 0) {
        const imgFormData = new FormData();
        selectedFiles.forEach((file) => {
          imgFormData.append('file', file);
        });
        await api.uploadImage(listingId, imgFormData);
      }

      navigate(`/${listingType === 'laptop' ? 'laptops' : 'parts'}/${listingId}`);
    } catch (error) {
      setErrors({
        submit: error.response?.data?.detail || 'Failed to create listing. Please try again.',
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

  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-3xl mx-auto px-4 py-8 w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Create New Listing</h1>

        <div className="flex gap-4 mb-8">
          <button
            type="button"
            onClick={() => setListingType('laptop')}
            className={`flex-1 py-3 px-4 rounded-lg border-2 transition-colors flex items-center justify-center gap-2 font-medium ${
              listingType === 'laptop'
                ? 'border-blue-600 bg-blue-50 text-blue-600'
                : 'border-gray-300 text-gray-600 hover:border-gray-400'
            }`}
          >
            <Laptop className="w-5 h-5" />
            Laptop
          </button>
          <button
            type="button"
            onClick={() => setListingType('part')}
            className={`flex-1 py-3 px-4 rounded-lg border-2 transition-colors flex items-center justify-center gap-2 font-medium ${
              listingType === 'part'
                ? 'border-blue-600 bg-blue-50 text-blue-600'
                : 'border-gray-300 text-gray-600 hover:border-gray-400'
            }`}
          >
            <Wrench className="w-5 h-5" />
            Part
          </button>
          <button
            type="button"
            onClick={() => setListingType('service')}
            className={`flex-1 py-3 px-4 rounded-lg border-2 transition-colors flex items-center justify-center gap-2 font-medium ${
              listingType === 'service'
                ? 'border-blue-600 bg-blue-50 text-blue-600'
                : 'border-gray-300 text-gray-600 hover:border-gray-400'
            }`}
          >
            <Wrench className="w-5 h-5" />
            Service
          </button>
        </div>

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
                  {['repair', 'maintenance', 'diagnostics', 'data_recovery', 'cleaning', 'other'].map((t) => (
                    <option key={t} value={t}>
                      {t.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                    </option>
                  ))}
                </select>
                {errors.service_type && <span className="text-sm text-red-600">{errors.service_type}</span>}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Estimated Duration"
                  name="estimated_duration"
                  value={formData.estimated_duration}
                  onChange={handleChange}
                  placeholder="e.g., 2-3 business days"
                />

                <Input
                  label="Warranty (days)"
                  name="warranty_days"
                  type="number"
                  value={formData.warranty_days}
                  onChange={handleChange}
                  placeholder="e.g., 90"
                  min="0"
                />
              </div>
            </div>
          )}

          <div className="space-y-4 pt-4 border-t border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Images</h2>
            <ImageUpload onUpload={handleImageUpload} maxFiles={5} />
          </div>

          {errors.submit && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {errors.submit}
            </div>
          )}

          <Button type="submit" variant="primary" size="lg" loading={loading} className="w-full">
            Create Listing
          </Button>
        </form>
      </main>
      <Footer />
    </div>
  );
}
