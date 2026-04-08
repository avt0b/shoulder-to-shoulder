<script setup>
import ProfileNavbar from '../components/ProfileNavbar.vue';
</script>

<template>
  <div class="map-page">
    <h2 class="title">Карта</h2>
    <div class="map-placeholder">
      <svg viewBox="0 0 100 100" class="map-icon">
        <circle cx="50" cy="50" r="20" fill="none" stroke="currentColor" stroke-width="2"/>
        <circle cx="50" cy="50" r="5" fill="currentColor"/>
        <line x1="50" y1="10" x2="50" y2="30" stroke="currentColor" stroke-width="2"/>
        <line x1="50" y1="70" x2="50" y2="90" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="50" x2="30" y2="50" stroke="currentColor" stroke-width="2"/>
        <line x1="70" y1="50" x2="90" y2="50" stroke="currentColor" stroke-width="2"/>
      </svg>
      <p class="map-text">Здесь будет карта</p>
    </div>
    <ProfileNavbar />
  </div>
</template>

<style scoped>
.map-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px);
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.title {
  font-size: clamp(22px, 5vw, 32px);
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 30px;
}

.map-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: min(350px, 90vw);
}

.map-icon {
  width: 80px;
  height: 80px;
  color: #ffffff;
}

.map-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: clamp(14px, 3.5vw, 18px);
  text-align: center;
}
</style>
