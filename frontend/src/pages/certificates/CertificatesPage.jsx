import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function CertificatesPage() {
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSignModal, setShowSignModal] = useState(false);
  const [caList, setCaList] = useState([]);

  useEffect(() => {
    loadCertificates();
    loadCAs();
  }, []);

  const loadCertificates = async () => {
    try {
      const response = await api.get('/certificates/');
      setCertificates(response.data);
    } catch (error) {
      console.error('Failed to load certificates:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCAs = async () => {
    try {
      const response = await api.get('/certificates/ca/list');
      setCaList(response.data);
    } catch (error) {
      console.error('Failed to load CAs:', error);
    }
  };

  const downloadCertificate = async (certId, certName) => {
    try {
      const response = await api.get(`/certificates/${certId}/download?include_key=true`);
      
      const certBlob = new Blob([response.data.certificate], { type: 'text/plain' });
      const certUrl = window.URL.createObjectURL(certBlob);
      const certLink = document.createElement('a');
      certLink.href = certUrl;
      certLink.download = `${certName}.crt`;
      certLink.click();
      
      if (response.data.private_key) {
        const keyBlob = new Blob([response.data.private_key], { type: 'text/plain' });
        const keyUrl = window.URL.createObjectURL(keyBlob);
        const keyLink = document.createElement('a');
        keyLink.href = keyUrl;
        keyLink.download = `${certName}.key`;
        keyLink.click();
      }
    } catch (error) {
      alert('Failed to download certificate');
    }
  };

  const revokeCertificate = async (certId) => {
    if (!confirm('Are you sure you want to revoke this certificate?')) return;
    
    try {
      await api.delete(`/certificates/${certId}`);
      loadCertificates();
    } catch (error) {
      alert('Failed to revoke certificate');
    }
  };

  const CreateCAForm = () => {
    const [name, setName] = useState('');
    const [duration, setDuration] = useState('87600');
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault();
      setCreating(true);
      setError('');

      try {
        await api.post('/certificates/ca', {
          name,
          cert_type: 'ca',
          duration_hours: parseInt(duration)
        });
        setShowCreateModal(false);
        loadCertificates();
        loadCAs();
      } catch (err) {
        // Extract error message properly
        let errorMessage = 'Failed to create CA';
        
        if (err.response?.data?.detail) {
          if (Array.isArray(err.response.data.detail)) {
            // Pydantic validation errors
            errorMessage = err.response.data.detail.map(e => e.msg).join(', ');
          } else if (typeof err.response.data.detail === 'string') {
            errorMessage = err.response.data.detail;
          }
        }
        
        setError(errorMessage);
      } finally {
        setCreating(false);
      }
    };

    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
            {error}
          </div>
        )}
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">CA Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            placeholder="my-nebula-ca"
            required
          />
          <p className="text-xs text-gray-500 mt-1">Only alphanumeric, dots, dashes, and underscores allowed</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Duration (hours)</label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            required
          />
        </div>

        <div className="flex justify-end space-x-3">
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
            {creating ? 'Creating...' : 'Create CA'}
          </button>
        </div>
      </form>
    );
  };

  const SignCertificateForm = () => {
    const [name, setName] = useState('');
    const [caId, setCaId] = useState('');
    const [ipAddress, setIpAddress] = useState('');
    const [groups, setGroups] = useState('');
    const [duration, setDuration] = useState('87600');
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault();
      setCreating(true);
      setError('');

      try {
        const groupsArray = groups ? groups.split(',').map(g => g.trim()) : [];
        await api.post(`/certificates/sign?ca_id=${caId}`, {
          name,
          cert_type: 'host',
          ip_address: ipAddress,
          groups: groupsArray,
          duration_hours: parseInt(duration)
        });
        setShowSignModal(false);
        loadCertificates();
      } catch (err) {
        // Extract error message properly
        let errorMessage = 'Failed to sign certificate';
        
        if (err.response?.data?.detail) {
          if (Array.isArray(err.response.data.detail)) {
            // Pydantic validation errors - format nicely
            errorMessage = err.response.data.detail.map(e => {
              const field = e.loc?.join('.') || 'Field';
              return `${field}: ${e.msg}`;
            }).join('; ');
          } else if (typeof err.response.data.detail === 'string') {
            errorMessage = err.response.data.detail;
          }
        }
        
        setError(errorMessage);
        console.error('Validation error:', err.response?.data);
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
          <label className="block text-sm font-medium text-gray-700 mb-2">Certificate Authority</label>
          <select
            value={caId}
            onChange={(e) => setCaId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            required
          >
            <option value="">Select CA</option>
            {caList.map(ca => (
              <option key={ca.id} value={ca.id}>{ca.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Host Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            placeholder="server-01"
            required
          />
          <p className="text-xs text-gray-500 mt-1">Only alphanumeric, dots, dashes, and underscores allowed</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">IP Address (CIDR)</label>
          <input
            type="text"
            value={ipAddress}
            onChange={(e) => setIpAddress(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            placeholder="192.168.100.1/24"
            required
          />
          <p className="text-xs text-gray-500 mt-1">Format: IP/CIDR (e.g., 192.168.100.1/24)</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Groups (comma-separated)</label>
          <input
            type="text"
            value={groups}
            onChange={(e) => setGroups(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            placeholder="server, web, production"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Duration (hours)</label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            required
          />
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => setShowSignModal(false)}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={creating}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {creating ? 'Creating...' : 'Sign Certificate'}
          </button>
        </div>
      </form>
    );
  };

  if (loading) {
    return <div className="text-center py-8">Loading certificates...</div>;
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Certificates</h1>
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Create CA
          </button>
          <button
            onClick={() => setShowSignModal(true)}
            className="px-4 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
            disabled={caList.length === 0}
          >
            Sign Certificate
          </button>
        </div>
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-4 md:p-6 max-w-md w-full">
            <h2 className="text-lg md:text-xl font-bold mb-4">Create CA Certificate</h2>
            <CreateCAForm />
          </div>
        </div>
      )}

      {showSignModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-4 md:p-6 max-w-md w-full">
            <h2 className="text-lg md:text-xl font-bold mb-4">Sign Host Certificate</h2>
            <SignCertificateForm />
          </div>
        </div>
      )}

      {certificates.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 text-sm md:text-base">No certificates yet. Create a CA certificate to get started.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">IP</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Groups</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">Expires</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {certificates.map((cert) => (
                <tr key={cert.id}>
                  <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm font-medium text-gray-900">
                    {cert.name}
                  </td>
                  <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm">
                    <span className={`px-2 py-1 text-xs rounded ${
                      cert.is_ca ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {cert.is_ca ? 'CA' : cert.cert_type.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm text-gray-500 hidden sm:table-cell">
                    {cert.ip_address || '-'}
                  </td>
                  <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm text-gray-500 hidden md:table-cell">
                    {cert.groups || '-'}
                  </td>
                  <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm text-gray-500 hidden lg:table-cell">
                    {new Date(cert.expires_at).toLocaleDateString()}
                  </td>
                  <td className="px-3 md:px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      cert.revoked ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {cert.revoked ? 'Revoked' : 'Active'}
                    </span>
                  </td>
                  <td className="px-3 md:px-6 py-4 whitespace-nowrap text-xs md:text-sm space-x-2">
                    <button
                      onClick={() => downloadCertificate(cert.id, cert.name)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Download
                    </button>
                    {!cert.revoked && (
                      <button
                        onClick={() => revokeCertificate(cert.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Revoke
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
