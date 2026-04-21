import axios from 'axios';

let API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('Raw VITE_API_URL:', API_BASE_URL);

// Ensure HTTPS for production - be explicit about it
if (API_BASE_URL.includes('railway.app')) {
  // Remove any http:// prefix and force https://
  API_BASE_URL = API_BASE_URL.replace(/^https?:\/\//, 'https://');
}

// Final verification
if (!API_BASE_URL.startsWith('http')) {
  API_BASE_URL = 'https://' + API_BASE_URL;
}

console.log('Final API_BASE_URL:', API_BASE_URL);
console.log('VITE_API_URL env:', import.meta.env.VITE_API_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Force HTTPS in all requests
  validateStatus: () => true, // Don't throw on any status
});

console.log('Axios baseURL:', api.defaults.baseURL);

// Add token to requests and FORCE HTTPS
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // CRITICAL: Force HTTPS for all railway.app requests
  // This must be done BEFORE axios constructs the final URL
  if (config.baseURL && config.baseURL.includes('railway.app')) {
    config.baseURL = config.baseURL.replace(/^http:\/\//, 'https://');
  }

  // Also ensure the URL itself is HTTPS if it's absolute
  if (config.url && config.url.startsWith('http://') && config.url.includes('railway.app')) {
    config.url = config.url.replace(/^http:\/\//, 'https://');
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
