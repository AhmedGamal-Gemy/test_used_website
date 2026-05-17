import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Laptop, Wrench } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Card from '../components/Card';
import Spinner from '../components/Spinner';
import { laptopsAPI, partsAPI } from '../api';

export default function Home() {
  const [laptops, setLaptops] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchFeatured() {
      try {
        const [laptopsRes, partsRes] = await Promise.all([
          laptopsAPI.list({ limit: 8 }),
          partsAPI.list({ limit: 8 }),
        ]);
        setLaptops(laptopsRes.data || []);
        setParts(partsRes.data || []);
      } catch (err) {
        console.error('Failed to fetch featured listings:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchFeatured();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (search.trim()) {
      navigate(`/laptops?search=${encodeURIComponent(search.trim())}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1">
        {/* Hero section */}
        <section className="bg-blue-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Find Your Perfect Laptop or Part
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              Buy and sell used laptops and computer parts with confidence
            </p>
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search for laptops, parts..."
                  className="flex-1 px-4 py-3 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
                <button
                  type="submit"
                  className="px-6 py-3 bg-white text-blue-600 font-medium rounded-lg hover:bg-blue-50 transition-colors flex items-center gap-2"
                >
                  <Search className="w-5 h-5" />
                  Search
                </button>
              </div>
            </form>
          </div>
        </section>

        {/* Category cards */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Browse Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              onClick={() => navigate('/laptops')}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer flex items-center gap-4"
            >
              <div className="p-3 bg-blue-100 rounded-lg">
                <Laptop className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Laptops</h3>
                <p className="text-gray-600">Browse used laptops from trusted sellers</p>
              </div>
            </div>
            <div
              onClick={() => navigate('/parts')}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer flex items-center gap-4"
            >
              <div className="p-3 bg-green-100 rounded-lg">
                <Wrench className="w-8 h-8 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Parts</h3>
                <p className="text-gray-600">Find computer parts and components</p>
              </div>
            </div>
          </div>
        </section>

        {/* Featured Listings */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Spinner size="lg" />
          </div>
        ) : (
          <>
            {/* Featured Laptops */}
            {laptops.length > 0 && (
              <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Featured Laptops</h2>
                  <button
                    onClick={() => navigate('/laptops')}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View All →
                  </button>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {laptops.map((laptop) => (
                    <Card
                      key={laptop.id || laptop._id}
                      image={laptop.image_url}
                      title={laptop.title}
                      price={laptop.price}
                      condition={laptop.condition}
                      onClick={() => navigate(`/laptops/${laptop.id || laptop._id}`)}
                    />
                  ))}
                </div>
              </section>
            )}

            {/* Featured Parts */}
            {parts.length > 0 && (
              <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Featured Parts</h2>
                  <button
                    onClick={() => navigate('/parts')}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View All →
                  </button>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {parts.map((part) => (
                    <Card
                      key={part.id || part._id}
                      image={part.image_url}
                      title={part.title}
                      price={part.price}
                      condition={part.condition}
                      onClick={() => navigate(`/parts/${part.id || part._id}`)}
                    />
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>
      <Footer />
    </div>
  );
}
