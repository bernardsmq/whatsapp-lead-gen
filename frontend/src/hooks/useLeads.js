import { useState, useEffect, useCallback } from 'react';
import { leadsAPI, dashboardAPI } from '../lib/api';

export const useLeads = (status = null, score = null) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('📥 Fetching leads with status:', status, 'score:', score);
      const response = await leadsAPI.getAll(status, score);
      console.log('✅ Leads response:', response);
      console.log('   Data:', response.data);
      setLeads(response.data || []);
    } catch (err) {
      console.error('❌ Leads API error:', err);
      console.error('   Status:', err.response?.status);
      console.error('   Data:', err.response?.data);
      console.error('   Message:', err.message);
      console.error('   Full error:', err);

      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch leads';

      // Log full error for debugging
      if (err.response?.status === 401) {
        console.error('✗ 401 Unauthorized - Token may not be in localStorage');
        const token = localStorage.getItem('token');
        console.error('  Token in storage:', token ? `${token.substring(0, 20)}...` : 'NULL');
        setError('Not authenticated. Clearing cache and redirecting...');
        // Clear and redirect after a short delay
        setTimeout(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('user_id');
          window.location.href = '/login';
        }, 1000);
      } else if (err.response?.status === 403) {
        setError('Access denied');
      } else if (err.response?.status === 307) {
        console.error('⚠️ Got 307 Redirect - endpoint returning redirect instead of data');
        setError('Server error: endpoint redirecting');
      } else {
        setError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  }, [status, score]);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  return { leads, loading, error, refetch: fetchLeads };
};

export const useLead = (leadId) => {
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!leadId) return;

    const fetchLead = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await leadsAPI.getById(leadId);
        setLead(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch lead');
      } finally {
        setLoading(false);
      }
    };

    fetchLead();
  }, [leadId]);

  return { lead, loading, error };
};

export const useConversations = (leadId) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!leadId) return;

    const fetchConversations = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await leadsAPI.getConversations(leadId);
        setConversations(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch conversations');
      } finally {
        setLoading(false);
      }
    };

    fetchConversations();
  }, [leadId]);

  return { conversations, loading, error };
};

export const useDashboardStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await dashboardAPI.getStats();
        setStats(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch stats');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  return { stats, loading, error };
};
