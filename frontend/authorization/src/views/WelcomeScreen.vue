<template>
  <transition name="fade" appear>
    <div class="welcome" v-if="!isFinished">
      <main class="main-content">
        <!-- Hero Section -->
        <section class="hero-card">
          <img
            class="hero-image"
            :src="heroImage"
            alt="Сообщество уличных тренировок"
          />
          <div class="hero-overlay"></div>
          <div class="hero-content">
            <div class="hero-text">
              <h1 class="hero-title">Плечом к плечу</h1>
              <p class="hero-subtitle">Твое сообщество для уличных тренировок</p>
            </div>
            <div class="hero-actions">
              <button class="btn btn-primary" @click="goRegister">
                Регистрация
              </button>
              <button class="btn btn-secondary" @click="goLogin">
                Войти
              </button>
              <p class="auth-note">Присоединяйтесь к 5,000+ атлетов в вашем городе</p>
            </div>
          </div>
        </section>

        <!-- Feature Grid -->
        <section class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon icon-primary">
              <span class="material-symbols">groups</span>
            </div>
            <div class="feature-info">
              <h4>Найди команду</h4>
              <p>Тренируйся с единомышленниками своего уровня</p>
            </div>
          </div>
          <div class="feature-card">
            <div class="feature-icon icon-tertiary">
              <span class="material-symbols">map</span>
            </div>
            <div class="feature-info">
              <h4>Карта площадок</h4>
              <p>Лучшие места для тренировок по всему городу</p>
            </div>
          </div>
          <div class="feature-card">
            <div class="feature-icon icon-secondary">
              <span class="material-symbols">military_tech</span>
            </div>
            <div class="feature-info">
              <h4>Достижения</h4>
              <p>Прогрессируй и открывай новые разряды</p>
            </div>
          </div>
        </section>
      </main>

      <!-- Ambient Glow -->
      <div class="ambient-glow"></div>
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
  background: #f3f4f5;
  font-family: 'Inter', sans-serif;
  color: #191c1d;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  z-index: 1000;
}

/* ===== Main ===== */
.main-content {
  padding: 0 12px 24px;
  max-width: 1024px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ===== Hero Card ===== */
.hero-card {
  position: relative;
  width: 100%;
  min-height: 480px;
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
  margin-top: 12px;
}

.hero-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.7s ease;
}

.hero-card:hover .hero-image {
  transform: scale(1.05);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 0%, rgba(0, 0, 0, 0.05) 30%, rgba(0, 0, 0, 0.1) 60%, rgba(0, 0, 0, 0.75) 100%);
}

.hero-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  z-index: 2;
}

.hero-text {
  padding: 16px;
}

.hero-title {
  font-size: 28px;
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

.hero-actions {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.5) 0%, transparent 100%);
}

.btn {
  width: 100%;
  padding: 13px 20px;
  border: none;
  border-radius: 9999px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  font-family: 'Inter', sans-serif;
  -webkit-tap-highlight-color: transparent;
  min-height: 44px;
}

.btn:active {
  transform: scale(0.95);
}

.btn-primary {
  background: linear-gradient(135deg, #9b2f00 0%, #c2410c 100%);
  color: #ffffff;
  box-shadow: 0 2px 10px rgba(155, 47, 0, 0.25);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.auth-note {
  text-align: center;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  padding: 0 8px;
  margin: 0;
}

/* ===== Feature Grid ===== */
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

.feature-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.feature-card {
  background: #e1e3e4;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.feature-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon .material-symbols {
  font-size: 22px;
}

.icon-primary {
  background: #c2410c;
  color: #ffece7;
}

.icon-tertiary {
  background: #0069de;
  color: #ffffff;
}

.icon-secondary {
  background: #fea182;
  color: #78351e;
}

.feature-info h4 {
  font-size: 14px;
  font-weight: 600;
  color: #191c1d;
  margin: 0 0 2px;
  line-height: 1.2;
}

.feature-info p {
  font-size: 12px;
  color: #59413a;
  margin: 0;
  line-height: 1.35;
}

/* ===== Ambient Glow ===== */
.ambient-glow {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 20%;
  background: rgba(155, 47, 0, 0.1);
  filter: blur(120px);
  pointer-events: none;
  z-index: -1;
}

/* ===== Transitions ===== */
.fade-enter-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(16px);
}

/* ===== Маленькие экраны (320px и ниже) ===== */
@media (max-width: 320px) {
  .main-content {
    padding: 0 8px 16px;
    gap: 10px;
  }

  .hero-card {
    min-height: 380px;
    border-radius: 10px;
    margin-top: 8px;
  }

  .hero-text {
    padding: 12px;
  }

  .hero-title {
    font-size: 24px;
  }

  .hero-subtitle {
    font-size: 12px;
  }

  .hero-actions {
    padding: 12px;
    gap: 6px;
  }

  .btn {
    padding: 12px 16px;
    font-size: 14px;
    min-height: 40px;
  }

  .auth-note {
    font-size: 10px;
  }

  .feature-card {
    padding: 10px;
    gap: 10px;
    border-radius: 10px;
  }

  .feature-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
  }

  .feature-icon .material-symbols {
    font-size: 20px;
  }

  .feature-info h4 {
    font-size: 13px;
  }

  .feature-info p {
    font-size: 11px;
  }

  .feature-grid {
    gap: 8px;
  }
}

/* ===== iPhone SE / маленькие (321px — 375px) ===== */
@media (min-width: 321px) and (max-width: 375px) {
  .main-content {
    padding: 0 10px 18px;
    gap: 10px;
  }

  .hero-card {
    min-height: 420px;
  }

  .hero-text {
    padding: 14px;
  }

  .hero-title {
    font-size: 26px;
  }

  .hero-subtitle {
    font-size: 12px;
  }

  .hero-actions {
    padding: 14px;
  }

  .btn {
    padding: 12px 18px;
    font-size: 14px;
  }

  .feature-card {
    padding: 10px;
    gap: 10px;
  }

  .feature-icon {
    width: 38px;
    height: 38px;
  }
}

/* ===== Стандартные (376px — 428px) ===== */
@media (min-width: 376px) and (max-width: 428px) {
  .main-content {
    padding: 0 12px 20px;
  }

  .hero-card {
    min-height: 460px;
  }

  .hero-title {
    font-size: 30px;
  }

  .hero-subtitle {
    font-size: 13px;
  }

  .hero-actions {
    padding: 16px;
  }

  .btn {
    padding: 13px 20px;
    font-size: 15px;
  }
}

/* ===== Большие телефоны (429px — 767px) ===== */
@media (min-width: 429px) and (max-width: 767px) {
  .main-content {
    padding: 0 16px 24px;
    gap: 14px;
  }

  .hero-card {
    min-height: 500px;
  }

  .hero-title {
    font-size: 34px;
  }

  .hero-subtitle {
    font-size: 15px;
  }

  .hero-actions {
    padding: 18px;
  }

  .btn {
    padding: 14px 22px;
    font-size: 16px;
  }

  .feature-info h4 {
    font-size: 15px;
  }

  .feature-info p {
    font-size: 13px;
  }
}

/* ===== Планшеты (768px — 1023px) ===== */
@media (min-width: 768px) and (max-width: 1023px) {
  .main-content {
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
    grid-template-areas:
      "hero"
      "features";
    gap: 16px;
    padding: 0 20px 32px;
  }

  .hero-card {
    grid-area: hero;
    min-height: 560px;
    border-radius: 14px;
  }

  .feature-grid {
    grid-area: features;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }

  .hero-title {
    font-size: 38px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .hero-actions {
    padding: 20px;
    gap: 10px;
  }

  .btn {
    padding: 14px 22px;
    font-size: 16px;
  }

  .feature-card {
    padding: 14px;
    border-radius: 14px;
  }
}

/* ===== Планшеты большие и десктоп (1024px+) ===== */
@media (min-width: 1024px) {
  .main-content {
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
    grid-template-areas:
      "hero"
      "features";
    gap: 16px;
    padding: 0 24px 40px;
  }

  .hero-card {
    grid-area: hero;
    min-height: 600px;
    border-radius: 16px;
  }

  .feature-grid {
    grid-area: features;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }

  .hero-title {
    font-size: 44px;
  }

  .hero-subtitle {
    font-size: 18px;
  }

  .hero-actions {
    padding: 24px;
    gap: 12px;
  }

  .btn {
    padding: 16px 28px;
    font-size: 18px;
  }

  .feature-card {
    padding: 16px;
    border-radius: 16px;
  }

  .feature-info h4 {
    font-size: 15px;
  }

  .feature-info p {
    font-size: 13px;
  }
}

/* ===== Ландшафтная ориентация (малая высота) ===== */
@media (max-height: 500px) and (orientation: landscape) {
  .main-content {
    padding: 0 12px 12px;
    gap: 10px;
  }

  .hero-card {
    min-height: 240px;
    margin-top: 0;
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

  .hero-actions {
    padding: 10px 14px;
    gap: 6px;
  }

  .btn {
    padding: 8px 16px;
    font-size: 13px;
    min-height: 36px;
  }

  .feature-card {
    padding: 10px;
    gap: 10px;
  }

  .feature-icon {
    width: 36px;
    height: 36px;
  }
}
</style>
