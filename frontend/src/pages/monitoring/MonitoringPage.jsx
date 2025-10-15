import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function MonitoringPage() {
  const [systemStats, setSystemStats] = useState(null);
  const [networkStats, setNetworkStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // 30 seconds default

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, refreshInterval * 1000);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const loadStats = async () => {
    try {
      const [system, network] = await Promise.all([
        api.get('/monitoring/system'),
        api.get('/monitoring/network')
      ]);
      setSystemStats(system.data);
      setNetworkStats(network.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (loading) {
    return <div className="text-center py-8">Loading monitoring data...</div>;
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">System Monitoring</h1>
        <div className="flex items-center space-x-4">
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value={10}>Refresh every 10s</option>
            <option value={30}>Refresh every 30s</option>
            <option value={60}>Refresh every 60s</option>
            <option value={300}>Refresh every 5min</option>
          </select>
          <button
            onClick={loadStats}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
          >
            Refresh Now
          </button>
        </div>
      </div>

      {/* System Stats */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">System Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">CPU Usage</h3>
            <div className="flex items-end space-x-2">
              <p className="text-3xl font-bold text-blue-600">
                {systemStats?.cpu_percent.toFixed(1)}%
              </p>
            </div>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${systemStats?.cpu_percent}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Memory Usage</h3>
            <div className="flex items-end space-x-2">
              <p className="text-3xl font-bold text-green-600">
                {systemStats?.memory_percent.toFixed(1)}%
              </p>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {systemStats?.memory_used_mb.toFixed(0)} / {systemStats?.memory_total_mb.toFixed(0)} MB
            </p>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${systemStats?.memory_percent}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Disk Usage</h3>
            <div className="flex items-end space-x-2">
              <p className="text-3xl font-bold text-yellow-600">
                {systemStats?.disk_percent.toFixed(1)}%
              </p>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {systemStats?.disk_used_gb.toFixed(1)} / {systemStats?.disk_total_gb.toFixed(1)} GB
            </p>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-yellow-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${systemStats?.disk_percent}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">System Uptime</h3>
            <p className="text-3xl font-bold text-purple-600">
              {Math.floor(systemStats?.uptime_seconds / 3600)}h
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {Math.floor((systemStats?.uptime_seconds % 3600) / 60)}m
            </p>
          </div>
        </div>
      </div>

      {/* Network Stats */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Network Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Data Transfer</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Bytes Sent</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatBytes(networkStats?.bytes_sent)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Bytes Received</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatBytes(networkStats?.bytes_recv)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Packets & Errors</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Packets Sent</p>
                <p className="text-lg font-semibold text-gray-900">
                  {networkStats?.packets_sent.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Packets Received</p>
                <p className="text-lg font-semibold text-gray-900">
                  {networkStats?.packets_recv.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Errors In</p>
                <p className="text-lg font-semibold text-red-600">
                  {networkStats?.errors_in}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Errors Out</p>
                <p className="text-lg font-semibold text-red-600">
                  {networkStats?.errors_out}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Drops In</p>
                <p className="text-lg font-semibold text-orange-600">
                  {networkStats?.drops_in}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Drops Out</p>
                <p className="text-lg font-semibold text-orange-600">
                  {networkStats?.drops_out}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
