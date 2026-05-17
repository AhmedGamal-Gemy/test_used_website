import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Card from '../components/Card';
import Spinner from '../components/Spinner';
import EmptyState from '../components/EmptyState';
import { laptopsAPI, partsAPI, favoritesAPI, usersAPI } from '../api';
import { useToast } from '../hooks/useToast';

export default function Favorites() {
  const { isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('laptops');
  const [laptops, setLaptops] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { showError } = useToast();

  useEffect(() => {
    if (!isAuthenticated) { navigate('/login'); return; }

    async function fetchFavorites() {
      try {
        setLoading(true);
        setError(null);

        // Fetch user profile to get favorite IDs
        const { data: user } = await usersAPI.getProfile();
        const favoriteLaptopIds = user.favorite_laptops || [];
        const favoritePartIds = user.favorite_parts || [];

        // Fetch all laptops and parts, then filter by favorites
        const [laptopsRes, partsRes] = await Promise.all([
          laptopsAPI.list({ limit: 100 }),
          partsAPI.list({ limit: 100 }),
        ]);

        const allLaptops = laptopsRes.data || [];
        const allParts = partsRes.data || [];

        // Filter to only include favorites
        const favoriteLaptops = allLaptops.filter(laptop =>
          favoriteLaptopIds.includes(laptop.id || laptop._id)
        );
        const favoriteParts = allParts.filter(part =>
          favoritePartIds.includes(part.id || part._id)
        );

        setLaptops(favoriteLaptops);
        setParts(favoriteParts);
      } catch (err) {
        console.error('Failed to fetch favorites:', err);
        setError('Failed to load favorites. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    fetchFavorites();
  }, [isAuthenticated, navigate]);

  const handleRemoveLaptop = async (id) => {
    try {
      await favoritesAPI.removeLaptop(id);
      setLaptops(prev => prev.filter(laptop => (laptop.id || laptop._id) !== id));
    } catch (err) {
      console.error('Failed to remove laptop from favorites:', err);
      showError('Failed to remove from favorites. Please try again.');
    }
  };

  const handleRemovePart = async (id) => {
    try {
      await favoritesAPI.removePart(id);
      setParts(prev => prev.filter(part => (part.id || part._id) !== id));
    } catch (err) {
      console.error('Failed to remove part from favorites:', err);
      showError('Failed to remove from favorites. Please try again.');
    }
  };

  const handleCardClick = (item, type) => {
    navigate(`/${type}/${item.id || item._id}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl mx-auto px-4 py-8">
          <Spinner size="lg" className="py-12" />
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">My Favorites</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm p-4 mb-6">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('laptops')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'laptops'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Laptops
          </button>
          <button
            onClick={() => setActiveTab('parts')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'parts'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Parts
          </button>
        </div>

        {/* Laptops Tab */}
        {activeTab === 'laptops' && (
          <>
            {laptops.length === 0 ? (
              <EmptyState
                icon="package"
                title="No favorite laptops"
                description="You haven't added any laptops to your favorites yet."
              />
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {laptops.map(laptop => (
                  <Card
                    key={laptop.id || laptop._id}
                    image={laptop.image_url}
                    title={laptop.title}
                    price={laptop.price}
                    condition={laptop.condition}
                    isFavorited={true}
                    onToggleFavorite={() => handleRemoveLaptop(laptop.id || laptop._id)}
                    onClick={() => handleCardClick(laptop, 'laptops')}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* Parts Tab */}
        {activeTab === 'parts' && (
          <>
            {parts.length === 0 ? (
              <EmptyState
                icon="package"
                title="No favorite parts"
                description="You haven't added any parts to your favorites yet."
              />
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {parts.map(part => (
                  <Card
                    key={part.id || part._id}
                    image={part.image_url}
                    title={part.title}
                    price={part.price}
                    condition={part.condition}
                    isFavorited={true}
                    onToggleFavorite={() => handleRemovePart(part.id || part._id)}
                    onClick={() => handleCardClick(part, 'parts')}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </main>
      <Footer />
    </div>
  );
}
