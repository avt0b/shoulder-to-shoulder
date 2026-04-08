<template>
  <div class="app-container">
    <transition name="map-expand" mode="out-in">
      <MapLight v-if="isMapExpanded" @close="closeMap" />
      <MainPage v-else @expand-map="expandMap" />
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MainPage from './components/MainPage.vue'
import MapLight from './components/MapLight.vue'

const isMapExpanded = ref(false)

const expandMap = () => {
  isMapExpanded.value = true
}

const closeMap = () => {
  isMapExpanded.value = false
}
</script>

<style scoped>
.app-container {
  position: relative;
  width: 100%;
  min-height: 100dvh;
  overflow: hidden;
}

.map-expand-enter-active,
.map-expand-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.map-expand-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.map-expand-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
