import axios from 'axios';

// Determine API URL at runtime based on current hostname
let API_BASE_URL;

if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  // Local development
  API_BASE_URL = 'http://localhost:8000';
} else {
  // Production - always use HTTPS
  API_BASE_URL = 'https://whatsapp-lead-gen-production.up.railway.app';
}

console.log('API_BASE_URL:', API_BASE_URL, '| Hostname:', window.location.hostname);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// NUCLEAR: Force HTTPS on every single request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Replace HTTP with HTTPS in baseURL
  if (config.baseURL) {
    config.baseURL = config.baseURL.replace(/^http:\/\//, 'https://');
  }

  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Only redirect if not already on login page
      const isLoginPage = window.location.pathname === '/login';
      if (!isLoginPage) {
        console.warn('⚠️ 401 Unauthorized - Clearing token and redirecting to login');
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        setTimeout(() => {
          window.location.href = '/login';
        }, 500);
      }
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
