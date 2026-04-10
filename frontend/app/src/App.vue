<template>
  <div class="app-container">
    <!-- Map Fullscreen -->
    <transition name="map-expand" mode="out-in">
      <MapLight v-if="isMapExpanded" @close="closeMap" @navigate="handleNavigateFromMap" />

      <!-- Events Page -->
      <EventsPage
        v-else-if="currentPage === 'events'"
        @close="currentPage = 'main'"
        @navigate="handleNavigate"
      />

      <!-- Main Page -->
      <MainPage v-else @expand-map="expandMap" @navigate="handleNavigate" />
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import MainPage from './components/MainPage.vue'
import MapLight from './components/MapLight.vue'
import EventsPage from './components/EventsPage.vue'

const isMapExpanded = ref(false)
const currentPage = ref('main')
const mapKey = ref(0)

const expandMap = () => {
  mapKey.value++
  isMapExpanded.value = true
}

const closeMap = () => {
  isMapExpanded.value = false
}

const handleNavigate = (page) => {
  currentPage.value = page
}

const handleNavigateFromMap = (page) => {
  isMapExpanded.value = false
  currentPage.value = page
}

// Глобальная функция для раскрытия карты из EventsPage
window.__triggerMapExpand = async () => {
  // Убеждаемся что MainPage смонтирован (currentPage = 'main')
  if (currentPage.value === 'main') {
    await nextTick()
    isMapExpanded.value = true
  }
}
</script>

<style scoped>
.app-container {
  position: relative;
  width: 100%;
  min-height: 100dvh;
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
