<template>
  <div class="register-page">
    <!-- TopAppBar -->
    <header class="top-bar">
      <span class="brand">Плечом к плечу</span>
    </header>

    <main class="main-content">
      <!-- Hero Section -->
      <section class="hero-cell">
        <img
          class="hero-image"
          :src="heroImage"
          alt="Сообщество уличных тренировок"
        />
        <div class="hero-overlay"></div>
        <div class="hero-text">
          <h2 class="hero-title">Общий пульс.</h2>
          <p class="hero-subtitle">Присоединяйся к сообществу уличных тренировок</p>
        </div>
      </section>

      <!-- Registration Form -->
      <section class="form-cell">
        <div>
          <h3 class="form-title">Создать аккаунт</h3>
          <form class="register-form" @submit.prevent="handleRegister">
            <div class="field">
              <label class="field-label">Номер телефона</label>
              <input
                v-model="phone"
                type="tel"
                placeholder="+7 (900) 000-00-00"
                class="form-input"
              />
            </div>
            <div class="field">
              <label class="field-label">Логин</label>
              <input
                v-model="login"
                type="text"
                placeholder="Введите логин"
                class="form-input"
              />
            </div>
            <div class="field">
              <label class="field-label">Пароль</label>
              <input
                v-model="password"
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
            <button type="submit" class="register-btn" :disabled="loading">
              {{ loading ? 'Загрузка...' : 'Зарегистрироваться' }}
            </button>
          </form>
        </div>
        <div class="form-footer">
          <p class="login-text">
            Уже есть аккаунт?
            <router-link to="/login" class="login-link">
              Войти
            </router-link>
          </p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import heroImage from '../assets/RegistrationPicture.jpg';

const router = useRouter();
const phone = ref('');
const login = ref('');
const password = ref('');
const confirmPassword = ref('');
const error = ref('');
const loading = ref(false);

const handleRegister = async () => {
  error.value = '';
  if (!phone.value || !login.value || !password.value || !confirmPassword.value) {
    error.value = 'Заполните все поля';
    return;
  }
  if (password.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают';
    return;
  }

  loading.value = true;
  try {
    router.push('/profile');
  } catch {
    error.value = 'Ошибка регистрации. Попробуйте снова.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.register-page {
  position: fixed;
  inset: 0;
  background: #f3f4f5;
  font-family: 'Inter', sans-serif;
  color: #191c1d;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* ===== TopAppBar ===== */
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  background: #fafafa;
  z-index: 50;
}

.brand {
  font-size: 18px;
  font-weight: 600;
  color: #9b2f00;
  font-style: italic;
  letter-spacing: -0.02em;
}

/* ===== Main ===== */
.main-content {
  padding: 80px 12px 32px;
  max-width: 1024px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

/* ===== Hero Cell ===== */
.hero-cell {
  position: relative;
  width: 100%;
  min-height: 280px;
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
}

.hero-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.7s ease;
}

.hero-cell:hover .hero-image {
  transform: scale(1.05);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 0%, rgba(0, 0, 0, 0.05) 30%, rgba(0, 0, 0, 0.1) 60%, rgba(0, 0, 0, 0.75) 100%);
}

.hero-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 16px;
  z-index: 2;
}

.hero-title {
  font-size: 26px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
  word-break: break-word;
}

.hero-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  margin: 4px 0 0;
  font-weight: 500;
  line-height: 1.35;
}

/* ===== Form Cell ===== */
.form-cell {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 12px;
}

.form-title {
  font-size: 20px;
  font-weight: 600;
  color: #191c1d;
  margin: 0 0 12px;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
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

.register-btn {
  width: 100%;
  padding: 13px 20px;
  border: none;
  border-radius: 9999px;
  font-size: 15px;
  font-weight: 600;
  background: linear-gradient(135deg, #c2410c 0%, #9b2f00 100%);
  color: #ffffff;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
  box-shadow: 0 2px 10px rgba(194, 65, 12, 0.25);
  margin-top: 4px;
  min-height: 44px;
  font-family: 'Inter', sans-serif;
  -webkit-tap-highlight-color: transparent;
}

.register-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.register-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.register-btn:hover:not(:disabled) {
  opacity: 0.92;
  box-shadow: 0 4px 16px rgba(194, 65, 12, 0.3);
}

.form-footer {
  margin-top: 8px;
  text-align: center;
}

.login-text {
  font-size: 13px;
  color: #59413a;
  margin: 0;
}

.login-link {
  color: #9b2f00;
  font-weight: 700;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}

/* ===== Footer Link ===== */
.footer-link {
  display: none;
}

/* ===== Маленькие экраны (320px и ниже) ===== */
@media (max-width: 320px) {
  .main-content {
    padding: 0 8px 16px;
    padding-top: 72px;
    gap: 10px;
  }

  .hero-cell {
    min-height: 220px;
    border-radius: 10px;
  }

  .hero-text {
    padding: 12px;
  }

  .hero-title {
    font-size: 22px;
  }

  .hero-subtitle {
    font-size: 12px;
  }

  .form-cell {
    padding: 14px;
    border-radius: 10px;
  }

  .form-title {
    font-size: 17px;
    margin-bottom: 10px;
  }

  .form-input {
    padding: 12px 14px;
    font-size: 13px;
  }

  .register-btn {
    padding: 12px 16px;
    font-size: 14px;
    min-height: 40px;
  }

  .error {
    font-size: 11px;
    padding: 6px 10px;
  }

  .login-text {
    font-size: 12px;
  }
}

/* ===== iPhone SE / маленькие (321px — 375px) ===== */
@media (min-width: 321px) and (max-width: 375px) {
  .main-content {
    padding: 0 10px 18px;
    padding-top: 72px;
    gap: 10px;
  }

  .hero-cell {
    min-height: 240px;
  }

  .hero-text {
    padding: 14px;
  }

  .hero-title {
    font-size: 24px;
  }

  .hero-subtitle {
    font-size: 12px;
  }

  .form-cell {
    padding: 14px;
  }

  .form-input {
    padding: 12px 14px;
    font-size: 13px;
  }

  .register-btn {
    padding: 12px 18px;
    font-size: 14px;
  }
}

/* ===== Стандартные (376px — 428px) ===== */
@media (min-width: 376px) and (max-width: 428px) {
  .main-content {
    padding: 0 12px 20px;
    padding-top: 72px;
  }

  .hero-cell {
    min-height: 260px;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-subtitle {
    font-size: 13px;
  }

  .form-cell {
    padding: 16px;
  }

  .form-title {
    font-size: 20px;
  }

  .form-input {
    padding: 13px 16px;
    font-size: 14px;
  }

  .register-btn {
    padding: 13px 20px;
    font-size: 15px;
  }
}

/* ===== Большие телефоны (429px — 767px) ===== */
@media (min-width: 429px) and (max-width: 767px) {
  .main-content {
    padding: 0 16px 24px;
    padding-top: 72px;
    gap: 14px;
  }

  .hero-cell {
    min-height: 300px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 15px;
  }

  .form-cell {
    padding: 18px;
  }

  .form-title {
    font-size: 22px;
  }

  .register-btn {
    padding: 14px 22px;
    font-size: 16px;
  }
}

/* ===== Планшеты (768px — 1023px) ===== */
@media (min-width: 768px) and (max-width: 1023px) {
  .main-content {
    grid-template-columns: 7fr 5fr;
    grid-template-rows: auto auto;
    grid-template-areas:
      "hero form";
    gap: 16px;
    padding: 0 20px 32px;
    padding-top: 96px;
  }

  .hero-cell {
    grid-area: hero;
    min-height: 400px;
    border-radius: 14px;
  }

  .form-cell {
    grid-area: form;
    padding: 20px;
    border-radius: 14px;
  }

  .hero-title {
    font-size: 36px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .form-title {
    font-size: 22px;
    margin-bottom: 14px;
  }

  .register-btn {
    padding: 14px 22px;
    font-size: 16px;
  }
}

/* ===== Планшеты большие и десктоп (1024px+) ===== */
@media (min-width: 1024px) {
  .main-content {
    grid-template-columns: 7fr 5fr;
    grid-template-rows: auto auto;
    grid-template-areas:
      "hero form";
    gap: 16px;
    padding: 0 24px 40px;
    padding-top: 96px;
  }

  .hero-cell {
    grid-area: hero;
    min-height: 500px;
    border-radius: 16px;
  }

  .form-cell {
    grid-area: form;
    padding: 24px;
    border-radius: 16px;
  }

  .hero-title {
    font-size: 44px;
  }

  .hero-subtitle {
    font-size: 18px;
  }

  .form-title {
    font-size: 22px;
    margin-bottom: 16px;
  }

  .register-btn {
    padding: 16px 28px;
    font-size: 18px;
  }
}

/* ===== Ландшафтная ориентация (малая высота) ===== */
@media (max-height: 500px) and (orientation: landscape) {
  .main-content {
    padding: 0 12px 12px;
    padding-top: 72px;
    gap: 10px;
  }

  .hero-cell {
    min-height: 160px;
  }

  .hero-text {
    padding: 10px 14px;
  }

  .hero-title {
    font-size: 22px;
  }

  .hero-subtitle {
    font-size: 12px;
  }

  .form-cell {
    padding: 12px;
  }

  .form-input {
    padding: 10px 14px;
    font-size: 13px;
  }

  .register-btn {
    padding: 8px 16px;
    font-size: 13px;
    min-height: 36px;
  }
}
</style>
