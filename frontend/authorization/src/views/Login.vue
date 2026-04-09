<template>
  <div class="login-page">
    <!-- Full-screen Hero -->
    <section class="hero">
      <img
        class="hero-image"
        :src="heroImage"
        alt="Сообщество уличных тренировок"
      />
      <div class="hero-overlay"></div>

      <!-- Welcome Text -->
      <div class="welcome-text">
        <h2 class="welcome-title">Давно не виделись!</h2>
        <p class="welcome-subtitle">Готовы к тренировке?</p>
      </div>

      <!-- Login Form -->
      <div class="form-wrapper">
        <div class="form-header">
          <h3 class="form-title">Войти в аккаунт</h3>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="field">
            <label class="field-label">Номер телефона</label>
            <input
              v-model="phone_number"
              type="tel"
              placeholder="+7 (900) 000-00-00"
              class="form-input"
            />
          </div>
          <div class="field">
            <div class="field-header">
              <label class="field-label">Пароль</label>
              <router-link to="/forgot-password" class="forgot-link">
                Забыли пароль?
              </router-link>
            </div>
            <input
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="form-input"
            />
          </div>
          <p v-if="error" class="error">{{ error }}</p>
          <button type="submit" class="login-btn" :disabled="loading">
            {{ loading ? 'Загрузка...' : 'Войти' }}
          </button>
        </form>

        <div class="form-footer">
          <p class="register-text">
            Нет аккаунта?
            <router-link to="/register" class="register-link">
              Регистрация
            </router-link>
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../api/index';
import heroImage from '../assets/LoginPicture.jpg';

const router = useRouter();
const phone_number = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  error.value = '';

  const phoneRegex = /^(\+7|7|8)?\d{10}$/;
  if (!phoneRegex.test(phone_number.value.replace(/[\s\-\(\)]/g, ''))) {
    error.value = 'Неверный формат номера телефона. Используйте формат +7XXXXXXXXXX';
    return;
  }

  if (!password.value) {
    error.value = 'Заполните все поля';
    return;
  }

  loading.value = true;
  try {
    const data = await authApi.login({ phone_number: phone_number.value, password: password.value });
    localStorage.setItem('token', data.access_token);
    router.push('/profile');
  } catch (e) {
    const msg = e.message || '';
    if (msg.includes('номер телефона') || msg.toLowerCase().includes('phone')) {
      error.value = 'Пользователь с таким номером не найден';
    } else if (msg.includes('пароль') || msg.toLowerCase().includes('password')) {
      error.value = 'Неверный пароль';
    } else if (msg.includes('деактив')) {
      error.value = 'Аккаунт заблокирован. Обратитесь в поддержку';
    } else {
      error.value = 'Ошибка входа. Попробуйте снова.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.login-page {
  position: fixed;
  inset: 0;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

/* ===== Hero ===== */
.hero {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.hero-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.7s ease;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.2) 40%, rgba(0, 0, 0, 0.05) 100%);
}

/* ===== Welcome Text ===== */
.welcome-text {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  padding-bottom: 40vh;
  z-index: 2;
}

.welcome-title {
  font-size: clamp(28px, 7vw, 44px);
  font-weight: 800;
  color: #ffffff;
  margin: 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.35);
}

.welcome-subtitle {
  font-size: clamp(14px, 3.5vw, 18px);
  color: rgba(255, 255, 255, 0.9);
  margin: 6px 0 0;
  font-weight: 500;
  line-height: 1.35;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.3);
}

/* ===== Form Wrapper ===== */
.form-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px 20px 0 0;
  padding: 0 20px max(20px, env(safe-area-inset-bottom));
  padding-top: 24px;
  z-index: 2;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.15);
}

/* ===== Form Header ===== */
.form-header {
  text-align: center;
  margin-bottom: 20px;
}

.form-title {
  font-size: 20px;
  font-weight: 700;
  color: #191c1d;
  margin: 0;
  letter-spacing: -0.01em;
}

/* ===== Form ===== */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.field-label {
  font-size: 11px;
  font-weight: 500;
  color: #59413a;
  margin-left: 4px;
}

.forgot-link {
  font-size: 10px;
  font-weight: 500;
  color: #9b2f00;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.forgot-link:hover {
  text-decoration: underline;
}

.form-input {
  width: 100%;
  padding: 13px 16px;
  background: #e7e8e9;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  color: #191c1d;
  outline: none;
  transition: box-shadow 0.2s;
  font-family: 'Inter', sans-serif;
  min-height: 44px;
  box-sizing: border-box;
}

.form-input:focus {
  box-shadow: 0 0 0 3px rgba(194, 65, 12, 0.15);
}

.form-input::placeholder {
  color: #9ca3af;
}

.error {
  color: #ba1a1a;
  font-size: 12px;
  text-align: center;
  background: #ffdad6;
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 500;
  line-height: 1.3;
  word-break: break-word;
}

.login-btn {
  width: 100%;
  padding: 14px 20px;
  border: none;
  border-radius: 9999px;
  font-size: 15px;
  font-weight: 600;
  background: linear-gradient(135deg, #c2410c 0%, #9b2f00 100%);
  color: #ffffff;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
  box-shadow: 0 2px 10px rgba(194, 65, 12, 0.25);
  min-height: 48px;
  font-family: 'Inter', sans-serif;
  -webkit-tap-highlight-color: transparent;
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.login-btn:hover:not(:disabled) {
  opacity: 0.92;
  box-shadow: 0 4px 16px rgba(194, 65, 12, 0.3);
}

/* ===== Footer ===== */
.form-footer {
  margin-top: 12px;
  text-align: center;
}

.register-text {
  font-size: 13px;
  color: #59413a;
  margin: 0;
}

.register-link {
  color: #9b2f00;
  font-weight: 700;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
}

/* ===== Маленькие экраны ===== */
@media (max-width: 320px) {
  .form-wrapper {
    padding: 0 14px max(14px, env(safe-area-inset-bottom));
    padding-top: 18px;
    border-radius: 16px 16px 0 0;
  }

  .form-title {
    font-size: 17px;
  }

  .form-header {
    margin-bottom: 14px;
  }

  .form-input {
    padding: 12px 14px;
    font-size: 13px;
  }

  .login-btn {
    padding: 12px 16px;
    font-size: 14px;
    min-height: 42px;
  }
}

@media (min-width: 321px) and (max-width: 375px) {
  .form-wrapper {
    padding: 0 16px max(16px, env(safe-area-inset-bottom));
    padding-top: 20px;
  }

  .form-title {
    font-size: 18px;
  }

  .form-input {
    padding: 12px 14px;
    font-size: 13px;
  }

  .login-btn {
    padding: 13px 18px;
    font-size: 14px;
  }
}

@media (min-width: 376px) and (max-width: 428px) {
  .form-wrapper {
    padding: 0 20px max(20px, env(safe-area-inset-bottom));
    padding-top: 24px;
  }

  .form-title {
    font-size: 20px;
  }
}

@media (min-width: 429px) and (max-width: 767px) {
  .form-wrapper {
    max-width: 400px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 20px 20px 0 0;
  }
}

@media (min-width: 768px) {
  .form-wrapper {
    max-width: 420px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 24px 24px 0 0;
    padding-top: 28px;
  }

  .form-title {
    font-size: 22px;
  }
}

@media (max-height: 500px) and (orientation: landscape) {
  .form-wrapper {
    border-radius: 16px 16px 0 0;
    padding-top: 12px;
  }

  .form-header {
    margin-bottom: 10px;
  }

  .form-title {
    font-size: 16px;
  }

  .form-input {
    padding: 10px 14px;
    font-size: 13px;
  }

  .login-btn {
    padding: 10px 16px;
    font-size: 13px;
    min-height: 38px;
  }
}
</style>
