const API_URL = '/api';

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export const authApi = {
  async register({ phone, login, password }) {
    await delay();
    console.log('POST', API_URL + '/register', { phone, login, password });
    return { success: true, message: 'Регистрация успешна!' };
  },

  async login({ login, password }) {
    await delay();
    console.log('POST', API_URL + '/login', { login, password });
    return { success: true, message: 'Вход выполнен!', token: 'mock-token-123' };
  },

  async recovery({ emailOrPhone }) {
    await delay();
    console.log('POST', API_URL + '/recovery', { emailOrPhone });
    return { success: true, message: 'Инструкция по восстановлению отправлена!' };
  },
};
