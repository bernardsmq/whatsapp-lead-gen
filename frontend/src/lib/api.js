import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (email, password, name, role) => api.post('/auth/register', { email, password, name, role }),
  me: () => api.get('/auth/me'),
};

export const leadsAPI = {
  getAll: (status, score) => api.get('/leads', { params: { status_filter: status, score_filter: score } }),
  getById: (id) => api.get(`/leads/${id}`),
  getConversations: (id) => api.get(`/leads/${id}/conversations`),
  updateQualification: (id, data) => api.post(`/leads/${id}/qualification`, data),
};

export const sheetsAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/sheets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getBatches: () => api.get('/sheets/batches'),
};

export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
};

export const analyticsAPI = {
  getStats: () => api.get('/analytics/stats'),
  getMessagesByDate: (date) => api.get('/analytics/messages/by-date', { params: { date_str: date } }),
  getRecentActivity: (limit = 20) => api.get('/analytics/activity/recent', { params: { limit } }),
};

export default api;
