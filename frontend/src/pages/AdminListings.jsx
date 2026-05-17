import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Laptop, Wrench, Cpu, Trash2, Search, AlertTriangle } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Spinner from '../components/Spinner';
import { adminAPI, laptopsAPI, partsAPI, servicesAPI } from '../api';
import { useAuth } from '../contexts/AuthContext';

const TABS = [
  { key: 'laptops', label: 'Laptops', icon: Laptop },
  { key: 'parts', label: 'Parts', icon: Cpu },
  { key: 'services', label: 'Services', icon: Wrench },
];

export default function AdminListings() {
  const { isAdmin, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('laptops');
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(new Set());
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAdmin) {
      navigate('/');
    }
  }, [authLoading, isAdmin, navigate]);

  const fetchListings = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSelected(new Set());
    try {
      let res, items;
      switch (activeTab) {
        case 'laptops':
          res = await laptopsAPI.list({ limit: 100 });
          items = res.data || [];
          break;
        case 'parts':
          res = await partsAPI.list({ limit: 100 });
          items = res.data || [];
          break;
        case 'services':
          res = await servicesAPI.list({ limit: 100 });
          // Services endpoint wraps response in {data: [...]}
          items = res.data?.data || res.data || [];
          break;
      }
      setListings(items);
    } catch (err) {
      setError('Failed to load listings');
      console.error(err);
    }
    setLoading(false);
  }, [activeTab]);

  useEffect(() => {
    fetchListings();
  }, [fetchListings]);

  function toggleSelect(id) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleSelectAll() {
    if (selected.size === listings.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(listings.map((l) => l.id)));
    }
  }

  async function handleBulkDelete() {
    if (selected.size === 0) return;
    setDeleting(true);
    setError(null);
    try {
      const res = await adminAPI.bulkDelete(activeTab, Array.from(selected));
      const { deleted } = res.data;
      setConfirmDelete(false);
      setSelected(new Set());
      await fetchListings();
      alert(`Deleted ${deleted} ${activeTab} successfully.`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete listings');
    }
    setDeleting(false);
  }

  function renderRow(item) {
    const fields = {
      laptops: [
        { label: 'Title', value: item.title },
        { label: 'Brand', value: item.brand },
        { label: 'Model', value: item.model },
        { label: 'Condition', value: item.condition },
        { label: 'Price', value: `$${item.price}` },
      ],
      parts: [
        { label: 'Title', value: item.title },
        { label: 'Category', value: item.category },
        { label: 'Condition', value: item.condition },
        { label: 'Price', value: `$${item.price}` },
      ],
      services: [
        { label: 'Title', value: item.title },
        { label: 'Type', value: item.service_type },
        { label: 'Price', value: `$${item.price}` },
      ],
    };

    return fields[activeTab] || [];
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Manage Listings</h1>
          {selected.size > 0 && (
            <button
              onClick={() => setConfirmDelete(true)}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              disabled={deleting}
            >
              <Trash2 className="w-4 h-4" />
              Delete Selected ({selected.size})
            </button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 border-b border-gray-200">
          {TABS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {/* Confirm dialog */}
        {confirmDelete && (
          <div className="mb-6 p-4 border border-red-200 bg-red-50 rounded-lg flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800">
                Delete {selected.size} {activeTab}?
              </p>
              <p className="text-sm text-red-600 mt-1">This action cannot be undone.</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setConfirmDelete(false)}
                className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                onClick={handleBulkDelete}
                className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Confirm Delete'}
              </button>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Table */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No {activeTab} found.</div>
        ) : (
          <div className="overflow-x-auto border border-gray-200 rounded-lg">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="p-3 w-10">
                    <input
                      type="checkbox"
                      checked={selected.size === listings.length && listings.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-gray-300"
                    />
                  </th>
                  <th className="p-3 text-left font-medium text-gray-600">#</th>
                  {renderRow(listings[0]).map((f) => (
                    <th key={f.label} className="p-3 text-left font-medium text-gray-600">
                      {f.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {listings.map((item, idx) => (
                  <tr
                    key={item.id}
                    className={`hover:bg-gray-50 transition-colors ${
                      selected.has(item.id) ? 'bg-blue-50' : ''
                    }`}
                  >
                    <td className="p-3">
                      <input
                        type="checkbox"
                        checked={selected.has(item.id)}
                        onChange={() => toggleSelect(item.id)}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="p-3 text-gray-400">{idx + 1}</td>
                    {renderRow(item).map((f) => (
                      <td key={f.label} className="p-3 text-gray-700">
                        {f.value}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="mt-4 text-sm text-gray-400">
          {!loading && `${listings.length} ${activeTab} total`}
          {selected.size > 0 && ` · ${selected.size} selected`}
        </div>
      </main>
      <Footer />
    </div>
  );
}
