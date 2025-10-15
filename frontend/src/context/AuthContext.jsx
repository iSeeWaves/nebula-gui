/* eslint-disable react-refresh/only-export-components */
import { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    
    if (token) {
      try {
        const response = await api.get('/auth/me');
        setUser(response.data);
        setLoading(false); // ✅ Fixed
        return response.data;
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        setLoading(false); // ✅ Fixed
      }
    } else {
      setLoading(false); // ✅ Fixed
    }
  };

  const login = async (username, password) => {
    try {
      console.log('AuthContext: Starting login...');
      
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      console.log('AuthContext: Sending login request...');
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log('AuthContext: Login response received');
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      console.log('AuthContext: Token saved');

      // Get user info after login
      console.log('AuthContext: Fetching user info...');
      const userResponse = await api.get('/auth/me');
      console.log('AuthContext: User info received:', userResponse.data);
      
      setUser(userResponse.data);
      setLoading(false);
      
      return userResponse.data;
      
    } catch (error) {
      console.error('AuthContext: Login failed:', error);
      setLoading(false);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const value = {
    user,
    setUser,
    login,
    logout,
    loading,
    checkAuth,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};