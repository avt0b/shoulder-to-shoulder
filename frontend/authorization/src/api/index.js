const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Переключи на true для использования mock-данных
const USE_MOCK = false;

function normalizePhone(phone) {
  const cleaned = phone.replace(/[\s\-\(\)]/g, '');
  if (cleaned.startsWith('+')) return cleaned;
  if (cleaned.startsWith('8') && cleaned.length === 11) return '+7' + cleaned.slice(1);
  if (cleaned.startsWith('7') && cleaned.length === 11) return '+' + cleaned;
  if (cleaned.length === 10) return '+7' + cleaned;
  return '+' + cleaned;
}

// ===== Mock helpers =====
const delay = (ms = 500) => new Promise(r => setTimeout(r, ms));

function mockLogin(data) {
  return delay().then(() => {
    if (data.login === 'test' || data.password === 'test') {
      throw new Error('Неверный логин или пароль');
    }
    return {
      access_token: 'mock-jwt-token-' + Date.now(),
      refresh_token: 'mock-refresh-token',
      user: { login: data.login, display_name: data.login },
    };
  });
}

function mockRegister(data) {
  return delay(800).then(() => {
    if (data.password !== data.confirmPassword) {
      throw new Error('Пароли не совпадают');
    }
    return { message: 'Регистрация успешна' };
  });
}

function mockSendResetCode(data) {
  return delay().then(() => {
    if (!data.contact) {
      throw new Error('Введите номер телефона или Email');
    }
    return { message: 'Код отправлен', code: '123456' };
  });
}

function mockResetPassword(data) {
  return delay(800).then(() => {
    if (data.code !== '123456') {
      throw new Error('Неверный код');
    }
    if (data.new_password !== data.confirmPassword) {
      throw new Error('Пароли не совпадают');
    }
    return { message: 'Пароль изменён' };
  });
}

// ===== Real API =====
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
    const detail = data.detail || data.message;
    const errorMessage = extractErrorMessage(detail) || `Ошибка сервера: ${response.status}`;
    throw new Error(errorMessage);
  }

  if (response.status === 204) return null;

  return response.json();
}

function extractErrorMessage(detail) {
  if (!detail) return null;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map(item => extractErrorMessage(item)).filter(Boolean).join('. ');
  }
  if (typeof detail === 'object') {
    return Object.entries(detail)
      .map(([key, value]) => {
        const msg = extractErrorMessage(value);
        return msg ? `${key}: ${msg}` : null;
      })
      .filter(Boolean)
      .join('. ');
  }
  return String(detail);
}

// ===== Export =====
export const authApi = USE_MOCK
  ? {
      register(data) {
        return mockRegister(data);
      },
      login(data) {
        return mockLogin(data);
      },
      sendResetCode(data) {
        return mockSendResetCode(data);
      },
      resetPassword(data) {
        return mockResetPassword(data);
      },
    }
  : {
      register(data) {
        const body = {
          phone_number: normalizePhone(data.phone_number),
          password: data.password,
          display_name: data.display_name,
          ...(data.email ? { email: data.email } : {}),
        };
        return request('/api/v1/auth/register', { method: 'POST', body });
      },
      login(data) {
        const body = {
          phone_number: normalizePhone(data.phone_number),
          password: data.password,
        };
        return request('/api/v1/auth/login', { method: 'POST', body });
      },
      sendResetCode(data) {
        return request('/api/v1/auth/forgot-password/send-code', { method: 'POST', body: data });
      },
      resetPassword(data) {
        return request('/api/v1/auth/forgot-password/reset', { method: 'POST', body: data });
      },
      getProfile() {
        return request('/api/v1/users/me');
      },
      updateProfile(data) {
        return request('/api/v1/users/me', { method: 'PUT', body: data });
      },
      updateContact(data) {
        return request('/api/v1/users/me/contact', { method: 'PUT', body: data });
      },
      getRating() {
        return request('/api/v1/users/me/rating');
      },
      getPublicProfile(userId) {
        return request(`/api/v1/users/${userId}/public`);
      },
    };
