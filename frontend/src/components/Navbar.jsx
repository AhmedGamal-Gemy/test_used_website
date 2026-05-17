import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Wrench, LayoutDashboard, ChevronDown } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const [adminDropdownOpen, setAdminDropdownOpen] = useState(false);
  const adminDropdownRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (adminDropdownRef.current && !adminDropdownRef.current.contains(event.target)) {
        setAdminDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-xl font-bold text-blue-600">
            Marketplace
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <Link to="/" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
              Home
            </Link>
            <Link to="/laptops" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
              Laptops
            </Link>
            <Link to="/parts" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
              Parts
            </Link>
            <Link to="/services" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors flex items-center gap-1">
              <Wrench className="w-4 h-4" />
              Services
            </Link>
            <Link to="/favorites" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
              Favorites
            </Link>
            <Link to="/orders" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
              My Orders
            </Link>
            <Link to="/messages" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
              Messages
            </Link>
            {isAdmin && (
              <div className="relative" ref={adminDropdownRef}>
                <button
                  onClick={() => setAdminDropdownOpen(!adminDropdownOpen)}
                  className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-1"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Admin
                  <ChevronDown className={`w-3 h-3 transition-transform ${adminDropdownOpen ? 'rotate-180' : ''}`} />
                </button>
                {adminDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-50">
                    <Link
                      to="/admin"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-blue-600 transition-colors"
                      onClick={() => setAdminDropdownOpen(false)}
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="/admin/orders"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-blue-600 transition-colors"
                      onClick={() => setAdminDropdownOpen(false)}
                    >
                      Orders
                    </Link>
                    <Link
                      to="/create"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-blue-600 transition-colors"
                      onClick={() => setAdminDropdownOpen(false)}
                    >
                      Create Listing
                    </Link>
                    <Link
                      to="/admin/listings"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-blue-600 transition-colors"
                      onClick={() => setAdminDropdownOpen(false)}
                    >
                      Manage Listings
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <Link
                  to="/profile"
                  className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
                >
                  {user?.email || 'Profile'}
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="text-sm font-medium bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
