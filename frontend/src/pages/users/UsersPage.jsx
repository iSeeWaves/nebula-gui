import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    loadUsers();
    loadStats();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await api.get('/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to load users:', error);
      if (error.response?.status === 403) {
        alert('You do not have permission to view users. Admin access required.');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/users/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const toggleUserActive = async (userId) => {
    try {
      await api.post(`/users/${userId}/toggle-active`);
      loadUsers();
      alert('User status updated successfully!');
    } catch (error) {
      alert('Failed to update user status: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteUser = async (userId) => {
    if (!confirm('⚠️ Are you sure you want to delete this user?\n\nThis action cannot be undone.')) return;
    
    try {
      await api.delete(`/users/${userId}`);
      loadUsers();
      loadStats();
      alert('✅ User deleted successfully!');
    } catch (error) {
      alert('❌ Failed to delete user: ' + (error.response?.data?.detail || error.message));
    }
  };

  const editUser = (user) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const EditUserModal = () => {
    const [email, setEmail] = useState(selectedUser?.email || '');
    const [role, setRole] = useState(selectedUser?.role || 'user');
    const [isActive, setIsActive] = useState(selectedUser?.is_active || true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault();
      setSaving(true);
      setError('');

      try {
        await api.put(`/users/${selectedUser.id}`, {
          email,
          role,
          is_active: isActive
        });
        setShowEditModal(false);
        loadUsers();
        loadStats();
        alert('✅ User updated successfully!');
      } catch (err) {
        let errorMessage = 'Failed to update user';
        if (err.response?.data?.detail) {
          if (Array.isArray(err.response.data.detail)) {
            errorMessage = err.response.data.detail.map(e => e.msg).join(', ');
          } else {
            errorMessage = err.response.data.detail;
          }
        }
        setError(errorMessage);
      } finally {
        setSaving(false);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg p-4 md:p-6 max-w-md w-full">
          <h2 className="text-lg md:text-xl font-bold mb-4 text-gray-900">Edit User: {selectedUser?.username}</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="viewer">Viewer - Can only view</option>
                <option value="user">User - Can create/manage own resources</option>
                <option value="admin">Admin - Full access</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Active (user can login)
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={() => setShowEditModal(false)}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const getRoleBadge = (role) => {
    const colors = {
      admin: 'bg-purple-100 text-purple-800',
      user: 'bg-blue-100 text-blue-800',
      viewer: 'bg-gray-100 text-gray-800'
    };
    return (
      <span className={`px-2 py-1 text-xs rounded-full ${colors[role] || colors.viewer}`}>
        {role.charAt(0).toUpperCase() + role.slice(1)}
      </span>
    );
  };

  if (loading) {
    return <div className="text-center py-8">Loading users...</div>;
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">User Management</h1>
          <p className="text-sm text-gray-600 mt-1">Manage system users and permissions</p>
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-green-600">{stats.active_users}</p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Admins</p>
                <p className="text-2xl font-bold text-purple-600">{stats.admin_users}</p>
              </div>
              <div className="bg-purple-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Recent Signups</p>
                <p className="text-2xl font-bold text-orange-600">{stats.recent_signups}</p>
              </div>
              <div className="bg-orange-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && selectedUser && <EditUserModal />}

      {/* Users Table */}
      {users.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">No users found.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Email</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">Last Login</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm font-medium text-gray-900">
                      {user.username}
                      {user.is_admin && (
                        <span className="ml-2 px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded-full">
                          Admin
                        </span>
                      )}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm text-gray-500 hidden md:table-cell">
                      {user.email}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap">
                      {getRoleBadge(user.role)}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        user.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? '🟢 Active' : '🔴 Inactive'}
                      </span>
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm text-gray-500 hidden lg:table-cell">
                      {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm">
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => editUser(user)}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => toggleUserActive(user.id)}
                          className="text-yellow-600 hover:text-yellow-800 font-medium"
                        >
                          {user.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                        <button
                          onClick={() => deleteUser(user.id)}
                          className="text-red-600 hover:text-red-800 font-medium"
                        >
                          Delete
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
    </div>
  );
}
