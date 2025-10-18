import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function ClientSetupPage() {
  const { user } = useAuth(); // Now using it properly
  const [caList, setCaList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [provisionToken, setProvisionToken] = useState(null);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    device_name: '',
    device_type: 'linux',
    ca_id: '',
    ip_address: '',
    auto_connect: true
  });

  useEffect(() => {
    fetchCAs();
  }, []);

  const fetchCAs = async () => {
    try {
      const response = await api.get('/certificates/ca/list');
      setCaList(response.data);
      if (response.data.length > 0) {
        setFormData(prev => ({ ...prev, ca_id: response.data[0].id }));
      }
    } catch (error) {
      console.error('Error fetching CAs:', error);
      setError('Failed to load CA certificates');
    }
  };

  const handleProvision = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/client-setup/provision', formData);
      setProvisionToken(response.data);
    } catch (error) {
      console.error('Provision error:', error);
      setError(error.response?.data?.detail || 'Failed to provision device');
    } finally {
      setLoading(false);
    }
  };

  const downloadClient = () => {
    if (!provisionToken) return;
    
    const downloadUrl = `${api.defaults.baseURL}/client-setup/download/${provisionToken.token}`;
    window.open(downloadUrl, '_blank');
  };

  const showQRCode = () => {
    if (!provisionToken) return;
    
    const qrUrl = `${api.defaults.baseURL}/client-setup/qr-code/${provisionToken.token}`;
    window.open(qrUrl, '_blank', 'width=500,height=500');
  };

  const resetForm = () => {
    setProvisionToken(null);
    setError('');
    setFormData({
      device_name: '',
      device_type: 'linux',
      ca_id: caList[0]?.id || '',
      ip_address: '',
      auto_connect: true
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🚀 One-Click Client Setup
        </h1>
        <p className="text-gray-600">
          Generate pre-configured client packages for easy device provisioning
        </p>
        {user && (
          <p className="text-sm text-gray-500 mt-1">
            Logged in as: <strong>{user.username}</strong>
            {user.is_admin && <span className="ml-2 text-purple-600">(Admin)</span>}
          </p>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
          <div className="flex items-center">
            <span className="text-xl mr-2">⚠️</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {!provisionToken ? (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">Provision New Device</h2>
          
          {caList.length === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg">
              <p className="font-medium">⚠️ No CA Certificates Found</p>
              <p className="text-sm mt-1">
                Please create a CA certificate first in the <a href="/certificates" className="underline font-medium">Certificates</a> page.
              </p>
            </div>
          ) : (
            <form onSubmit={handleProvision} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Device Name *
                </label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="johns-laptop"
                  value={formData.device_name}
                  onChange={(e) => setFormData({...formData, device_name: e.target.value})}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use a descriptive name like "johns-laptop" or "office-desktop"
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Device Type *
                </label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={formData.device_type}
                  onChange={(e) => setFormData({...formData, device_type: e.target.value})}
                >
                  <option value="linux">🐧 Linux</option>
                  <option value="macos">🍎 macOS</option>
                  <option value="windows">🪟 Windows</option>
                  <option value="android" disabled>📱 Android (Coming Soon)</option>
                  <option value="ios" disabled>📱 iOS (Coming Soon)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Certificate Authority *
                </label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={formData.ca_id}
                  onChange={(e) => setFormData({...formData, ca_id: e.target.value})}
                  required
                >
                  <option value="">Select CA</option>
                  {caList.map(ca => (
                    <option key={ca.id} value={ca.id}>
                      {ca.name} (expires: {new Date(ca.expires_at).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  IP Address (Optional)
                </label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="192.168.100.X/24 (leave empty for auto-assign)"
                  value={formData.ip_address}
                  onChange={(e) => setFormData({...formData, ip_address: e.target.value})}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty to auto-assign the next available IP
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="auto_connect"
                  checked={formData.auto_connect}
                  onChange={(e) => setFormData({...formData, auto_connect: e.target.checked})}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="auto_connect" className="ml-2 text-sm text-gray-700">
                  Auto-connect VPN on device startup
                </label>
              </div>

              <button
                type="submit"
                disabled={loading || caList.length === 0}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </span>
                ) : (
                  '🎯 Generate Client Package'
                )}
              </button>
            </form>
          )}
        </div>
      ) : (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-lg p-6 shadow-md">
          <div className="flex items-center mb-4">
            <div className="bg-green-500 text-white rounded-full w-10 h-10 flex items-center justify-center mr-3 flex-shrink-0">
              ✓
            </div>
            <h3 className="text-xl font-semibold text-green-800">
              Client Package Ready!
            </h3>
          </div>
          
          <div className="bg-white rounded-lg p-4 mb-4 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Device:</span>
              <span className="text-sm text-purple-700 font-semibold">{provisionToken.device_name}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Expires:</span>
              <span className="text-sm font-semibold text-purple-700">
                {new Date(provisionToken.expires_at).toLocaleString()}
              </span>
            </div>
            <div className="border-t pt-2 mt-2">
              <span className="text-xs text-gray-500">Token:</span>
              <code className="block text-xs font-mono bg-gray-700 px-2 py-1 rounded mt-1 break-all">
                {provisionToken.token}
              </code>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-3 mb-4">
            <button
              onClick={downloadClient}
              className="bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 transition-colors font-medium shadow-sm flex items-center justify-center"
            >
              <span className="mr-2">📥</span>
              Download Package
            </button>
            
            <button
              onClick={showQRCode}
              className="bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm flex items-center justify-center"
            >
              <span className="mr-2">📱</span>
              Show QR Code
            </button>
          </div>

          <button
            onClick={resetForm}
            className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors font-medium"
          >
            ➕ Provision Another Device
          </button>
        </div>
      )}

      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center">
          <span className="mr-2">📖</span> How It Works
        </h3>
        <ol className="space-y-3">
          <li className="flex items-start">
            <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">1</span>
            <div>
              <strong className="text-blue-900">Generate Package</strong>
              <p className="text-sm text-gray-700">Fill in device details and click "Generate Client Package"</p>
            </div>
          </li>
          <li className="flex items-start">
            <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">2</span>
            <div>
              <strong className="text-blue-900">Download</strong>
              <p className="text-sm text-gray-700">Download the generated ZIP file to your device</p>
            </div>
          </li>
          <li className="flex items-start">
            <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">3</span>
            <div>
              <strong className="text-blue-900">Install</strong>
              <p className="text-sm text-gray-700">Extract and run the installation script (install.sh or install.bat)</p>
            </div>
          </li>
          <li className="flex items-start">
            <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">4</span>
            <div>
              <strong className="text-blue-900">Connected!</strong>
              <p className="text-sm text-gray-700">Device automatically connects to VPN - no manual configuration needed!</p>
            </div>
          </li>
        </ol>
      </div>

      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-yellow-900 mb-2 flex items-center">
          <span className="mr-2">⚠️</span> Important Notes
        </h4>
        <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
          <li>Installation script requires administrator/root privileges</li>
          <li>Provisioning token expires after 24 hours</li>
          <li>Keep the private key secure - never share it</li>
          <li>For mobile devices, use QR code provisioning</li>
        </ul>
      </div>
    </div>
  );
}
