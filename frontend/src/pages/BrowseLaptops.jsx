import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Card from '../components/Card';
import Spinner from '../components/Spinner';
import EmptyState from '../components/EmptyState';
import Input from '../components/Input';
import Button from '../components/Button';
import { laptopsAPI } from '../api';

export default function BrowseLaptops() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const navigate = useNavigate();

  // Read filters from URL params
  const search = searchParams.get('search') || '';
  const brand = searchParams.get('brand') || '';
  const category = searchParams.get('category') || '';
  const condition = searchParams.get('condition') || '';
  const minPrice = searchParams.get('min_price') || '';
  const maxPrice = searchParams.get('max_price') || '';
  const skip = parseInt(searchParams.get('skip') || '0', 10);
  const limit = 12;

  // Fetch items when filters change
  useEffect(() => {
    async function fetchItems() {
      setLoading(true);
      setError(null);
      try {
        const params = { skip, limit };
        if (search) params.search = search;
        if (brand) params.brand = brand;
        if (category) params.category = category;
        if (condition) params.condition = condition;
        if (minPrice) params.min_price = parseFloat(minPrice);
        if (maxPrice) params.max_price = parseFloat(maxPrice);

        const res = await laptopsAPI.list(params);
        setItems(res.data || []);

        // Get total count from headers or fallback to items length
        const totalCount = res.headers?.['x-total-count']
          ? parseInt(res.headers['x-total-count'], 10)
          : (res.data?.length || 0);
        setTotal(totalCount);
      } catch (err) {
        console.error('Failed to fetch laptops:', err);
        setError('Failed to load laptops. Please try again.');
        setItems([]);
      } finally {
        setLoading(false);
      }
    }
    fetchItems();
  }, [search, brand, category, condition, minPrice, maxPrice, skip]);

  // Update URL params helper (resets pagination on filter change)
  function updateFilter(key, value) {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    newParams.delete('skip'); // Reset pagination when filters change
    setSearchParams(newParams);
  }

  // Load more items (preserve skip for pagination)
  function loadMore() {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('skip', skip + limit);
    setSearchParams(newParams);
  }

  // Clear all filters
  function clearFilters() {
    setSearchParams(new URLSearchParams());
  }

  const hasMore = skip + limit < total;

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Mobile filter toggle */}
            <div className="md:hidden mb-4">
              <Button
                variant="secondary"
                onClick={() => setMobileFiltersOpen(!mobileFiltersOpen)}
                className="w-full"
              >
                {mobileFiltersOpen ? 'Hide Filters' : 'Show Filters'}
              </Button>
            </div>

            {/* Filter Sidebar */}
            <div className={`${mobileFiltersOpen ? 'block' : 'hidden'} md:block w-full md:w-64 flex-shrink-0 bg-white p-4 rounded-lg border border-gray-200 h-fit`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-gray-900">Filters</h3>
                <button
                  onClick={clearFilters}
                  className="text-sm text-blue-600 hover:text-blue-700 transition-colors"
                >
                  Clear All
                </button>
              </div>

              <div className="flex flex-col gap-4">
                {/* Search Input */}
                <Input
                  label="Search"
                  type="text"
                  placeholder="Search laptops..."
                  value={search}
                  onChange={(e) => updateFilter('search', e.target.value)}
                />

                {/* Brand Dropdown */}
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">Brand</label>
                  <select
                    value={brand}
                    onChange={(e) => updateFilter('brand', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  >
                    <option value="">All Brands</option>
                    {['Apple', 'Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Other'].map((b) => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                  </select>
                </div>

                {/* Category Dropdown (Laptops only) */}
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">Category</label>
                  <select
                    value={category}
                    onChange={(e) => updateFilter('category', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  >
                    <option value="">All Categories</option>
                    {['Business', 'Gaming', 'Ultrabook', 'Budget'].map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                {/* Condition Dropdown */}
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">Condition</label>
                  <select
                    value={condition}
                    onChange={(e) => updateFilter('condition', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  >
                    <option value="">All Conditions</option>
                    {['New', 'Like New', 'Good', 'Fair'].map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                {/* Price Range */}
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">Min Price</label>
                  <Input
                    type="number"
                    placeholder="0"
                    value={minPrice}
                    onChange={(e) => updateFilter('min_price', e.target.value)}
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-gray-700">Max Price</label>
                  <Input
                    type="number"
                    placeholder="Any"
                    value={maxPrice}
                    onChange={(e) => updateFilter('max_price', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Results Section */}
            <div className="flex-1">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">
                  Browse Laptops
                  {total > 0 && <span className="text-sm font-normal text-gray-500 ml-2">({total} results)</span>}
                </h2>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm p-4 mb-6">
                  {error}
                </div>
              )}

              {loading ? (
                <div className="flex justify-center py-12">
                  <Spinner size="lg" />
                </div>
              ) : items.length === 0 ? (
                <EmptyState
                  title="No laptops found"
                  description="Try adjusting your filters or search query"
                  icon="package"
                />
              ) : (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {items.map((item) => (
                      <Card
                        key={item.id || item._id}
                        title={item.title}
                        price={item.price}
                        condition={item.condition}
                        image={item.image_url}
                        badge={item.brand}
                        onClick={() => navigate(`/laptops/${item.id || item._id}`)}
                      />
                    ))}
                  </div>

                  {/* Load More Pagination */}
                  {hasMore && (
                    <div className="flex justify-center mt-8">
                      <Button onClick={loadMore} variant="secondary">
                        Load More
                      </Button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
