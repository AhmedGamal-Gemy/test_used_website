import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Input from '../components/Input';
import Button from '../components/Button';
import Spinner from '../components/Spinner';
import { usersAPI } from '../api';

export default function Profile() {
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    location: '',
    avatar_url: '',
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [authLoading, isAuthenticated, navigate]);

  // Fetch profile on mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchProfile();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  async function fetchProfile() {
    setLoading(true);
    setError(null);
    try {
      const { data } = await usersAPI.getProfile();
      setProfile(data);
      setFormData({
        full_name: data.full_name || '',
        phone: data.phone || '',
        location: data.location || '',
        avatar_url: data.avatar_url || '',
      });
    } catch (err) {
      console.error('Failed to fetch profile:', err);
      setError('Failed to load profile. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }

  function handleEdit() {
    setIsEditing(true);
    setSuccess(null);
    setError(null);
  }

  function handleCancel() {
    setIsEditing(false);
    // Reset form data to current profile values
    if (profile) {
      setFormData({
        full_name: profile.full_name || '',
        phone: profile.phone || '',
        location: profile.location || '',
        avatar_url: profile.avatar_url || '',
      });
    }
    setError(null);
    setSuccess(null);
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const { data } = await usersAPI.updateProfile(formData);
      setProfile(data);
      setFormData({
        full_name: data.full_name || '',
        phone: data.phone || '',
        location: data.location || '',
        avatar_url: data.avatar_url || '',
      });
      setIsEditing(false);
      setSuccess('Profile updated successfully!');
    } catch (err) {
      console.error('Failed to update profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile. Please try again.');
    } finally {
      setSaving(false);
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-4xl mx-auto px-4 py-8 flex items-center justify-center">
          <Spinner size="lg" />
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">My Profile</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm p-4 mb-6">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm p-4 mb-6">
            {success}
          </div>
        )}

        {!isEditing ? (
          // Display Mode
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-6">
            {/* Avatar */}
            <div className="flex items-center gap-4">
              {profile?.avatar_url ? (
                <img
                  src={profile.avatar_url}
                  alt="Avatar"
                  className="w-20 h-20 rounded-full object-cover border border-gray-200"
                />
              ) : (
                <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center">
                  <span className="text-2xl text-gray-500">
                    {(profile?.full_name || profile?.email || '?').charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {profile?.full_name || 'No name set'}
                </h2>
                <p className="text-sm text-gray-500">{profile?.email}</p>
              </div>
            </div>

            {/* Profile Info */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-gray-100">
              <div>
                <p className="text-sm font-medium text-gray-500">Full Name</p>
                <p className="text-gray-900">{profile?.full_name || 'Not set'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Email</p>
                <p className="text-gray-900">{profile?.email}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Phone</p>
                <p className="text-gray-900">{profile?.phone || 'Not set'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Location</p>
                <p className="text-gray-900">{profile?.location || 'Not set'}</p>
              </div>
            </div>

            {/* Edit Button */}
            <div className="pt-4 border-t border-gray-100">
              <Button variant="primary" onClick={handleEdit}>
                Edit Profile
              </Button>
            </div>
          </div>
        ) : (
          // Edit Mode
          <form onSubmit={handleSave} className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Edit Profile</h2>

            <Input
              label="Full Name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Enter your full name"
            />

            <Input
              label="Email"
              value={profile?.email || ''}
              disabled
              className="bg-gray-50"
            />

            <Input
              label="Phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              placeholder="Enter your phone number"
            />

            <Input
              label="Location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="Enter your location"
            />

            <Input
              label="Avatar URL"
              name="avatar_url"
              type="url"
              value={formData.avatar_url}
              onChange={handleChange}
              placeholder="https://example.com/avatar.jpg"
            />

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4 border-t border-gray-100">
              <Button type="submit" variant="primary" loading={saving}>
                Save Changes
              </Button>
              <Button type="button" variant="secondary" onClick={handleCancel} disabled={saving}>
                Cancel
              </Button>
            </div>
          </form>
        )}
      </main>
      <Footer />
    </div>
  );
}
