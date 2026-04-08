<template>
  <div class="auth-page">
    <h2 class="title">Восстановление пароля</h2>
    <form class="auth-form" @submit.prevent="handleRecovery">
      <div class="input-group">
        <input
          v-model="emailOrPhone"
          type="text"
          placeholder="Email или номер телефона"
          class="auth-input"
        />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
      <button type="submit" class="auth-button" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Восстановить' }}
      </button>
    </form>
    <div class="links">
      <router-link to="/login" class="link">Войти</router-link>
    </div>
    <BottomNavbar />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { authApi } from '../services/api';
import BottomNavbar from '../components/BottomNavbar.vue';

const emailOrPhone = ref('');
const error = ref('');
const success = ref('');
const loading = ref(false);

const handleRecovery = async () => {
  error.value = '';
  success.value = '';
  if (!emailOrPhone.value) {
    error.value = 'Введите Email или номер телефона';
    return;
  }

  loading.value = true;
  try {
    const res = await authApi.recovery({
      emailOrPhone: emailOrPhone.value,
    });
    success.value = res.message;
  } catch (e) {
    error.value = 'Ошибка восстановления. Попробуйте снова.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px);
  padding: clamp(15px, 4vw, 30px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.title {
  font-size: clamp(22px, 5vw, 32px);
  font-weight: bold;
  color: #ffffff;
  margin-bottom: clamp(20px, 5vw, 40px);
  text-align: center;
}

.auth-form {
  width: 100%;
  max-width: min(350px, 90vw);
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 3vw, 18px);
}

.input-group {
  width: 100%;
}

.auth-input {
  width: 100%;
  padding: clamp(12px, 3vw, 16px) clamp(15px, 4vw, 20px);
  border: none;
  border-radius: clamp(8px, 2vw, 14px);
  font-size: clamp(14px, 3.5vw, 17px);
  background: rgba(255, 255, 255, 0.95);
  box-sizing: border-box;
  outline: none;
  transition: box-shadow 0.3s;
}

.auth-input:focus {
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.4);
}

.error,
.success {
  font-size: clamp(12px, 3vw, 14px);
  text-align: center;
  padding: clamp(6px, 1.5vw, 10px);
  border-radius: clamp(6px, 1.5vw, 10px);
}

.error {
  color: #ff6b6b;
  background: rgba(255, 255, 255, 0.2);
}

.success {
  color: #51cf66;
  background: rgba(255, 255, 255, 0.2);
}

.auth-button {
  width: 100%;
  padding: clamp(12px, 3vw, 16px);
  border: none;
  border-radius: clamp(8px, 2vw, 14px);
  font-size: clamp(14px, 3.5vw, 17px);
  font-weight: 600;
  background: #ffffff;
  color: #764ba2;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-button:active:not(:disabled) {
  transform: scale(0.98);
}

.auth-button:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.links {
  display: flex;
  gap: clamp(15px, 4vw, 25px);
  margin-top: clamp(15px, 4vw, 25px);
}

.link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: clamp(12px, 3vw, 15px);
  transition: color 0.3s;
}

.link:hover {
  color: #ffffff;
  text-decoration: underline;
}

@media (max-width: 320px) {
  .auth-form {
    max-width: 100%;
  }
}

@media (min-width: 768px) {
  .auth-form {
    max-width: 400px;
  }
}
</style>
