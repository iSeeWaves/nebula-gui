import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '' },
    { path: '/certificates', label: 'Certificates', icon: '' },
    { path: '/client-setup', label: 'Client Setup', icon: '' }, // NEW!
    { path: '/configs', label: 'Configurations', icon: '' },
    { path: '/monitoring', label: 'Monitoring', icon: '' },
    { path: '/users', label: 'Users', icon: '', adminOnly: true },
    { path: '/audit', label: 'Audit Logs', icon: '', adminOnly: true },
  ];

  // Filter nav items based on user role
  const visibleNavItems = navItems.filter(item => 
    !item.adminOnly || user?.is_admin
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-xl md:text-2xl font-bold text-gray-900">Nebula GUI</h1>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-4">
              {visibleNavItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span className="mr-1">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </nav>

            <div className="flex items-center space-x-2 md:space-x-4">
              {/* Profile Link - Desktop */}
              <Link
                to="/profile"
                className="hidden sm:flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>{user?.username}</span>
                {user?.is_admin && (
                  <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded-full">
                    Admin
                  </span>
                )}
              </Link>
              
              <button
                onClick={handleLogout}
                className="px-3 py-2 text-xs md:text-sm text-red-600 hover:bg-red-50 rounded-md transition-colors"
              >
                Logout
              </button>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-md text-gray-700 hover:bg-gray-100"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {mobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden py-2 space-y-1">
              {/* Profile Link - Mobile */}
              <Link
                to="/profile"
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  location.pathname === '/profile'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">👤</span>
                Profile
                {user?.is_admin && (
                  <span className="ml-2 px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded-full">
                    Admin
                  </span>
                )}
              </Link>
              
              {visibleNavItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-3 py-2 rounded-md text-base font-medium ${
                    location.pathname === item.path
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
