<template>
  <div class="forgot-password-page">
    <section class="hero">
      <img
        class="hero-image"
        :src="heroImage"
        alt="Сообщество уличных тренировок"
      />
      <div class="hero-overlay"></div>

      <!-- Welcome Text -->
      <div class="welcome-text">
        <h2 class="welcome-title">Забыли пароль?</h2>
        <p class="welcome-subtitle">Ничего страшного, восстановим!</p>
      </div>

      <!-- Forgot Password Form -->
      <div class="form-wrapper">
        <div class="form-header">
          <h3 class="form-title">Восстановление пароля</h3>
        </div>

        <!-- Step 1: Enter phone/email -->
        <form v-if="step === 1" class="forgot-form" @submit.prevent="handleSendCode">
          <div class="field">
            <label class="field-label">Номер телефона или Email</label>
            <input
              v-model="contact"
              type="text"
              placeholder="+7 (900) 000-00-00 или email"
              class="form-input"
            />
          </div>
          <p v-if="error" class="error">{{ error }}</p>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? 'Отправка...' : 'Получить код' }}
          </button>
        </form>

        <!-- Step 2: Enter code + new password -->
        <form v-if="step === 2" class="forgot-form" @submit.prevent="handleResetPassword">
          <div class="field">
            <label class="field-label">Код из SMS / Email</label>
            <input
              v-model="code"
              type="text"
              placeholder="123456"
              class="form-input"
            />
          </div>
          <div class="field">
            <label class="field-label">Новый пароль</label>
            <input
              v-model="newPassword"
              type="password"
              placeholder="••••••••"
              class="form-input"
            />
          </div>
          <div class="field">
            <label class="field-label">Подтверждение пароля</label>
            <input
              v-model="confirmPassword"
              type="password"
              placeholder="••••••••"
              class="form-input"
            />
          </div>
          <p v-if="error" class="error">{{ error }}</p>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? 'Сохранение...' : 'Сбросить пароль' }}
          </button>
        </form>

        <div class="form-footer">
          <p class="back-text">
            <router-link to="/login" class="back-link">
              ← Назад ко входу
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
import heroImage from '../assets/ForgotPasswordPicture.jpg';

const router = useRouter();
const contact = ref('');
const code = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const error = ref('');
const loading = ref(false);
const step = ref(1);

const handleSendCode = async () => {
  error.value = '';
  if (!contact.value) {
    error.value = 'Введите номер телефона или Email';
    return;
  }

  loading.value = true;
  try {
    await authApi.sendResetCode({ contact: contact.value });
    step.value = 2;
  } catch (e) {
    error.value = e.message || 'Ошибка отправки кода. Попробуйте снова.';
  } finally {
    loading.value = false;
  }
};

const handleResetPassword = async () => {
  error.value = '';
  if (!code.value || !newPassword.value || !confirmPassword.value) {
    error.value = 'Заполните все поля';
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают';
    return;
  }

  loading.value = true;
  try {
    await authApi.resetPassword({
      contact: contact.value,
      code: code.value,
      new_password: newPassword.value,
    });
    router.push('/login');
  } catch (e) {
    error.value = e.message || 'Ошибка сброса пароля. Попробуйте снова.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.forgot-password-page {
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
  max-height: 75vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
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
.forgot-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
}

.field-label {
  font-size: 11px;
  font-weight: 500;
  color: #59413a;
  margin-left: 4px;
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

.submit-btn {
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

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.92;
  box-shadow: 0 4px 16px rgba(194, 65, 12, 0.3);
}

/* ===== Footer ===== */
.form-footer {
  margin-top: 12px;
  padding-bottom: 4px;
  text-align: center;
}

.back-text {
  font-size: 13px;
  color: #59413a;
  margin: 0;
}

.back-link {
  color: #9b2f00;
  font-weight: 700;
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}

/* ===== Маленькие экраны ===== */
@media (max-width: 320px) {
  .form-wrapper {
    padding: 0 14px max(14px, env(safe-area-inset-bottom));
    padding-top: 16px;
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

  .submit-btn {
    padding: 12px 16px;
    font-size: 14px;
    min-height: 42px;
  }
}

@media (min-width: 321px) and (max-width: 375px) {
  .form-wrapper {
    padding: 0 16px max(16px, env(safe-area-inset-bottom));
    padding-top: 18px;
  }

  .form-title {
    font-size: 18px;
  }

  .form-input {
    padding: 12px 14px;
    font-size: 13px;
  }

  .submit-btn {
    padding: 13px 18px;
    font-size: 14px;
  }
}

@media (min-width: 376px) and (max-width: 428px) {
  .form-wrapper {
    padding: 0 20px max(20px, env(safe-area-inset-bottom));
    padding-top: 20px;
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
    padding-top: 24px;
  }

  .form-title {
    font-size: 22px;
  }
}

@media (max-height: 500px) and (orientation: landscape) {
  .welcome-text {
    padding-bottom: 28vh;
  }

  .welcome-title {
    font-size: 22px;
  }

  .welcome-subtitle {
    font-size: 12px;
  }

  .form-wrapper {
    border-radius: 16px 16px 0 0;
    padding-top: 12px;
    max-height: 80vh;
  }

  .form-header {
    margin-bottom: 8px;
  }

  .form-title {
    font-size: 16px;
  }

  .form-input {
    padding: 10px 14px;
    font-size: 13px;
  }

  .submit-btn {
    padding: 10px 16px;
    font-size: 13px;
    min-height: 38px;
  }
}
</style>
