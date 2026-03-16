import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import Loading from './ui/Loading';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, initialize } = useAuthStore();
  
  // Initialize auth state on mount
  if (!isAuthenticated && !localStorage.getItem('token')) {
    return <Navigate to="/login" replace />;
  }
  
  // Show loading while checking auth
  if (!isAuthenticated) {
    return <Loading />;
  }
  
  return children;
}