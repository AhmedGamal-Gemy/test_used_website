import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, Laptop, Wrench, Star, MessageSquare,
  Heart, Package, Shield, TrendingUp, MessageCircle, BarChart3,
  Inbox, MailQuestion, MessageSquareReply, DollarSign,
  Trash2, AlertTriangle
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Spinner from '../components/Spinner';
import Button from '../components/Button';
import { adminAPI, usersAPI } from '../api';
import { useAuth } from '../contexts/AuthContext';

export default function AdminDashboard() {
  const { isAdmin, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedUsers, setSelectedUsers] = useState(new Set());
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAdmin) {
      navigate('/');
      return;
    }
    fetchDashboard();
    fetchUsers();
  }, [authLoading, isAdmin]);

  async function fetchDashboard() {
    try {
      const res = await adminAPI.getDashboard();
      setDashboard(res.data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    }
  }

  async function fetchUsers() {
    try {
      const res = await adminAPI.listUsers();
      setUsers(res.data || []);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
    setLoading(false);
  }

  async function handleRoleChange(userId, newRole) {
    try {
      await adminAPI.updateUserRole(userId, newRole);
      fetchUsers();
    } catch (err) {
      alert('Failed to update user role');
    }
  }

  function toggleUserSelect(id) {
    setSelectedUsers((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleSelectAllUsers() {
    if (selectedUsers.size === users.length) {
      setSelectedUsers(new Set());
    } else {
      setSelectedUsers(new Set(users.map((u) => u.id)));
    }
  }

  async function handleDeleteUser(userId) {
    setConfirmDelete({ type: 'single', ids: [userId] });
  }

  async function handleBulkDeleteUsers() {
    setConfirmDelete({ type: 'bulk', ids: Array.from(selectedUsers) });
  }

  async function executeDelete() {
    if (!confirmDelete) return;
    setDeleting(true);
    setError(null);
    try {
      const { type, ids } = confirmDelete;
      if (type === 'single') {
        await adminAPI.deleteUser(ids[0]);
      } else {
        await adminAPI.bulkDelete('users', ids);
      }
      setConfirmDelete(null);
      setSelectedUsers(new Set());
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete user(s)');
    }
    setDeleting(false);
  }

  if (authLoading || loading) {
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

  if (!isAdmin) return null;

  const stats = [
    { label: 'Total Users', value: dashboard?.total_users || 0, icon: Users, color: 'text-blue-600 bg-blue-50' },
    { label: 'Admins', value: dashboard?.total_admins || 0, icon: Shield, color: 'text-purple-600 bg-purple-50' },
    { label: 'Laptops', value: dashboard?.total_laptops || 0, icon: Laptop, color: 'text-green-600 bg-green-50' },
    { label: 'Parts', value: dashboard?.total_parts || 0, icon: Package, color: 'text-orange-600 bg-orange-50' },
    { label: 'Services', value: dashboard?.total_services || 0, icon: Wrench, color: 'text-indigo-600 bg-indigo-50' },
    { label: 'Reviews', value: dashboard?.total_reviews || 0, icon: Star, color: 'text-yellow-600 bg-yellow-50' },
    { label: 'Favorites', value: dashboard?.total_favorites || 0, icon: Heart, color: 'text-red-600 bg-red-50' },
    { label: 'Listings', value: dashboard?.total_listings || 0, icon: Package, color: 'text-cyan-600 bg-cyan-50' },
  ];

  const d = dashboard || {};

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center gap-3 mb-8">
          <LayoutDashboard className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">{error}</div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
          {stats.map((stat) => (
            <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2 rounded-lg ${stat.color}`}>
                  <stat.icon className="w-5 h-5" />
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-sm text-gray-500">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Inquiries & Conversations Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Message Stats */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <MessageCircle className="w-5 h-5 text-blue-600" />
              Inquiries & Messages
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <Inbox className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-blue-600">{d.total_inquiries || 0}</p>
                <p className="text-xs text-gray-500">Total Inquiries</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <MessageSquareReply className="w-6 h-6 text-green-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-green-600">{d.total_admin_replies || 0}</p>
                <p className="text-xs text-gray-500">Your Replies</p>
              </div>
              <div className="bg-orange-50 rounded-lg p-4 text-center">
                <MailQuestion className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-orange-600">{d.unanswered_inquiries || 0}</p>
                <p className="text-xs text-gray-500">Unanswered</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <MessageSquare className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-purple-600">{d.total_conversations || 0}</p>
                <p className="text-xs text-gray-500">Conversations</p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Response Rate</span>
                <span className="font-semibold text-gray-900">
                  {d.total_inquiries > 0
                    ? `${Math.round((d.total_admin_replies / d.total_inquiries) * 100)}%`
                    : '-'}
                </span>
              </div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: d.total_inquiries > 0 ? `${Math.min((d.total_admin_replies / d.total_inquiries) * 100, 100)}%` : '0%' }}
                />
              </div>
            </div>
          </div>

          {/* Price Distribution */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-600" />
              Laptop Price Distribution
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Budget ($0 - $500)</span>
                  <span className="font-semibold">{d.price_ranges?.budget || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-green-500 h-2.5 rounded-full" style={{
                    width: `${d.total_laptops > 0 ? ((d.price_ranges?.budget || 0) / d.total_laptops) * 100 : 0}%`
                  }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Mid-Range ($500 - $1500)</span>
                  <span className="font-semibold">{d.price_ranges?.mid || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-500 h-2.5 rounded-full" style={{
                    width: `${d.total_laptops > 0 ? ((d.price_ranges?.mid || 0) / d.total_laptops) * 100 : 0}%`
                  }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Premium ($1500+)</span>
                  <span className="font-semibold">{d.price_ranges?.premium || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-purple-500 h-2.5 rounded-full" style={{
                    width: `${d.total_laptops > 0 ? ((d.price_ranges?.premium || 0) / d.total_laptops) * 100 : 0}%`
                  }} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity + Top Favorited */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Recent Activity */}
          {d && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                Activity (Last 30 Days)
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-blue-600">{d.recent_laptops_30d || 0}</p>
                  <p className="text-sm text-gray-500">New Laptops</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-orange-600">{d.recent_parts_30d || 0}</p>
                  <p className="text-sm text-gray-500">New Parts</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-green-600">{d.total_listings || 0}</p>
                  <p className="text-sm text-gray-500">Total Listings</p>
                </div>
              </div>
            </div>
          )}

          {/* Top Favorited */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Heart className="w-5 h-5 text-red-600" />
              Top Favorited Listings
            </h2>
            {d.top_favorited && d.top_favorited.length > 0 ? (
              <div className="space-y-3">
                {d.top_favorited.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-sm font-bold text-gray-400 w-5">#{idx + 1}</span>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{item.title}</p>
                        <p className="text-xs text-gray-500 capitalize">{item.type}{item.price ? ` · $${item.price}` : ''}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-red-500 flex-shrink-0">
                      <Heart className="w-4 h-4 fill-red-500" />
                      <span className="text-sm font-semibold">{item.favorite_count}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-6">No favorited listings yet.</p>
            )}
          </div>
        </div>

        {/* User Signups Over Time */}
        {d.user_signups && d.user_signups.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              User Signups (Last 6 Months)
            </h2>
            <div className="flex items-end gap-2 h-32">
              {d.user_signups.map((item, idx) => {
                const maxCount = Math.max(...d.user_signups.map(s => s.count), 1);
                const heightPct = (item.count / maxCount) * 100;
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                    <span className="text-xs font-semibold text-gray-700">{item.count}</span>
                    <div
                      className="w-full bg-blue-500 rounded-t"
                      style={{ height: `${heightPct}%`, minHeight: '4px' }}
                    />
                    <span className="text-xs text-gray-500">{monthNames[item.month - 1]}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'overview' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'users' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            User Management
          </button>
        </div>

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-gray-900">Manage Users</h2>
                  <p className="text-sm text-gray-500">Promote, demote, or remove users</p>
                </div>
                {selectedUsers.size > 0 && (
                  <button
                    onClick={handleBulkDeleteUsers}
                    className="flex items-center gap-2 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Selected ({selectedUsers.size})
                  </button>
                )}
              </div>
            </div>

            {/* Confirm dialog */}
            {confirmDelete && (
              <div className="p-4 border-b border-red-200 bg-red-50 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-red-800">
                    Delete {confirmDelete.type === 'single' ? 'this user' : `${confirmDelete.ids.length} users`}?
                  </p>
                  <p className="text-sm text-red-600 mt-1">This action cannot be undone.</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setConfirmDelete(null)}
                    className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                    disabled={deleting}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={executeDelete}
                    className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
                    disabled={deleting}
                  >
                    {deleting ? 'Deleting...' : 'Confirm'}
                  </button>
                </div>
              </div>
            )}

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="p-3 w-10">
                      <input
                        type="checkbox"
                        checked={selectedUsers.size === users.length && users.length > 0}
                        onChange={toggleSelectAllUsers}
                        className="rounded border-gray-300"
                      />
                    </th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Email</th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Name</th>
                    <th className="text-left p-3 text-sm font-medium text-gray-500">Role</th>
                    <th className="text-right p-3 text-sm font-medium text-gray-500">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className={`border-b border-gray-100 hover:bg-gray-50 ${
                      selectedUsers.has(user.id) ? 'bg-blue-50' : ''
                    }`}>
                      <td className="p-3">
                        <input
                          type="checkbox"
                          checked={selectedUsers.has(user.id)}
                          onChange={() => toggleUserSelect(user.id)}
                          className="rounded border-gray-300"
                        />
                      </td>
                      <td className="p-3 text-sm text-gray-900">{user.email}</td>
                      <td className="p-3 text-sm text-gray-600">{user.full_name || '-'}</td>
                      <td className="p-3">
                        <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                          user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {user.role === 'admin' ? (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => handleRoleChange(user.id, 'user')}
                            >
                              Demote
                            </Button>
                          ) : (
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleRoleChange(user.id, 'admin')}
                            >
                              Promote
                            </Button>
                          )}
                          <button
                            onClick={() => handleDeleteUser(user.id)}
                            className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                            title="Delete user"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
