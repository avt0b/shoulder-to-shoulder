<template>
  <transition name="fade" appear>
    <div class="welcome" v-if="!isFinished">
      <!-- Full-screen Hero -->
      <section class="hero">
        <img
          class="hero-image"
          :src="heroImage"
          alt="Сообщество уличных тренировок"
        />
        <div class="hero-overlay"></div>

        <!-- Centered Title -->
        <div class="hero-content">
          <h1 class="hero-title">Плечом к плечу</h1>
          <p class="hero-subtitle">Твое сообщество для уличных тренировок</p>
        </div>

        <!-- Bottom Buttons -->
        <div class="hero-actions">
          <button class="btn btn-primary" @click="goRegister">
            Регистрация
          </button>
          <button class="btn btn-glass" @click="goLogin">
            Войти
          </button>
        </div>
      </section>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import heroImage from '../assets/WelcomePicture.jpg';

const router = useRouter();
const isFinished = ref(false);

const goLogin = () => {
  finish();
  router.push('/login');
};

const goRegister = () => {
  finish();
  router.push('/register');
};

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.welcome {
  position: fixed;
  inset: 0;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
  z-index: 1000;
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
    linear-gradient(to top, rgba(0, 0, 0, 0.65) 0%, rgba(0, 0, 0, 0) 35%),
    radial-gradient(ellipse at center, rgba(0, 0, 0, 0.15) 0%, rgba(0, 0, 0, 0.4) 100%);
}

/* ===== Centered Title ===== */
.hero-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  padding-bottom: 12vh;
  z-index: 2;
}

.hero-title {
  font-size: clamp(28px, 7vw, 48px);
  font-weight: 800;
  color: #ffffff;
  margin: 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.35);
}

.hero-subtitle {
  font-size: clamp(13px, 3vw, 16px);
  color: rgba(255, 255, 255, 0.92);
  margin: 6px 0 0;
  font-weight: 500;
  line-height: 1.35;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.3);
}

/* ===== Bottom Buttons ===== */
.hero-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 16px max(16px, env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 3;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.55) 0%, transparent 100%);
}

.btn {
  width: 100%;
  padding: 14px 20px;
  border: none;
  border-radius: 9999px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  font-family: 'Inter', sans-serif;
  -webkit-tap-highlight-color: transparent;
  min-height: 48px;
}

.btn:active {
  transform: scale(0.96);
}

.btn-primary {
  background: linear-gradient(135deg, #9b2f00 0%, #c2410c 100%);
  color: #ffffff;
  box-shadow: 0 2px 14px rgba(155, 47, 0, 0.35);
}

.btn-glass {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1.5px solid rgba(255, 255, 255, 0.3);
}

/* ===== Transitions ===== */
.fade-enter-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(16px);
}
</style>
