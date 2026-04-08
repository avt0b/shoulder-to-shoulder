<script setup>
import ProfileNavbar from '../components/ProfileNavbar.vue';
</script>

<template>
  <div class="profile-page">
    <h2 class="title">Профиль</h2>
    <ProfileNavbar />
  </div>
</template>

<style scoped>
.profile-page {
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
}
</style>
