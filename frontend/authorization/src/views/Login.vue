<template>
  <div class="login-page">
    <!-- TopAppBar -->
    <header class="top-bar">
      <span class="brand">Плечом к плечу</span>
    </header>

    <main class="main-content">
      <!-- Hero Bento Cell -->
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

      <!-- Login Form Cell -->
      <section class="form-cell">
        <div>
          <h3 class="form-title">Добро пожаловать</h3>
          <form class="login-form" @submit.prevent="handleLogin">
            <div class="field">
              <label class="field-label">Логин</label>
              <input
                v-model="login"
                type="text"
                placeholder="Введите ваш логин"
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
        </div>
        <div class="form-footer">
          <p class="register-text">
            Нет аккаунта?
            <router-link to="/register" class="register-link">
              Регистрация
            </router-link>
          </p>
        </div>
      </section>

      <!-- Stats Cell -->
      <section class="stats-cell">
        <span class="material-symbols stats-icon">groups</span>
        <div class="stats-count">12.4k+</div>
        <div class="stats-label">Атлетов в сети</div>
      </section>

      <!-- CTA Cell -->
      <section class="cta-cell">
        <div class="cta-info">
          <div class="cta-title">Готовы к движению?</div>
          <div class="cta-desc">Присоединяйтесь к ближайшей тренировке в вашем районе.</div>
        </div>
        <div class="cta-icon-wrap">
          <span class="material-symbols">bolt</span>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import heroImage from '../assets/LoginPicture.jpg';

const router = useRouter();
const login = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  error.value = '';
  if (!login.value || !password.value) {
    error.value = 'Заполните все поля';
    return;
  }

  loading.value = true;
  try {
    localStorage.setItem('token', 'mock-token');
    router.push('/profile');
  } catch {
    error.value = 'Ошибка входа. Попробуйте снова.';
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

.login-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
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

.form-footer {
  margin-top: 8px;
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

/* ===== Stats Cell ===== */
.stats-cell {
  background: #e1e3e4;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.material-symbols {
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  display: inline-block;
  line-height: 1;
  text-transform: none;
  letter-spacing: normal;
  word-wrap: normal;
  white-space: nowrap;
  direction: ltr;
  font-size: 22px;
}

.stats-icon {
  color: #9b2f00;
  margin-bottom: 6px;
}

.stats-count {
  font-size: 22px;
  font-weight: 700;
  color: #191c1d;
  line-height: 1;
}

.stats-label {
  font-size: 10px;
  font-weight: 500;
  color: #59413a;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 4px;
}

/* ===== CTA Cell ===== */
.cta-cell {
  background: #d8e2ff;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cta-info {
  flex: 1;
}

.cta-title {
  font-size: 14px;
  font-weight: 600;
  color: #001a41;
  margin-bottom: 2px;
}

.cta-desc {
  font-size: 12px;
  color: #004494;
  line-height: 1.35;
}

.cta-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: #0069de;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cta-icon-wrap .material-symbols {
  color: #ffffff;
  font-size: 22px;
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

  .login-btn {
    padding: 12px 16px;
    font-size: 14px;
    min-height: 40px;
  }

  .error {
    font-size: 11px;
    padding: 6px 10px;
  }

  .register-text {
    font-size: 12px;
  }

  .stats-cell {
    padding: 10px;
    border-radius: 10px;
  }

  .stats-icon {
    font-size: 20px;
  }

  .stats-count {
    font-size: 18px;
  }

  .stats-label {
    font-size: 9px;
  }

  .cta-cell {
    padding: 10px;
    border-radius: 10px;
  }

  .cta-title {
    font-size: 13px;
  }

  .cta-desc {
    font-size: 11px;
  }

  .cta-icon-wrap {
    width: 36px;
    height: 36px;
  }

  .cta-icon-wrap .material-symbols {
    font-size: 20px;
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

  .login-btn {
    padding: 12px 18px;
    font-size: 14px;
  }

  .stats-cell {
    padding: 10px;
  }

  .cta-cell {
    padding: 10px;
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

  .login-btn {
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

  .login-btn {
    padding: 14px 22px;
    font-size: 16px;
  }

  .cta-title {
    font-size: 15px;
  }

  .cta-desc {
    font-size: 13px;
  }
}

/* ===== Планшеты (768px — 1023px) ===== */
@media (min-width: 768px) and (max-width: 1023px) {
  .main-content {
    grid-template-columns: 7fr 5fr;
    grid-template-rows: auto auto;
    grid-template-areas:
      "hero form"
      "stats cta";
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

  .stats-cell {
    grid-area: stats;
    padding: 14px;
    border-radius: 14px;
  }

  .cta-cell {
    grid-area: cta;
    padding: 14px;
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

  .login-btn {
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
      "hero form"
      "stats cta";
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

  .stats-cell {
    grid-area: stats;
    padding: 16px;
    border-radius: 16px;
  }

  .cta-cell {
    grid-area: cta;
    padding: 16px;
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

  .login-btn {
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

  .login-btn {
    padding: 8px 16px;
    font-size: 13px;
    min-height: 36px;
  }

  .cta-cell {
    padding: 10px;
  }

  .cta-icon-wrap {
    width: 36px;
    height: 36px;
  }
}
</style>
