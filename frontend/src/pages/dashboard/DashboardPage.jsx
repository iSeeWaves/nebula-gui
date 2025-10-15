import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await api.get('/monitoring/system');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <div className="bg-white rounded-lg shadow p-4 md:p-6">
          <h3 className="text-xs md:text-sm font-medium text-gray-500 mb-2">CPU Usage</h3>
          <p className="text-2xl md:text-3xl font-bold text-blue-600">{stats?.cpu_percent.toFixed(1)}%</p>
        </div>

        <div className="bg-white rounded-lg shadow p-4 md:p-6">
          <h3 className="text-xs md:text-sm font-medium text-gray-500 mb-2">Memory Usage</h3>
          <p className="text-2xl md:text-3xl font-bold text-green-600">{stats?.memory_percent.toFixed(1)}%</p>
        </div>

        <div className="bg-white rounded-lg shadow p-4 md:p-6">
          <h3 className="text-xs md:text-sm font-medium text-gray-500 mb-2">Disk Usage</h3>
          <p className="text-2xl md:text-3xl font-bold text-yellow-600">{stats?.disk_percent.toFixed(1)}%</p>
        </div>

        <div className="bg-white rounded-lg shadow p-4 md:p-6">
          <h3 className="text-xs md:text-sm font-medium text-gray-500 mb-2">Uptime</h3>
          <p className="text-2xl md:text-3xl font-bold text-purple-600">
            {Math.floor(stats?.uptime_seconds / 3600)}h
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-4 md:p-6">
        <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-4">System Information</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs md:text-sm text-gray-500">Total Memory</p>
            <p className="text-base md:text-lg font-medium text-gray-900">{stats?.memory_total_mb.toFixed(0)} MB</p>
          </div>
          <div>
            <p className="text-xs md:text-sm text-gray-500">Used Memory</p>
            <p className="text-base md:text-lg font-medium text-gray-900">{stats?.memory_used_mb.toFixed(0)} MB</p>
          </div>
          <div>
            <p className="text-xs md:text-sm text-gray-500">Total Disk</p>
            <p className="text-base md:text-lg font-medium text-gray-900">{stats?.disk_total_gb.toFixed(1)} GB</p>
          </div>
          <div>
            <p className="text-xs md:text-sm text-gray-500">Used Disk</p>
            <p className="text-base md:text-lg font-medium text-gray-900">{stats?.disk_used_gb.toFixed(1)} GB</p>
          </div>
        </div>
      </div>
    </div>
  );
}
