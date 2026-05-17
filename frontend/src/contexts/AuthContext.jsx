import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, usersAPI } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!token;
  const isAdmin = user?.role === 'admin';

  // Auto-load user on mount if token exists
  useEffect(() => {
    if (token) {
      loadUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  async function loadUser() {
    try {
      const { data } = await usersAPI.getProfile();
      setUser(data);
    } catch {
      // Token invalid, clear
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      setToken(null);
      setUser(null);
    }
    setIsLoading(false);
  }

  async function login(email, password) {
    const { data } = await authAPI.signin({ email, password });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
    setToken(data.access_token);
    // Load user profile after login
    const { data: userData } = await usersAPI.getProfile();
    setUser(userData);
  }

  async function signup(email, password) {
    await authAPI.signup({ email, password });
    // Auto-signin after signup
    await login(email, password);
  }

  async function logout() {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await authAPI.signout({ refresh_token: refreshToken });
      }
    } catch {
      // Ignore errors on signout
    }
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, isAdmin, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
