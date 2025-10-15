import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProtectedRoute({ children, requireAdmin = false }) {
  const { user, loading } = useAuth();

  console.log('ProtectedRoute - Loading:', loading);
  console.log('ProtectedRoute - User:', user);
  console.log('ProtectedRoute - Require Admin:', requireAdmin);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    console.log('ProtectedRoute - No user, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !user.is_admin) {
    console.log('ProtectedRoute - Admin required but user is not admin');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center p-8">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
          <p className="text-sm text-gray-500">Admin access required.</p>
        </div>
      </div>
    );
  }

  console.log('ProtectedRoute - Access granted, rendering children');
  return children;
}