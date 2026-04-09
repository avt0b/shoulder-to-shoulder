const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const token = localStorage.getItem('token');

  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || data.message || `Ошибка сервера: ${response.status}`);
  }

  if (response.status === 204) return null;

  return response.json();
}

export const authApi = {
  /** POST /api/v1/auth/register */
  register(data) {
    return request('/api/v1/auth/register', {
      method: 'POST',
      body: data,
    });
  },

  /** POST /api/v1/auth/login */
  login(data) {
    return request('/api/v1/auth/login', {
      method: 'POST',
      body: data,
    });
  },

  /** POST /api/v1/auth/forgot-password/send-code */
  sendResetCode(data) {
    return request('/api/v1/auth/forgot-password/send-code', {
      method: 'POST',
      body: data,
    });
  },

  /** POST /api/v1/auth/forgot-password/reset */
  resetPassword(data) {
    return request('/api/v1/auth/forgot-password/reset', {
      method: 'POST',
      body: data,
    });
  },
};
