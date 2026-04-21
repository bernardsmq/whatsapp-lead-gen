import { useState, useEffect } from 'react';
import api from '../lib/api';

export default function Debug() {
  const [status, setStatus] = useState({
    apiUrl: '',
    frontendUrl: '',
    token: '',
    healthCheck: null,
    leadsCheck: null,
    statsCheck: null,
    error: null,
  });

  useEffect(() => {
    const checkStatus = async () => {
      try {
        // Get API URL from axios instance
        const apiUrl = api.defaults.baseURL || 'not set';
        const token = localStorage.getItem('token');
        const frontendUrl = window.location.origin;

        setStatus(prev => ({ ...prev, apiUrl, token: token ? `${token.substring(0, 20)}...` : 'not set', frontendUrl }));

        // Test health endpoint
        try {
          const healthRes = await api.get('/health');
          setStatus(prev => ({ ...prev, healthCheck: { status: 200, data: healthRes.data } }));
        } catch (err) {
          setStatus(prev => ({ ...prev, healthCheck: { status: err.response?.status || 'error', error: err.message } }));
        }

        // Test /leads endpoint
        try {
          const leadsRes = await api.get('/leads');
          setStatus(prev => ({ ...prev, leadsCheck: { status: 200, count: leadsRes.data?.length || 0 } }));
        } catch (err) {
          setStatus(prev => ({ ...prev, leadsCheck: { status: err.response?.status || 'error', error: err.message } }));
        }

        // Test /dashboard/stats endpoint
        try {
          const statsRes = await api.get('/dashboard/stats');
          setStatus(prev => ({ ...prev, statsCheck: { status: 200, data: statsRes.data } }));
        } catch (err) {
          setStatus(prev => ({ ...prev, statsCheck: { status: err.response?.status || 'error', error: err.message } }));
        }
      } catch (err) {
        setStatus(prev => ({ ...prev, error: err.message }));
      }
    };

    checkStatus();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">🔧 Debug Status</h1>

        <div className="space-y-4">
          {/* Frontend URL */}
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <h2 className="text-lg font-semibold text-slate-300 mb-2">Frontend URL</h2>
            <p className="text-slate-400 font-mono break-all">{status.frontendUrl}</p>
          </div>

          {/* API URL */}
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <h2 className="text-lg font-semibold text-slate-300 mb-2">API Base URL</h2>
            <p className="text-slate-400 font-mono break-all">{status.apiUrl}</p>
          </div>

          {/* Token */}
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <h2 className="text-lg font-semibold text-slate-300 mb-2">Auth Token</h2>
            <p className="text-slate-400 font-mono">{status.token}</p>
          </div>

          {/* Health Check */}
          <div className={`rounded-lg p-4 border ${status.healthCheck?.status === 200 ? 'bg-green-900 border-green-700' : 'bg-red-900 border-red-700'}`}>
            <h2 className="text-lg font-semibold text-slate-300 mb-2">Health Check (/health)</h2>
            <p className={`font-mono text-sm ${status.healthCheck?.status === 200 ? 'text-green-300' : 'text-red-300'}`}>
              {status.healthCheck ? (
                <>
                  Status: {status.healthCheck.status}
                  {status.healthCheck.error && ` - ${status.healthCheck.error}`}
                  {status.healthCheck.data && ` - ${JSON.stringify(status.healthCheck.data)}`}
                </>
              ) : (
                'Checking...'
              )}
            </p>
          </div>

          {/* Leads Check */}
          <div className={`rounded-lg p-4 border ${status.leadsCheck?.status === 200 ? 'bg-green-900 border-green-700' : 'bg-red-900 border-red-700'}`}>
            <h2 className="text-lg font-semibold text-slate-300 mb-2">Leads Endpoint (GET /leads)</h2>
            <p className={`font-mono text-sm ${status.leadsCheck?.status === 200 ? 'text-green-300' : 'text-red-300'}`}>
              {status.leadsCheck ? (
                <>
                  Status: {status.leadsCheck.status}
                  {status.leadsCheck.error && ` - ${status.leadsCheck.error}`}
                  {status.leadsCheck.count !== undefined && ` - ${status.leadsCheck.count} leads found`}
                </>
              ) : (
                'Checking...'
              )}
            </p>
          </div>

          {/* Stats Check */}
          <div className={`rounded-lg p-4 border ${status.statsCheck?.status === 200 ? 'bg-green-900 border-green-700' : 'bg-red-900 border-red-700'}`}>
            <h2 className="text-lg font-semibold text-slate-300 mb-2">Stats Endpoint (GET /dashboard/stats)</h2>
            <p className={`font-mono text-sm ${status.statsCheck?.status === 200 ? 'text-green-300' : 'text-red-300'}`}>
              {status.statsCheck ? (
                <>
                  Status: {status.statsCheck.status}
                  {status.statsCheck.error && ` - ${status.statsCheck.error}`}
                  {status.statsCheck.data && ` - Success`}
                </>
              ) : (
                'Checking...'
              )}
            </p>
          </div>
        </div>

        <div className="mt-8 text-slate-400 text-sm">
          <p>💡 Open the browser console (F12) to see detailed request logs</p>
        </div>
      </div>
    </div>
  );
}
