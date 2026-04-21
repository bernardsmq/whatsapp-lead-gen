import { useState, useEffect } from 'react';
import { analyticsAPI } from '../lib/api';

export const useAnalytics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await analyticsAPI.getStats();
        setStats(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch analytics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  return { stats, loading, error };
};

export const useMessagesByDate = (dateStr) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!dateStr) return;

    const fetchMessages = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await analyticsAPI.getMessagesByDate(dateStr);
        setMessages(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch messages');
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
  }, [dateStr]);

  return { messages, loading, error };
};

export const useRecentActivity = (limit = 20) => {
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchActivity = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await analyticsAPI.getRecentActivity(limit);
        setActivity(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch activity');
      } finally {
        setLoading(false);
      }
    };

    fetchActivity();
    const interval = setInterval(fetchActivity, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, [limit]);

  return { activity, loading, error };
};
