import client from './client';

// Auth API
export const authAPI = {
  signup: (data) => client.post('/api/auth/signup', data),
  signin: (data) => client.post('/api/auth/signin', data),
  signout: (data) => client.post('/api/auth/signout', data),
  refresh: (data) => client.post('/api/auth/refresh', data),
};

// Laptops API
export const laptopsAPI = {
  list: (params) => client.get('/api/laptops', { params }),
  get: (id) => client.get(`/api/laptops/${id}`),
  create: (data) => client.post('/api/laptops', data),
  update: (id, data) => client.put(`/api/laptops/${id}`, data),
  delete: (id) => client.delete(`/api/laptops/${id}`),
  uploadImage: (id, formData) =>
    client.post(`/api/laptops/${id}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// Parts API
export const partsAPI = {
  list: (params) => client.get('/api/parts', { params }),
  get: (id) => client.get(`/api/parts/${id}`),
  create: (data) => client.post('/api/parts', data),
  update: (id, data) => client.put(`/api/parts/${id}`, data),
  delete: (id) => client.delete(`/api/parts/${id}`),
  uploadImage: (id, formData) =>
    client.post(`/api/parts/${id}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// Users API
export const usersAPI = {
  getProfile: () => client.get('/api/users/me'),
  updateProfile: (data) => client.put('/api/users/me', data),
};

// Favorites API
export const favoritesAPI = {
  addLaptop: (id) => client.post(`/api/favorites/laptops/${id}`),
  removeLaptop: (id) => client.delete(`/api/favorites/laptops/${id}`),
  addPart: (id) => client.post(`/api/favorites/parts/${id}`),
  removePart: (id) => client.delete(`/api/favorites/parts/${id}`),
};

// Reviews API
export const reviewsAPI = {
  createReview: (sellerId, data) => client.post(`/api/reviews/seller/${sellerId}`, data),
  getSellerReviews: (sellerId) => client.get(`/api/reviews/seller/${sellerId}`),
};

// Messages / Contact API
export const messagesAPI = {
  sendInquiry: (data) => client.post('/api/messages/contact', data),
  getConversation: (params) => client.get('/api/messages/conversation', { params }),
  getConversations: () => client.get('/api/messages/conversations'),
  // Admin endpoints
  getAdminConversations: () => client.get('/api/messages/admin/conversations'),
  getAdminConversation: (params) => client.get('/api/messages/admin/conversation', { params }),
  adminReply: (data) => client.post('/api/messages/admin/reply', data),
};

// Services API
export const servicesAPI = {
  list: (params) => client.get('/api/services', { params }),
  get: (id) => client.get(`/api/services/${id}`),
  create: (data) => client.post('/api/services', data),
  update: (id, data) => client.put(`/api/services/${id}`, data),
  delete: (id) => client.delete(`/api/services/${id}`),
};

// Orders API
export const ordersAPI = {
  createOrder: (data) => client.post('/api/orders', data),
  getMyOrders: () => client.get('/api/orders'),
  getOrder: (id) => client.get(`/api/orders/${id}`),
  // Admin
  getAllOrders: () => client.get('/api/admin/orders'),
  updateOrderStatus: (id, data) => client.put(`/api/admin/orders/${id}/status`, data),
};

// Admin API
export const adminAPI = {
  listUsers: (params) => client.get('/api/users/', { params }),
  updateUserRole: (userId, role) => client.patch(`/api/users/${userId}/role`, { role }),
  deleteUser: (userId) => client.delete(`/api/users/${userId}`),
  getDashboard: () => client.get('/api/users/analytics/dashboard'),
  bulkDelete: (resource, ids) => client.post(`/api/admin/bulk-delete/${resource}`, { ids }),
};

export default {
  auth: authAPI,
  laptops: laptopsAPI,
  parts: partsAPI,
  users: usersAPI,
  favorites: favoritesAPI,
  reviews: reviewsAPI,
  messages: messagesAPI,
  services: servicesAPI,
  orders: ordersAPI,
  admin: adminAPI,
};
