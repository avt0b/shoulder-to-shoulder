<template>
  <div class="register-page">
    <section class="hero">
      <img class="hero-image" :src="heroImage" alt="Сообщество уличных тренировок" />
      <div class="hero-overlay"></div>

      <div class="welcome-text">
        <h2 class="welcome-title">Добро пожаловать!</h2>
        <p class="welcome-subtitle">Станьте частью команды</p>
      </div>

      <div class="form-wrapper">
        <div class="form-header">
          <h3 class="form-title">Создать аккаунт</h3>
        </div>

        <form class="register-form" @submit.prevent="handleRegister">
          <div class="field">
            <label class="field-label">Номер телефона</label>
            <input v-model="phoneNumber" type="tel" placeholder="+7 (900) 000-00-00" class="form-input" />
          </div>
          <div class="field">
            <label class="field-label">Имя</label>
            <input v-model="displayName" type="text" placeholder="Введите имя" class="form-input" />
          </div>
          <div class="field">
            <label class="field-label">Email <span class="optional">(необязательно)</span></label>
            <input v-model="email" type="email" placeholder="user@example.com" class="form-input" />
          </div>
          <div class="field">
            <label class="field-label">Пароль</label>
            <input v-model="password" type="password" placeholder="••••••••" class="form-input" />
          </div>
          <div class="field">
            <label class="field-label">Подтверждение пароля</label>
            <input v-model="confirmPassword" type="password" placeholder="••••••••" class="form-input" />
          </div>
          <p v-if="authStore.error" class="error">{{ authStore.error }}</p>
          <button type="submit" class="register-btn" :disabled="authStore.loading">
            {{ authStore.loading ? 'Загрузка...' : 'Зарегистрироваться' }}
          </button>
        </form>

        <div class="form-footer">
          <p class="login-text">
            Уже есть аккаунт?
            <router-link to="/login" class="login-link">Войти</router-link>
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register, authStore } from '../stores/auth'
import heroImage from '../assets/RegistrationPicture.jpg'

const router = useRouter()
const phoneNumber = ref('')
const displayName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const handleRegister = async () => {
  const phoneRegex = /^(\+7|7|8)?\d{10}$/
  if (!phoneRegex.test(phoneNumber.value.replace(/[\s\-\(\)]/g, ''))) {
    authStore.error = 'Неверный формат номера телефона'
    return
  }
  if (!displayName.value || !password.value || !confirmPassword.value) {
    authStore.error = 'Заполните все поля'
    return
  }
  if (password.value !== confirmPassword.value) {
    authStore.error = 'Пароли не совпадают'
    return
  }

  try {
    await register({
      phone_number: phoneNumber.value,
      password: password.value,
      display_name: displayName.value,
      email: email.value || undefined,
    })
    router.push('/profile')
  } catch (e) {
    const msg = e.message || ''
    if (msg.toLowerCase().includes('phone') || msg.includes('номер')) {
      authStore.error = 'Аккаунт с таким номером уже существует'
    } else if (msg.toLowerCase().includes('email')) {
      authStore.error = 'Аккаунт с таким email уже существует'
    } else {
      authStore.error = 'Ошибка регистрации. Попробуйте снова.'
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.register-page {
  position: fixed;
  inset: 0;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

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
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.2) 40%, rgba(0, 0, 0, 0.05) 100%);
}

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
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.35);
}

.welcome-subtitle {
  font-size: clamp(14px, 3.5vw, 18px);
  color: rgba(255, 255, 255, 0.9);
  margin: 6px 0 0;
  font-weight: 500;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.3);
}

.form-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px 20px 0 0;
  padding: 0 20px max(20px, env(safe-area-inset-bottom));
  padding-top: 24px;
  z-index: 2;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.15);
  max-height: 75vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.form-header { text-align: center; margin-bottom: 20px; }
.form-title { font-size: 20px; font-weight: 700; color: #191c1d; margin: 0; }

.register-form { display: flex; flex-direction: column; gap: 12px; }

.field { display: flex; flex-direction: column; }
.field-label { font-size: 11px; font-weight: 500; color: #59413a; margin-left: 4px; }
.optional { font-weight: 400; color: #9ca3af; }

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
  min-height: 44px;
  box-sizing: border-box;
}

.form-input:focus { box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.15); }
.form-input::placeholder { color: #9ca3af; }

.error {
  color: #ba1a1a;
  font-size: 12px;
  text-align: center;
  background: #ffdad6;
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 500;
}

.register-btn {
  width: 100%;
  padding: 14px 20px;
  border: none;
  border-radius: 9999px;
  font-size: 15px;
  font-weight: 600;
  background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(234, 88, 12, 0.25);
  min-height: 48px;
  transition: transform 0.15s, opacity 0.15s;
}

.register-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.register-btn:active:not(:disabled) { transform: scale(0.98); }

.form-footer { margin-top: 12px; padding-bottom: 4px; text-align: center; }
.login-text { font-size: 13px; color: #59413a; margin: 0; }
.login-link { color: #ea580c; font-weight: 700; text-decoration: none; }
.login-link:hover { text-decoration: underline; }
</style>
