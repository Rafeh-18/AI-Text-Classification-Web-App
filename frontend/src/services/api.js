import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  // Fixed: don't override if header already set (e.g. the me(token) call right after login)
  if (!config.headers.Authorization) {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),

  // Fixed: renamed getMe → me to match usage in Login/Register.
  // Accepts an optional token for the post-login call, before the token
  // is stored in localStorage (so the interceptor can't attach it yet).
  me: (token) => api.get('/auth/me', token
    ? { headers: { Authorization: `Bearer ${token}` } }
    : {}
  ),
};

export const predictAPI = {
  classify: (text) => api.post('/predict/', { text }),
  getHistory: (params) => api.get('/predict/history', { params }),
  deletePrediction: (id) => api.delete(`/predict/history/${id}`),
};

export default api;