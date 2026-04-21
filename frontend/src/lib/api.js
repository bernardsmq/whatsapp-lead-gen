import axios from 'axios';

// Determine API URL from environment or at runtime
let API_BASE_URL;

// First try to use the build-time environment variable
if (import.meta.env.VITE_API_URL) {
  API_BASE_URL = import.meta.env.VITE_API_URL;
  console.log('Using VITE_API_URL from environment:', API_BASE_URL);
} else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  // Local development fallback
  API_BASE_URL = 'http://localhost:8000';
  console.log('Using localhost API URL for development');
} else {
  // Production fallback - try to use same domain as frontend
  API_BASE_URL = window.location.origin;
  console.log('Using frontend origin as API URL:', API_BASE_URL);
}

console.log('API_BASE_URL:', API_BASE_URL, '| Hostname:', window.location.hostname);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-Client-Version': `${Date.now()}`, // Cache busting header
  },
  timeout: 30000, // 30 second timeout
});

// Add authentication token and enforce HTTPS
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Ensure HTTPS - upgrade http to https in baseURL
  if (config.baseURL && config.baseURL.startsWith('http://')) {
    const originalURL = config.baseURL;
    config.baseURL = config.baseURL.replace(/^http:\/\//, 'https://');
    console.log(`🔒 Upgraded baseURL from ${originalURL} to ${config.baseURL}`);
  }

  const fullURL = (config.baseURL || '') + (config.url || '');
  console.log(`📡 ${config.method?.toUpperCase()} ${fullURL}`);

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
