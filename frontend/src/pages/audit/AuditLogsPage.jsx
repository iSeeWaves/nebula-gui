import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    action: '',
    resource_type: '',
    status: ''
  });

  useEffect(() => {
    loadLogs();
    loadStats();
  }, []);

  const loadLogs = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.action) params.append('action', filters.action);
      if (filters.resource_type) params.append('resource_type', filters.resource_type);
      if (filters.status) params.append('status', filters.status);

      const response = await api.get(`/audit/logs?${params.toString()}`);
      setLogs(response.data);
    } catch (error) {
      console.error('Failed to load logs:', error);
      if (error.response?.status === 403) {
        alert('You do not have permission to view audit logs. Admin access required.');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/audit/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const applyFilters = () => {
    setLoading(true);
    loadLogs();
  };

  const clearFilters = () => {
    setFilters({ action: '', resource_type: '', status: '' });
    setLoading(true);
    setTimeout(() => loadLogs(), 100);
  };

  const getActionColor = (action) => {
    if (action.includes('login')) return 'text-blue-600';
    if (action.includes('create')) return 'text-green-600';
    if (action.includes('delete') || action.includes('revoke')) return 'text-red-600';
    if (action.includes('update') || action.includes('activate')) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getStatusBadge = (status) => {
    if (status === 'success') {
      return <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Success</span>;
    }
    return <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">Failed</span>;
  };

  if (loading) {
    return <div className="text-center py-8">Loading audit logs...</div>;
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Audit Logs</h1>
          <p className="text-sm text-gray-600 mt-1">Track all system activities and user actions</p>
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Logs</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_logs}</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Failed Actions</p>
                <p className="text-2xl font-bold text-red-600">{stats.failed_actions}</p>
              </div>
              <div className="bg-red-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Last 24 Hours</p>
                <p className="text-2xl font-bold text-green-600">{stats.recent_activity_24h}</p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <select
            value={filters.action}
            onChange={(e) => setFilters({ ...filters, action: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Actions</option>
            <option value="login_success">Login Success</option>
            <option value="login_failed">Login Failed</option>
            <option value="user_signup">User Signup</option>
            <option value="logout">Logout</option>
          </select>

          <select
            value={filters.resource_type}
            onChange={(e) => setFilters({ ...filters, resource_type: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Resources</option>
            <option value="auth">Authentication</option>
            <option value="user">Users</option>
            <option value="certificate">Certificates</option>
            <option value="config">Configurations</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Status</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>

          <div className="flex gap-2">
            <button
              onClick={applyFilters}
              className="flex-1 px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Apply
            </button>
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      {logs.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">No audit logs found.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Resource</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">IP Address</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {log.username}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`font-medium ${getActionColor(log.action)}`}>
                        {log.action.replace(/_/g, ' ')}
                      </span>
                      {log.resource_name && (
                        <div className="text-xs text-gray-500">
                          {log.resource_name}
                        </div>
                      )}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">
                      {log.resource_type}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs text-gray-500 hidden lg:table-cell">
                      {log.ip_address || '-'}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(log.status)}
                      {log.error_message && (
                        <div className="text-xs text-red-600 mt-1">
                          {log.error_message}
                        </div>
                      )}
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
