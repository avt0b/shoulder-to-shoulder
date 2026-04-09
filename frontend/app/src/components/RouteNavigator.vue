<template>
  <div class="route-navigator">
    <!-- Header -->
    <div class="nav-header">
      <button class="back-btn" @click="$emit('close')">
        <span class="material-symbols-outlined">arrow_back</span>
      </button>
      <h2>Навигация</h2>
      <div class="placeholder"></div>
    </div>

    <!-- Input Fields -->
    <div class="nav-inputs">
      <div class="input-group">
        <label>От:</label>
        <input
          v-model="startPoint"
          type="text"
          disabled
          class="input-field disabled"
          placeholder="Получение координат..."
        />
        <button class="locate-btn" @click="refreshStartPoint" :disabled="loadingStart">
          <span class="material-symbols-outlined">gps_fixed</span>
        </button>
      </div>

      <button class="swap-btn" @click="swapPoints" :disabled="loading">
        <span class="material-symbols-outlined">swap_vert</span>
      </button>

      <div class="input-group">
        <label>До:</label>
        <input
          v-model="endPoint"
          type="text"
          placeholder="Выберите место..."
          class="input-field"
          @focus="showPlacesList = true"
        />
        <button class="clear-btn" v-if="endPoint" @click="endPoint = ''" style="visibility: visible">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <!-- Places Dropdown -->
      <div v-if="showPlacesList" class="places-dropdown">
        <div
          v-for="place in suggestedPlaces"
          :key="place.id"
          class="place-item"
          @click="selectPlace(place)"
        >
          <span class="place-emoji">{{ place.emoji || '📍' }}</span>
          <div class="place-info">
            <div class="place-name">{{ place.name }}</div>
            <div class="place-address">{{ place.address }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Route Info -->
    <div v-if="routeInfo && !loading" class="route-info">
      <div class="info-row">
        <span class="material-symbols-outlined">straighten</span>
        <span>{{ formatDistance(routeInfo.distance) }}</span>
      </div>
      <div class="info-row">
        <span class="material-symbols-outlined">schedule</span>
        <span>{{ formatDuration(routeInfo.duration) }}</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Построение маршрута...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-message">
      <span class="material-symbols-outlined">error</span>
      <p>{{ error }}</p>
    </div>

    <!-- Map (Leaflet will be mounted here) -->
    <div ref="mapContainer" class="route-map"></div>

    <!-- Start Navigation Button -->
    <button
      v-if="routeInfo && !loading"
      class="start-nav-btn"
      @click="startNavigation"
    >
      <span class="material-symbols-outlined">navigation</span>
      Начать навигацию
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { getRoute, getPlaces } from '@/services/api'
import { getCurrentPosition, getOrelCenter, OREL_PLACES, formatDistance, formatDuration } from '@/services/gps'

const emit = defineEmits(['close'])

// State
const startLat = ref(null)
const startLng = ref(null)
const startPlace = ref(OREL_PLACES.cityCenter)
const endPlace = ref(null)
const routeInfo = ref(null)
const loading = ref(false)
const loadingStart = ref(false)
const error = ref(null)
const showPlacesList = ref(false)
const places = ref([])
const mapContainer = ref(null)
let map = null
let routeLayer = null
let startMarker = null
let endMarker = null

// Computed
const startPoint = computed(() => {
  return startPlace.value?.name || 'Загружается...'
})

const endPoint = computed({
  get: () => endPlace.value?.name || '',
  set: (val) => {
    // При изменении текста в поле
  }
})

const suggestedPlaces = computed(() => {
  if (!places.value.length) {
    return Object.values(OREL_PLACES)
  }
  return places.value
})

// Methods
const initMap = () => {
  if (map) return

  map = L.map(mapContainer.value).setView([startLat.value, startLng.value], 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map)

  // Добавляем маркеры
  addMapMarkers()
}

const addMapMarkers = () => {
  if (!map) return

  // Удаляем старые маркеры
  if (startMarker) map.removeLayer(startMarker)
  if (endMarker) map.removeLayer(endMarker)

  // Начальная точка
  startMarker = L.circleMarker([startLat.value, startLng.value], {
    radius: 7,
    fillColor: '#4CAF50',
    color: '#fff',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.8
  })
    .addTo(map)
    .bindPopup('📍 ' + startPoint.value)

  // Конечная точка
  if (endPlace.value) {
    endMarker = L.circleMarker([endPlace.value.lat, endPlace.value.lng], {
      radius: 7,
      fillColor: '#FF5722',
      color: '#fff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8
    })
      .addTo(map)
      .bindPopup('📍 ' + endPlace.value.name)
  }

  // Подгоняем вид
  if (endPlace.value) {
    const bounds = L.latLngBounds(
      [startLat.value, startLng.value],
      [endPlace.value.lat, endPlace.value.lng]
    )
    map.fitBounds(bounds, { padding: [50, 50] })
  }
}

const drawRoute = (geometry) => {
  if (!map || !geometry) return

  // Удаляем старый маршрут
  if (routeLayer) map.removeLayer(routeLayer)

  // Преобразуем GeoJSON в points
  const points = geometry.coordinates.map((coord) => [coord[1], coord[0]])

  // Рисуем маршрут
  routeLayer = L.polyline(points, {
    color: '#2196F3',
    weight: 4,
    opacity: 0.8,
    dashArray: '5, 5'
  }).addTo(map)

  // Подгоняем вид
  const bounds = L.latLngBounds(points)
  map.fitBounds(bounds, { padding: [50, 50] })
}

const refreshStartPoint = async () => {
  loadingStart.value = true
  try {
    const pos = await getCurrentPosition()
    startLat.value = pos.lat
    startLng.value = pos.lng
    startPlace.value = pos
    if (map) {
      map.setView([startLat.value, startLng.value], 13)
      addMapMarkers()
    }
  } catch (err) {
    error.value = 'Не удалось получить GPS'
    console.error(err)
  } finally {
    loadingStart.value = false
  }
}

const swapPoints = () => {
  if (endPlace.value) {
    const temp = startPlace.value
    startPlace.value = endPlace.value
    startLat.value = endPlace.value.lat
    startLng.value = endPlace.value.lng
    endPlace.value = temp
  }
}

const selectPlace = (place) => {
  endPlace.value = place
  showPlacesList.value = false
  buildRoute()
}

const buildRoute = async () => {
  if (!endPlace.value || !startLat.value || !startLng.value) {
    error.value = 'Выберите конечную точку'
    return
  }

  loading.value = true
  error.value = null

  try {
    const data = await getRoute(
      startLat.value,
      startLng.value,
      endPlace.value.lat,
      endPlace.value.lng
    )

    routeInfo.value = {
      distance: data.distance,
      duration: data.duration,
      steps: data.steps || []
    }

    drawRoute(data.geometry)
    addMapMarkers()
  } catch (err) {
    error.value = 'Не удалось построить маршрут'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const startNavigation = () => {
  // Здесь можно добавить логику начала навигации
  console.log('🗺️ Навигация начата!')
}

const loadPlaces = async () => {
  try {
    const data = await getPlaces()
    places.value = data.places || []
  } catch (err) {
    console.warn('Не удалось загрузить места:', err)
  }
}

// Lifecycle
onMounted(async () => {
  // Получаем текущую позицию
  loadingStart.value = true
  try {
    const pos = await getCurrentPosition()
    startLat.value = pos.lat
    startLng.value = pos.lng
    startPlace.value = pos
  } finally {
    loadingStart.value = false
  }

  // Загружаем места
  await loadPlaces()

  // Инициализируем карту
  await nextTick()
  initMap()
})

// Следим за изменением endPlace для пересчета маршрута
watch(endPlace, () => {
  if (endPlace.value) {
    buildRoute()
  }
})
</script>

<style scoped>
.route-navigator {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  background: #f5f5f5;
  position: relative;
}

/* Header */
.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  gap: 12px;
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #f0f0f0;
}

.nav-header h2 {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.placeholder {
  width: 40px;
}

/* Input Fields */
.nav-inputs {
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  position: relative;
}

.input-group {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}

.input-group label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  width: 30px;
  text-transform: uppercase;
}

.input-field {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: #2196F3;
  background: #f0f8ff;
}

.input-field.disabled {
  background: #f9f9f9;
  color: #999;
  cursor: not-allowed;
}

.locate-btn,
.clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: background 0.2s;
  color: #2196F3;
}

.locate-btn:hover:not(:disabled),
.clear-btn:hover {
  background: #f0f8ff;
}

.locate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.swap-btn {
  width: 100%;
  height: 36px;
  margin: 8px 0;
  background: linear-gradient(135deg, #2196F3, #1976D2);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  font-size: 18px;
}

.swap-btn:hover:not(:disabled) {
  transform: rotate(180deg);
}

.swap-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Places Dropdown */
.places-dropdown {
  position: absolute;
  top: 100%;
  left: 16px;
  right: 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.place-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.place-item:last-child {
  border-bottom: none;
}

.place-item:hover {
  background: #f9f9f9;
}

.place-emoji {
  font-size: 18px;
  flex-shrink: 0;
}

.place-info {
  flex: 1;
}

.place-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.place-address {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

/* Route Info */
.route-info {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
}

.info-row {
  display: flex;
  gap: 6px;
  align-items: center;
  color: #333;
}

.info-row .material-symbols-outlined {
  font-size: 18px;
  color: #2196F3;
}

/* Map */
.route-map {
  flex: 1;
  position: relative;
  border-bottom: 1px solid #e0e0e0;
}

.route-map :deep(.leaflet-container) {
  height: 100%;
  width: 100%;
}

/* Loading */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px 16px;
  color: #666;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #f0f0f0;
  border-top-color: #2196F3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Error */
.error-message {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #ffebee;
  color: #c62828;
  border-bottom: 1px solid #ef5350;
  align-items: center;
}

.error-message .material-symbols-outlined {
  font-size: 20px;
}

.error-message p {
  margin: 0;
  font-size: 13px;
}

/* Start Navigation Button */
.start-nav-btn {
  position: absolute;
  bottom: 16px;
  right: 16px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  gap: 8px;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  transition: transform 0.2s;
}

.start-nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

/* Responsive */
@media (max-width: 640px) {
  .nav-inputs {
    padding: 12px;
  }

  .input-field {
    font-size: 13px;
    padding: 8px 10px;
  }

  .route-map {
    min-height: 300px;
  }
}
</style>
