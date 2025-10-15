import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';

export default function ProfilePage() {
  const { user, setUser } = useAuth();
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [loginHistory, setLoginHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    loadLoginHistory();
  }, []);

  const loadLoginHistory = async () => {
  try {
    const response = await api.get('/audit/logs/my');
    // Filter to only login/logout actions
    const loginLogs = response.data.filter(log => 
      ['login_success', 'login_failed', 'logout'].includes(log.action)
    );
    setLoginHistory(loginLogs);
  } catch (error) {
    console.error('Failed to load login history:', error);
  } finally {
    setLoadingHistory(false);
  }
};

  const EmailChangeModal = () => {
    const [email, setEmail] = useState(user?.email || '');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault();
      setError('');
      setSuccess('');
      setLoading(true);

      try {
        console.log('Sending email update request:', { email, password: '***' });
        
        const response = await api.put('/users/me/email', {
          email,
          password
        });
        
        console.log('Email update response:', response.data);
        
        // Update user context
        setUser(response.data);
        
        setSuccess('Email updated successfully!');
        
        setTimeout(() => {
          setShowEmailModal(false);
          setPassword('');
          setError('');
          setSuccess('');
        }, 2000);
      } catch (err) {
        console.error('Email update error:', err);
        let errorMessage = 'Failed to update email';
        
        if (err.response?.data?.detail) {
          if (typeof err.response.data.detail === 'string') {
            errorMessage = err.response.data.detail;
          } else if (Array.isArray(err.response.data.detail)) {
            errorMessage = err.response.data.detail.map(e => e.msg || e).join(', ');
          }
        } else if (err.message) {
          errorMessage = err.message;
        }
        
        console.error('Error message:', errorMessage);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg p-4 md:p-6 max-w-md w-full">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg md:text-xl font-bold text-gray-900">Change Email</h2>
            <button
              onClick={() => setShowEmailModal(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded text-sm">
                {success}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Email
              </label>
              <input
                type="email"
                value={user?.email}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                autoComplete="email"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                autoComplete="current-password"
                required
                placeholder="Enter your current password"
              />
              <p className="text-xs text-gray-500 mt-1">
                For security, please confirm your password to change your email
              </p>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={() => setShowEmailModal(false)}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Updating...' : 'Update Email'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const PasswordChangeModal = () => {
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [passwordStrength, setPasswordStrength] = useState({ score: 0, feedback: [] });

    const checkPasswordStrength = (password) => {
      const feedback = [];
      let score = 0;

      if (password.length >= 8) {
        score++;
      } else {
        feedback.push('At least 8 characters');
      }

      if (/[A-Z]/.test(password)) {
        score++;
      } else {
        feedback.push('One uppercase letter');
      }

      if (/[a-z]/.test(password)) {
        score++;
      } else {
        feedback.push('One lowercase letter');
      }

      if (/[0-9]/.test(password)) {
        score++;
      } else {
        feedback.push('One number');
      }

      if (/[^A-Za-z0-9]/.test(password)) {
        score++;
      } else {
        feedback.push('One special character');
      }

      setPasswordStrength({ score, feedback });
    };

    const handlePasswordChange = (e) => {
      const password = e.target.value;
      setNewPassword(password);
      checkPasswordStrength(password);
    };

    const getStrengthColor = () => {
      if (passwordStrength.score <= 2) return 'bg-red-500';
      if (passwordStrength.score <= 3) return 'bg-yellow-500';
      if (passwordStrength.score <= 4) return 'bg-blue-500';
      return 'bg-green-500';
    };

    const getStrengthText = () => {
      if (passwordStrength.score <= 2) return 'Weak';
      if (passwordStrength.score <= 3) return 'Fair';
      if (passwordStrength.score <= 4) return 'Good';
      return 'Strong';
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      setError('');
      setSuccess('');

      if (newPassword !== confirmPassword) {
        setError('New passwords do not match');
        return;
      }

      if (passwordStrength.score < 4) {
        setError('Password is too weak. Please meet all requirements.');
        return;
      }

      setLoading(true);

      try {
        await api.post('/users/me/change-password', {
          old_password: oldPassword,
          new_password: newPassword
        });

        setSuccess('Password changed successfully!');
        
        setTimeout(() => {
          setShowPasswordModal(false);
          setOldPassword('');
          setNewPassword('');
          setConfirmPassword('');
          setError('');
          setSuccess('');
        }, 2000);
      } catch (err) {
        let errorMessage = 'Failed to change password';
        if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        }
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg p-4 md:p-6 max-w-md w-full">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg md:text-xl font-bold text-gray-900">Change Password</h2>
            <button
              onClick={() => setShowPasswordModal(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded text-sm">
                {success}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Password
              </label>
              <input
                type="password"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                autoComplete="current-password"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={handlePasswordChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                autoComplete="new-password"
                required
              />
              
              {newPassword && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-gray-600">Password Strength:</span>
                    <span className={`font-medium ${
                      passwordStrength.score <= 2 ? 'text-red-600' :
                      passwordStrength.score <= 3 ? 'text-yellow-600' :
                      passwordStrength.score <= 4 ? 'text-blue-600' :
                      'text-green-600'
                    }`}>
                      {getStrengthText()}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getStrengthColor()}`}
                      style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                    />
                  </div>
                  {passwordStrength.feedback.length > 0 && (
                    <div className="mt-2 text-xs text-gray-600">
                      <p className="font-medium">Requirements:</p>
                      <ul className="list-disc list-inside">
                        {passwordStrength.feedback.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                autoComplete="new-password"
                required
              />
              {confirmPassword && newPassword !== confirmPassword && (
                <p className="text-xs text-red-600 mt-1">Passwords do not match</p>
              )}
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={() => setShowPasswordModal(false)}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || passwordStrength.score < 4}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Changing...' : 'Change Password'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const getActionIcon = (action) => {
    if (action === 'login_success') return '✅';
    if (action === 'login_failed') return '❌';
    if (action === 'logout') return '🚪';
    return '📝';
  };

  const getActionColor = (action) => {
    if (action === 'login_success') return 'text-green-600';
    if (action === 'login_failed') return 'text-red-600';
    if (action === 'logout') return 'text-gray-600';
    return 'text-blue-600';
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Profile</h1>
        <p className="text-sm text-gray-600 mt-1">Manage your account settings and view activity</p>
      </div>

      {/* Profile Information Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="text-sm font-medium text-gray-700">Username</p>
              <p className="text-sm text-gray-900">{user?.username}</p>
            </div>
            <span className="text-gray-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </span>
          </div>

          <div className="flex items-center justify-between py-3 border-b">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-700">Email</p>
              <p className="text-sm text-gray-900">{user?.email}</p>
            </div>
            <button
              onClick={() => setShowEmailModal(true)}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Change
            </button>
          </div>

          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="text-sm font-medium text-gray-700">Role</p>
              <span className={`inline-block mt-1 px-2 py-1 text-xs rounded-full ${
                user?.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                user?.role === 'user' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {user?.role?.charAt(0).toUpperCase() + user?.role?.slice(1)}
              </span>
            </div>
            <span className="text-gray-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </span>
          </div>

          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="text-sm font-medium text-gray-700">Account Status</p>
              <span className={`inline-block mt-1 px-2 py-1 text-xs rounded-full ${
                user?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {user?.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <span className="text-gray-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm font-medium text-gray-700">Member Since</p>
              <p className="text-sm text-gray-900">
                {new Date(user?.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>
            <span className="text-gray-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </span>
          </div>
        </div>
      </div>

      {/* Security Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Security</h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">Password</p>
              <p className="text-xs text-gray-500 mt-1">Change your password regularly to keep your account secure</p>
            </div>
            <button
              onClick={() => setShowPasswordModal(true)}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Change Password
            </button>
          </div>

          {user?.last_login && (
            <div className="pt-4 border-t">
              <p className="text-sm font-medium text-gray-700">Last Login</p>
              <p className="text-sm text-gray-900 mt-1">
                {new Date(user.last_login).toLocaleString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Login History Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Login History</h2>
        
        {loadingHistory ? (
          <div className="text-center py-8 text-gray-500">Loading history...</div>
        ) : loginHistory.length === 0 ? (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-gray-500 text-sm mt-4">No login history available</p>
          </div>
        ) : (
          <div className="space-y-3">
            {loginHistory.map((item, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <span className="text-2xl">{getActionIcon(item.action)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className={`text-sm font-medium ${getActionColor(item.action)}`}>
                      {item.action === 'login_success' ? 'Successful Login' :
                       item.action === 'login_failed' ? 'Failed Login Attempt' :
                       item.action === 'logout' ? 'Logout' : item.action}
                    </p>
                    <span className="text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-gray-600 space-y-1">
                    {item.ip_address && (
                      <div className="flex items-center">
                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                        </svg>
                        <span>IP: {item.ip_address}</span>
                      </div>
                    )}
                    {item.user_agent && (
                      <div className="flex items-start">
                        <svg className="w-3 h-3 mr-1 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <span className="truncate">{item.user_agent}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      {showPasswordModal && <PasswordChangeModal />}
      {showEmailModal && <EmailChangeModal />}
    </div>
  );
}
