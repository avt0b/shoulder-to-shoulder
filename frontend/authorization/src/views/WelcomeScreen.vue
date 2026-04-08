<template>
  <transition name="fade" appear>
    <div class="welcome" v-if="!isFinished">
      <div class="welcome-content">
        <div class="welcome-icon">🚀</div>
        <h1 class="welcome-title">Добро пожаловать!</h1>
        <p class="welcome-text">Войдите или создайте аккаунт, чтобы продолжить</p>

        <div class="buttons">
          <router-link to="/login" class="btn btn-primary" @click="finish">
            Войти
          </router-link>
          <router-link to="/register" class="btn btn-secondary" @click="finish">
            Регистрация
          </router-link>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isFinished = ref(false);

const finish = () => {
  isFinished.value = true;
  localStorage.setItem('app_visited', 'true');
};

onMounted(() => {
  const visited = localStorage.getItem('app_visited');
  if (visited) {
    isFinished.value = true;
    router.replace('/login');
  }
});
</script>

<style scoped>
.welcome {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 1000;
  padding: clamp(20px, 5vw, 40px) clamp(15px, 4vw, 30px);
}

.welcome-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.welcome-icon {
  font-size: clamp(60px, 15vw, 90px);
  margin-bottom: clamp(20px, 5vw, 35px);
  animation: bounce 0.8s ease-out;
}

.welcome-title {
  font-size: clamp(24px, 6vw, 36px);
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 10px;
}

.welcome-text {
  font-size: clamp(14px, 3.5vw, 17px);
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: clamp(30px, 8vw, 55px);
  max-width: min(280px, 85vw);
  line-height: 1.5;
}

.buttons {
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 3vw, 18px);
  width: 100%;
  max-width: min(300px, 85vw);
}

.btn {
  display: block;
  padding: clamp(13px, 3.5vw, 18px);
  border-radius: clamp(10px, 2.5vw, 16px);
  font-size: clamp(15px, 4vw, 19px);
  font-weight: 600;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn:active {
  transform: scale(0.97);
}

.btn-primary {
  background: #ffffff;
  color: #764ba2;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.btn-primary:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: 2px solid rgba(255, 255, 255, 0.4);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.25);
}

.fade-enter-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

@keyframes bounce {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  60% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 320px) {
  .buttons {
    max-width: 100%;
  }
}
</style>
