import axios from 'axios';

// Automatically normalize URL so both 'https://app.onrender.com' and 'https://app.onrender.com/api/v1' work
function getBaseApiUrl(): string {
  let raw = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  raw = raw.trim().replace(/\/+$/, '');
  if (!raw.endsWith('/api/v1')) {
    raw = `${raw}/api/v1`;
  }
  return raw;
}

export const api = axios.create({
  baseURL: getBaseApiUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to requests if in browser
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('codevita_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Interceptor for 401 Unauthorized handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Clear token and redirect to login if session expired
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        localStorage.removeItem('codevita_token');
        localStorage.removeItem('codevita_user');
      }
    }
    return Promise.reject(error);
  }
);
