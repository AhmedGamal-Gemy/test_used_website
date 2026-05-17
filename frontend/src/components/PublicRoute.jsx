import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function PublicRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  if (isAuthenticated) return <Navigate to="/" replace />;
  return children;
}
