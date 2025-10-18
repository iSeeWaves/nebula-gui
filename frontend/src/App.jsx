import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Layout from './components/layout/Layout';
import LoginPage from './pages/login/LoginPage';
import SignupPage from './pages/login/SignupPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import CertificatesPage from './pages/certificates/CertificatesPage';
import ConfigsPage from './pages/configs/ConfigsPage';
import MonitoringPage from './pages/monitoring/MonitoringPage';
import AuditLogsPage from './pages/audit/AuditLogsPage';
import UsersPage from './pages/users/UsersPage';
import ProfilePage from './pages/profile/ProfilePage';
import ClientSetupPage from './pages/ClientSetupPage';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          
          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/certificates"
            element={
              <ProtectedRoute>
                <Layout>
                  <CertificatesPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/configs"
            element={
              <ProtectedRoute>
                <Layout>
                  <ConfigsPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/monitoring"
            element={
              <ProtectedRoute>
                <Layout>
                  <MonitoringPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProfilePage />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          {/* Client Setup Route - NEW */}
          <Route
            path="/client-setup"
            element={
              <ProtectedRoute>
                <Layout>
                  <ClientSetupPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          {/* Admin-Only Routes */}
          <Route
            path="/users"
            element={
              <ProtectedRoute requireAdmin={true}>
                <Layout>
                  <UsersPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/audit"
            element={
              <ProtectedRoute requireAdmin={true}>
                <Layout>
                  <AuditLogsPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          {/* Default Redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
