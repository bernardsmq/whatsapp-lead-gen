import { useState, useEffect, useCallback } from 'react';
import { leadsAPI, dashboardAPI } from '../lib/api';

export const useLeads = (status = null, score = null) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchLeads = useCallback(async () => {
    setError(null);
    try {
      const response = await leadsAPI.getAll(status, score);
      setLeads(response.data || []);
      setLoading(false);
    } catch (err) {
      console.error('❌ Leads API error:', err.response?.status || err.message);

      if (err.response?.status === 401) {
        setError('Not authenticated');
        setTimeout(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('user_id');
          window.location.href = '/login';
        }, 1000);
      } else {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch leads');
      }
      setLoading(false);
    }
  }, [status, score]);

  useEffect(() => {
    setLoading(true);
    fetchLeads();

    // Poll for new leads every 4 seconds
    const interval = setInterval(fetchLeads, 4000);

    return () => clearInterval(interval);
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
      try {
        const response = await leadsAPI.getById(leadId);
        setLead(response.data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch lead');
      } finally {
        setLoading(false);
      }
    };

    setLoading(true);
    fetchLead();

    // Poll for updates every 3 seconds
    const interval = setInterval(fetchLead, 3000);

    return () => clearInterval(interval);
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
      try {
        const response = await leadsAPI.getConversations(leadId);
        setConversations(response.data || []);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch conversations');
      } finally {
        setLoading(false);
      }
    };

    setLoading(true);
    fetchConversations();

    // Poll for new messages every 2 seconds
    const interval = setInterval(fetchConversations, 2000);

    return () => clearInterval(interval);
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
