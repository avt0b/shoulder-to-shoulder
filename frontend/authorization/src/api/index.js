const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Переключи на true для использования mock-данных
const USE_MOCK = false;

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
    const errorMessage = typeof detail === 'string'
      ? detail
      : (typeof detail === 'object' && detail !== null)
        ? Object.values(detail).flat().join('. ') || `Ошибка сервера: ${response.status}`
        : `Ошибка сервера: ${response.status}`;
    throw new Error(errorMessage);
  }

  if (response.status === 204) return null;

  return response.json();
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
        return request('/api/v1/auth/register', { method: 'POST', body: data });
      },
      login(data) {
        return request('/api/v1/auth/login', { method: 'POST', body: data });
      },
      sendResetCode(data) {
        return request('/api/v1/auth/forgot-password/send-code', { method: 'POST', body: data });
      },
      resetPassword(data) {
        return request('/api/v1/auth/forgot-password/reset', { method: 'POST', body: data });
      },
    };
