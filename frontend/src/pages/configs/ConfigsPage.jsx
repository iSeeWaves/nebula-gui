import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function ConfigsPage() {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState(null);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      const response = await api.get('/configs/');
      setConfigs(response.data);
    } catch (error) {
      console.error('Failed to load configs:', error);
    } finally {
      setLoading(false);
    }
  };

  const activateConfig = async (configId) => {
    try {
      await api.post(`/configs/${configId}/activate`);
      await loadConfigs(); // Reload to show updated status
      alert('Configuration activated successfully!');
    } catch (error) {
      alert('Failed to activate configuration: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deactivateConfig = async (configId) => {
    if (!confirm('Are you sure you want to deactivate this configuration?')) return;
    
    try {
      await api.post(`/configs/${configId}/deactivate`);
      await loadConfigs(); // Reload to show updated status
      alert('Configuration deactivated successfully!');
    } catch (error) {
      alert('Failed to deactivate configuration: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteConfig = async (configId) => {
    if (!confirm('⚠️ Are you sure you want to delete this configuration?\n\nThis action cannot be undone.')) return;
    
    try {
      await api.delete(`/configs/${configId}`);
      await loadConfigs(); // Reload the list
      alert('✅ Configuration deleted successfully!');
    } catch (error) {
      alert('❌ Failed to delete configuration: ' + (error.response?.data?.detail || error.message));
    }
  };

  const viewConfig = (config) => {
    setSelectedConfig(config);
    setShowViewModal(true);
  };

  const CreateConfigForm = () => {
    const [name, setName] = useState('');
    const [configData, setConfigData] = useState(`pki:
  ca: /etc/nebula/ca.crt
  cert: /etc/nebula/host.crt
  key: /etc/nebula/host.key

static_host_map:
  "192.168.100.1": ["public-ip:4242"]

lighthouse:
  am_lighthouse: false
  interval: 60
  hosts:
    - "192.168.100.1"

listen:
  host: 0.0.0.0
  port: 4242

punchy:
  punch: true
  respond: true

tun:
  disabled: false
  dev: nebula1
  mtu: 1300
  drop_local_broadcast: false
  drop_multicast: false
  tx_queue: 500

logging:
  level: info
  format: text

firewall:
  conntrack:
    tcp_timeout: 12m
    udp_timeout: 3m
    default_timeout: 10m
  
  outbound:
    - port: any
      proto: any
      host: any
  
  inbound:
    - port: any
      proto: any
      host: any
`);
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault();
      setCreating(true);
      setError('');

      try {
        await api.post('/configs/', {
          name,
          config_data: configData
        });
        setShowCreateModal(false);
        await loadConfigs(); // Reload the list
        alert('✅ Configuration created successfully!');
      } catch (err) {
        let errorMessage = 'Failed to create configuration';
        
        if (err.response?.data?.detail) {
          if (Array.isArray(err.response.data.detail)) {
            errorMessage = err.response.data.detail.map(e => e.msg).join(', ');
          } else {
            errorMessage = err.response.data.detail;
          }
        }
        
        setError(errorMessage);
      } finally {
        setCreating(false);
      }
    };

    return (
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[70vh] overflow-y-auto">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
            {error}
          </div>
        )}
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Configuration Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            placeholder="my-nebula-config"
            required
          />
          <p className="text-xs text-gray-500 mt-1">A unique name for this configuration</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Configuration YAML
          </label>
          <textarea
            value={configData}
            onChange={(e) => setConfigData(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-xs text-gray-900"
            rows={20}
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Edit the YAML configuration. Make sure to update certificate paths and lighthouse settings.
          </p>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button
            type="button"
            onClick={() => setShowCreateModal(false)}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={creating}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {creating ? 'Creating...' : 'Create Configuration'}
          </button>
        </div>
      </form>
    );
  };

  if (loading) {
    return <div className="text-center py-8">Loading configurations...</div>;
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Configurations</h1>
          <p className="text-sm text-gray-600 mt-1">Manage Nebula VPN configurations</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Create Configuration
        </button>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-4 md:p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg md:text-xl font-bold mb-4 text-gray-900">Create Configuration</h2>
            <CreateConfigForm />
          </div>
        </div>
      )}

      {/* View Modal */}
      {showViewModal && selectedConfig && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-4 md:p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-lg md:text-xl font-bold text-gray-900">{selectedConfig.name}</h2>
                <span className={`inline-block mt-1 px-2 py-1 text-xs rounded-full ${
                  selectedConfig.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {selectedConfig.is_active ? '🟢 Active' : '⚪ Inactive'}
                </span>
              </div>
              <button
                onClick={() => setShowViewModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="bg-gray-900 rounded-lg p-4 mb-4">
              <pre className="text-xs font-mono whitespace-pre-wrap overflow-x-auto text-green-400">
                {selectedConfig.config_data}
              </pre>
            </div>

            <div className="flex flex-wrap gap-2 justify-end">
              {!selectedConfig.is_active ? (
                <button
                  onClick={async () => {
                    await activateConfig(selectedConfig.id);
                    setShowViewModal(false);
                  }}
                  className="px-4 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  ✓ Activate
                </button>
              ) : (
                <button
                  onClick={async () => {
                    await deactivateConfig(selectedConfig.id);
                    setShowViewModal(false);
                  }}
                  className="px-4 py-2 text-sm bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
                >
                  ⊗ Deactivate
                </button>
              )}
              <button
                onClick={() => {
                  navigator.clipboard.writeText(selectedConfig.config_data);
                  alert('✅ Configuration copied to clipboard!');
                }}
                className="px-4 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                📋 Copy
              </button>
              <button
                onClick={() => {
                  const blob = new Blob([selectedConfig.config_data], { type: 'text/yaml' });
                  const url = window.URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = `${selectedConfig.name}.yaml`;
                  link.click();
                }}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                ⬇ Download
              </button>
              <button
                onClick={() => setShowViewModal(false)}
                className="px-4 py-2 text-sm bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {configs.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-gray-500 text-sm md:text-base mt-4">
            No configurations yet. Create your first Nebula configuration to get started.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Created</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">Updated</th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {configs.map((config) => (
                  <tr key={config.id} className="hover:bg-gray-50">
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm font-medium text-gray-900">
                      {config.name}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        config.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {config.is_active ? '🟢 Active' : '⚪ Inactive'}
                      </span>
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm text-gray-500 hidden md:table-cell">
                      {new Date(config.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm text-gray-500 hidden lg:table-cell">
                      {new Date(config.updated_at).toLocaleDateString()}
                    </td>
                    <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm">
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => viewConfig(config)}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          View
                        </button>
                        {!config.is_active ? (
                          <button
                            onClick={() => activateConfig(config.id)}
                            className="text-green-600 hover:text-green-800 font-medium"
                          >
                            Activate
                          </button>
                        ) : (
                          <button
                            onClick={() => deactivateConfig(config.id)}
                            className="text-yellow-600 hover:text-yellow-800 font-medium"
                          >
                            Deactivate
                          </button>
                        )}
                        <button
                          onClick={() => deleteConfig(config.id)}
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
