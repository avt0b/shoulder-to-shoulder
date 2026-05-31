<template>
  <div class="map-light" :class="{ dark: isDarkMode || isNinjaMode }">
    <!-- Map Canvas -->
    <main class="map-canvas">
      <div ref="mapRef" class="leaflet-map"></div>
    </main>

    <!-- Spread Transition Overlay -->
    <div
      class="spread-overlay"
      :class="{ active: isTransitioning }"
      :style="overlayStyle"
    ></div>

    <!-- Top AppBar -->
    <header class="top-bar">
      <button class="close-btn" @click="$emit('close')" style="position: relative; z-index: 10;">
        <span class="material-symbols-outlined" style="font-size: 24px;">close</span>
      </button>
      <div class="search-bar" style="position: relative">
        <span class="material-symbols-outlined">search</span>
        <input
          v-model="placeSearchQuery"
          type="text"
          placeholder="Поиск мест..."
          @input="onPlaceSearch"
          @focus="showPlaceSuggestions = true"
          @blur="hidePlaceSuggestionsDelayed"
        />
        <!-- Подсказки мест -->
        <div class="search-suggestions" v-if="showPlaceSuggestions && placeSearchResults.length > 0">
          <div
            v-for="place in placeSearchResults"
            :key="place.id"
            class="search-suggestion-item"
            @mousedown="selectPlaceOnMap(place)"
          >
            <span class="search-suggestion-emoji">{{ place.emoji }}</span>
            <div class="search-suggestion-info">
              <span class="search-suggestion-name">{{ place.name }}</span>
              <span class="search-suggestion-address">{{ place.address }}</span>
            </div>
          </div>
        </div>
      </div>
      <button class="filter-toggle-btn" @click="showFilters = !showFilters">
        <span class="material-symbols-outlined">tune</span>
      </button>
    </header>

    <!-- Filters Panel -->
    <div class="filters-panel" :class="{ open: showFilters }">
      <div class="filters-header">
        <h3>Фильтры</h3>
        <button class="reset-filters-btn" @click="resetFilters">Сбросить</button>
      </div>

      <!-- Тип активности -->
      <div class="filter-group">
        <label class="filter-label">Тип активности</label>
        <div class="filter-chips">
          <button
            v-for="chip in activityTypes"
            :key="chip.key"
            class="filter-chip"
            :class="{ active: filters.activityType === chip.key }"
            @click="filters.activityType = filters.activityType === chip.key ? '' : chip.key"
          >
            {{ chip.emoji }} {{ chip.label }}
          </button>
        </div>
      </div>

      <!-- Уровень шума/людности -->
      <div class="filter-group">
        <label class="filter-label">Уровень шума</label>
        <div class="filter-chips">
          <button
            v-for="chip in noiseLevels"
            :key="chip.key"
            class="filter-chip"
            :class="{ active: filters.noiseLevel === chip.key }"
            @click="filters.noiseLevel = filters.noiseLevel === chip.key ? '' : chip.key"
          >
            {{ chip.emoji }} {{ chip.label }}
          </button>
        </div>
      </div>

      <!-- Освещение -->
      <div class="filter-group">
        <label class="filter-label">
          <input type="checkbox" v-model="filters.lit" />
          <span class="filter-checkbox-box">
            <span class="material-symbols-outlined">check</span>
          </span>
          💡 Освещённая территория
        </label>
      </div>

      <!-- Раздевалки -->
      <div class="filter-group">
        <label class="filter-label">
          <input type="checkbox" v-model="filters.lockers" />
          <span class="filter-checkbox-box">
            <span class="material-symbols-outlined">check</span>
          </span>
          🚿 Есть раздевалки
        </label>
      </div>

      <!-- Скамейки -->
      <div class="filter-group">
        <label class="filter-label">
          <input type="checkbox" v-model="filters.benches" />
          <span class="filter-checkbox-box">
            <span class="material-symbols-outlined">check</span>
          </span>
          🪑 Есть скамейки
        </label>
      </div>

      <!-- Анонимное место -->
      <div class="filter-group">
        <label class="filter-label">
          <input type="checkbox" v-model="filters.anonymous" />
          <span class="filter-checkbox-box">
            <span class="material-symbols-outlined">check</span>
          </span>
          🤫 Анонимное место
        </label>
      </div>

      <!-- Apply Button -->
      <button class="apply-filters-btn" @click="applyFilters">
        <span class="material-symbols-outlined">search</span>
        <span>Применить ({{ filteredPlacesCount }} мест)</span>
      </button>
    </div>

    <!-- Map Controls — скрываются при выборе точки -->
    <div class="map-controls" :class="{ 'raised': routeFast && routeSafety || isNavigating }" v-if="!pickMode">
      <button class="control-btn control-btn-ninja" :class="{ active: isNinjaMode }" ref="ninjaBtnRef" @click="toggleNinjaMode" :title="isNinjaMode ? 'Обычный режим' : 'Режим ниндзя'">
        <span class="material-symbols-outlined">{{ isNinjaMode ? 'visibility' : 'sports_martial_arts' }}</span>
      </button>
      <button class="control-btn control-btn-primary" @click="useMyLocation" title="Моё местоположение">
        <span class="material-symbols-outlined filled">my_location</span>
      </button>
    </div>

    <!-- FAB Quick Start — скрывается при открытой форме маршрута -->
    <transition name="fab-fade">
      <div class="fab-quick-start" v-if="!showRouteForm">
        <button class="fab-btn" @click="showRouteForm = true">
          <span class="material-symbols-outlined">directions_run</span>
          <span>Быстрый старт</span>
        </button>
      </div>
    </transition>

    <!-- Route Form Panel -->
    <div class="route-panel" :class="{ open: showRouteForm }">
      <div class="route-panel-header">
        <h3>Маршрут</h3>
        <button class="route-close" @click="showRouteForm = false">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <!-- Откуда -->
      <div class="route-field">
        <label>Откуда</label>
        <div class="route-input-row">
          <span class="material-symbols-outlined route-dot start-dot">circle</span>
          <input
            v-model="routeStartQuery"
            type="text"
            placeholder="Введите адрес или..."
            @input="onStartSearch"
            @focus="showStartSuggestions = true"
            @blur="hideStartSuggestionsDelayed"
          />
          <button class="route-geo-btn" @click="useMyLocation" title="Моё местоположение">
            <span class="material-symbols-outlined">directions_run</span>
          </button>
        </div>
        <!-- Подсказки адресов (Nominatim) -->
        <div class="route-dropdown" v-if="showStartSuggestions && startSuggestions.length > 0">
          <div
            v-for="(s, i) in startSuggestions"
            :key="i"
            class="route-dropdown-item"
            @mousedown="selectStartAddress(s)"
          >
            <span class="material-symbols-outlined" style="font-size:18px;color:#787170">place</span>
            <div class="route-place-info">
              <span class="route-place-name">{{ s.name }}</span>
              <span class="route-place-address">{{ s.address }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Куда -->
      <div class="route-field">
        <label>Куда</label>
        <div class="route-input-row">
          <span class="material-symbols-outlined route-dot end-dot">location_on</span>
          <input
            v-model="routeEndQuery"
            type="text"
            placeholder="Введите адрес или выберите место..."
            @input="onEndSearch"
            @focus="showEndSuggestions = true"
            @blur="hideEndSuggestionsDelayed"
          />
        </div>
        <!-- Подсказки адресов (Nominatim) -->
        <div class="route-dropdown" v-if="showEndSuggestions && endSuggestions.length > 0">
          <div
            v-for="(s, i) in endSuggestions"
            :key="i"
            class="route-dropdown-item"
            @mousedown="selectEndAddress(s)"
          >
            <span class="material-symbols-outlined" style="font-size:18px;color:#787170">place</span>
            <div class="route-place-info">
              <span class="route-place-name">{{ s.name }}</span>
              <span class="route-place-address">{{ s.address }}</span>
            </div>
          </div>
        </div>
        <!-- Или места из базы -->
        <div class="route-dropdown" v-if="showEndSuggestions && filteredEndPlaces.length > 0 && endSuggestions.length === 0">
          <div
            v-for="place in filteredEndPlaces"
            :key="place.id"
            class="route-dropdown-item"
            :class="{ selected: routeEndId === place.id }"
            @mousedown="selectEndPlace(place)"
          >
            <span class="route-place-emoji">{{ place.emoji }}</span>
            <div class="route-place-info">
              <span class="route-place-name">{{ place.name }}</span>
              <span class="route-place-address">{{ place.address }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Указать на карте -->
      <div class="route-pick-mode">
        <button class="route-pick-btn" @click="startPickMode('start')">
          <span class="material-symbols-outlined route-dot start-dot">circle</span>
          <span>Откуда — на карте</span>
        </button>
        <button class="route-pick-btn" @click="startPickMode('end')">
          <span class="material-symbols-outlined route-dot end-dot">location_on</span>
          <span>Куда — на карте</span>
        </button>
      </div>

      <!-- Кнопка построить -->
      <button class="route-build-btn" @click="buildRoute" :disabled="!canBuildRoute">
        <span class="material-symbols-outlined">route</span>
        <span>Построить маршрут</span>
      </button>
    </div>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav" v-if="!pickMode">
      <a class="nav-item" @click="$emit('close')">
        <span class="material-symbols-outlined">map</span>
        <span>Карта</span>
      </a>
      <a class="nav-item" @click="router.push('/events'); $emit('close')">
        <span class="material-symbols-outlined">event</span>
        <span>Ивенты</span>
      </a>
      <a class="nav-item" @click="router.push('/profile'); $emit('close')">
        <span class="material-symbols-outlined">person</span>
        <span>Профиль</span>
      </a>
      <a class="nav-item" @click="router.push('/rating'); $emit('close')">
        <span class="material-symbols-outlined">emoji_events</span>
        <span>Рейтинг</span>
      </a>
    </nav>

    <!-- Pick Point Overlay — режим выбора точки на карте -->
    <transition name="pick-overlay-fade">
      <div v-if="pickMode" class="pick-overlay">
        <!-- Маркер-иголка по центру -->
        <div class="pick-pin">
          <svg viewBox="0 0 36 52" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 0C8.06 0 0 8.06 0 18c0 13.5 18 34 18 34s18-20.5 18-34C36 8.06 27.94 0 18 0z"
                  :fill="pickMode === 'start' ? '#22c55e' : pickMode === 'event' ? '#ea580c' : '#ea580c'"/>
            <circle cx="18" cy="18" r="8" fill="white"/>
            <circle :cx="18" cy="18" r="4"
                    :fill="pickMode === 'start' ? '#22c55e' : pickMode === 'event' ? '#ea580c' : '#ea580c'"/>
          </svg>
        </div>

        <!-- Подсказка -->
        <div class="pick-hint">
          <span class="pick-hint-text">
            {{ pickMode === 'start' ? '🟢 Откуда' : pickMode === 'event' ? '📍 Место встречи' : '🟠 Куда' }} — переместите карту
          </span>
        </div>

        <!-- Кнопки -->
        <div class="pick-actions">
          <button class="pick-cancel-btn" @click="cancelPickMode">
            <span class="material-symbols-outlined">close</span>
            <span>Отмена</span>
          </button>
          <button class="pick-confirm-btn" @click="confirmPickMode">
            <span class="material-symbols-outlined">check</span>
            <span>Готово</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- Route Toggle Bar — поверх карты над bottom-nav -->
    <transition name="route-toggle-fade">
      <div v-if="routeFast && routeSafety && !isNavigating" class="route-bar-group">
        <!-- Быстрый / Безопасный -->
        <div class="route-toggle-bar-overlay">
          <button
            class="route-toggle-btn"
            :class="{ active: activeRoute === 'fast' }"
            @click="switchRoute('fast')"
          >
            <span class="route-toggle-icon" style="color: #ea580c">⚡</span>
            <span>Быстрый</span>
            <span class="route-toggle-meta">{{ routeFast.distance }} • {{ routeFast.duration }}</span>
          </button>
          <button
            class="route-toggle-btn"
            :class="{ active: activeRoute === 'safety' }"
            @click="switchRoute('safety')"
          >
            <span class="route-toggle-icon" style="color: #16a34a">🛡</span>
            <span>Безопасный</span>
            <span class="route-toggle-meta">{{ routeSafety.distance }} • {{ routeSafety.duration }}</span>
          </button>
          <button class="route-close-overlay" @click="clearRoute">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- Кнопка "Начать навигацию" — ОТДЕЛЬНО -->
    <transition name="nav-start-fade">
      <div v-if="routeFast && routeSafety && !isNavigating" class="nav-start-float-btn">
        <button @click="startNavigation">
          <span class="material-symbols-outlined">navigation</span>
          <span>Начать навигацию</span>
        </button>
      </div>
    </transition>

    <!-- Navigation Bar — показывается при навигации -->
    <transition name="nav-bar-fade">
      <div v-if="isNavigating" class="nav-bar-overlay">
        <div class="nav-bar-info">
          <div class="nav-bar-item">
            <span class="material-symbols-outlined">straighten</span>
            <div>
              <span class="nav-bar-value">{{ navRemaining.distance }}</span>
              <span class="nav-bar-label">Осталось</span>
            </div>
          </div>
          <div class="nav-bar-item">
            <span class="material-symbols-outlined">schedule</span>
            <div>
              <span class="nav-bar-value">{{ navRemaining.duration }}</span>
              <span class="nav-bar-label">Время</span>
            </div>
          </div>
        </div>
        <button class="nav-stop-btn" @click="stopNavigation">
        
          <span>Завершить</span>
        </button>
      </div>
    </transition>

    <!-- Loading Overlay — анимация тигра при построении маршрута -->
    <transition name="loading-overlay-fade">
      <div v-if="isBuildingRoute" class="loading-overlay">
        <p class="loading-text">Маскот обегает все возможные маршруты 🐅</p>
        <div class="loading-video-wrapper">
          <video class="loading-tiger" autoplay loop muted playsinline>
            <source src="/assets/TIGER.mp4" type="video/mp4" />
          </video>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { config, placesApi, eventsApi } from '../config'
import { setNavigation, updateNavPosition, updateNavRemaining, navigationStore } from '../stores/navigation'

const emit = defineEmits(['close'])
const router = useRouter()
const mapRef = ref(null)
const ninjaBtnRef = ref(null)
let map = null
let markers = []
let isNinjaMode = ref(false)
let isTransitioning = ref(false)
let overlayStyle = ref({})

// Theme
const isDarkMode = ref(localStorage.getItem('theme') === 'dark')

// Ивенты — маркеры на карте
const events = ref([])
let eventMarkers = []
const selectedEvent = ref(null)

// ============================================
// 🔍 Фильтры
// ============================================

const showFilters = ref(false)

// ============================================
// 🔎 Поиск мест на карте
// ============================================

const placeSearchQuery = ref('')
const placeSearchResults = ref([])
const showPlaceSuggestions = ref(false)
let hidePlaceTimer = null

function onPlaceSearch() {
  const q = placeSearchQuery.value.trim().toLowerCase()
  if (!q) {
    placeSearchResults.value = []
    return
  }
  // Ищем только среди мест на карте, исключая my_spot
  placeSearchResults.value = places.value.filter(p =>
    p.category !== 'my_spot' &&
    (p.name.toLowerCase().includes(q) || p.address.toLowerCase().includes(q))
  )
}

function hidePlaceSuggestionsDelayed() {
  hidePlaceTimer = setTimeout(() => { showPlaceSuggestions.value = false }, 200)
}

function selectPlaceOnMap(place) {
  placeSearchQuery.value = place.name
  showPlaceSuggestions.value = false
  if (map) {
    map.setView([place.lat, place.lng], 16, { animate: true })
    // Подсвечиваем маркер — открываем popup
    const marker = markers.find(m => {
      const ll = m.getLatLng()
      return Math.abs(ll.lat - place.lat) < 0.0001 && Math.abs(ll.lng - place.lng) < 0.0001
    })
    if (marker) {
      openPlacePopup(place)
      marker.openPopup()
    }
  }
}

// ============================================
// 🗺 Маршрутизация
// ============================================

const showRouteForm = ref(false)
const isBuildingRoute = ref(false)

// Точки маршрута
const routeStartQuery = ref('')
const routeEndQuery = ref('')
const routeStartCoords = ref(null) // { lat, lng }
const routeEndId = ref(null)
const routeEndCoords = ref(null) // { lat, lng }

// Geocoding (Nominatim)
const startSuggestions = ref([])
const endSuggestions = ref([])
const showStartSuggestions = ref(false)
const showEndSuggestions = ref(false)
let geoSearchTimer = null

// Режим выбора точки на карте
const pickMode = ref(null) // 'start' | 'end' | 'event' | null
let prevCenter = null

// Линия маршрута на карте
let routeLineLayer = null
let userDotLayer = null // точка пользователя
const routeFast = ref(null)       // { geometry, distance, duration }
const routeSafety = ref(null)     // { geometry, distance, duration }
const activeRoute = ref('fast')   // 'fast' | 'safety'

// Навигация
const isNavigating = ref(false)
let watchId = null
const userPosition = ref(null) // { lat, lng }
const navRemaining = ref({ distance: '0 м', duration: '0 мин' })

// Можно построить маршрут
const canBuildRoute = computed(() => {
  return routeStartCoords.value && routeEndCoords.value
})

// Отфильтрованные места для "Куда"
const filteredEndPlaces = computed(() => {
  if (!routeEndQuery.value.trim()) return places.value
  const q = routeEndQuery.value.toLowerCase()
  return places.value.filter(p =>
    p.name.toLowerCase().includes(q) || p.address.toLowerCase().includes(q)
  )
})

// ============================================
// 🔍 Geocoding (Nominatim)
// ============================================

const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'

// Границы Орла для приоритизации поиска
const ORL_VIEWBOX = '35.95,53.05,36.25,52.88' // left,top,right,bottom

function geocode(query) {
  return fetch(
    `${NOMINATIM_URL}?q=${encodeURIComponent(query)}&format=json&limit=10&countrycodes=ru&accept-language=ru&viewbox=${ORL_VIEWBOX}&bounded=1&addressdetails=1`,
    { headers: { 'User-Agent': 'ShoulderToShoulder/1.0' } }
  ).then(r => r.json())
}

function parseNominatimResult(item) {
  // Nominatim возвращает { lat, lon, display_name, address, ... }
  const parts = item.display_name.split(',')

  // Если есть номер дома в address — включаем в название
  const addr = item.address || {}
  let name = parts[0].trim()
  if (addr.house_number && addr.road) {
    name = `${addr.road}, ${addr.house_number}`
  }

  // Адрес: город + остальное
  let address = parts.slice(1, 4).join(',').trim()
  if (addr.city || addr.town) address = `${addr.city || addr.town}, ${address}`

  return {
    name,
    address,
    lat: parseFloat(item.lat),
    lng: parseFloat(item.lon),
    type: item.type // house, road, residential, etc.
  }
}

// Поиск для "Откуда"
function onStartSearch() {
  const q = routeStartQuery.value.trim()
  if (q.length < 3) {
    startSuggestions.value = []
    return
  }
  clearTimeout(geoSearchTimer)
  geoSearchTimer = setTimeout(async () => {
    try {
      const results = await geocode(q)
      startSuggestions.value = results.map(parseNominatimResult)
    } catch (e) {
      if (config.isDebug) console.warn('Geocoding error:', e)
      startSuggestions.value = []
    }
  }, 400)
}

function selectStartAddress(s) {
  routeStartCoords.value = { lat: s.lat, lng: s.lng }
  routeStartQuery.value = s.name
  showStartSuggestions.value = false
  pickMode.value = null
}

function hideStartSuggestionsDelayed() {
  setTimeout(() => { showStartSuggestions.value = false }, 200)
}

// Поиск для "Куда"
function onEndSearch() {
  const q = routeEndQuery.value.trim()
  routeEndId.value = null
  routeEndCoords.value = null
  if (q.length < 3) {
    endSuggestions.value = []
    return
  }
  clearTimeout(geoSearchTimer)
  geoSearchTimer = setTimeout(async () => {
    try {
      const results = await geocode(q)
      endSuggestions.value = results.map(parseNominatimResult)
    } catch (e) {
      if (config.isDebug) console.warn('Geocoding error:', e)
      endSuggestions.value = []
    }
  }, 400)
}

function selectEndAddress(s) {
  routeEndCoords.value = { lat: s.lat, lng: s.lng }
  routeEndQuery.value = s.name
  showEndSuggestions.value = false
  pickMode.value = null
}

function hideEndSuggestionsDelayed() {
  setTimeout(() => { showEndSuggestions.value = false }, 200)
}

// Выбор места из базы
function selectEndPlace(place) {
  routeEndId.value = place.id
  routeEndQuery.value = place.name
  routeEndCoords.value = { lat: place.lat, lng: place.lng }
  showEndSuggestions.value = false
  pickMode.value = null
}

// ============================================
// 📍 Выбор точки на карте (иголка по центру)
// ============================================

function startPickMode(type) {
  pickMode.value = type
  prevCenter = map.getCenter()
  showRouteForm.value = false
  map.getContainer().style.cursor = 'crosshair'
}

// Вызывается из MainPage для режима выбора точки для Event
function setMapPickMode(type) {
  pickMode.value = type
  if (prevCenter) {
    map.setView(prevCenter, map.getZoom(), { animate: false })
    prevCenter = null
  }
  map.getContainer().style.cursor = 'crosshair'
}

function cancelPickMode() {
  const wasEvent = pickMode.value === 'event'
  pickMode.value = null
  if (prevCenter) {
    map.setView(prevCenter, map.getZoom(), { animate: false })
    prevCenter = null
  }
  map.getContainer().style.cursor = ''
  // Возвращаем форму (кроме режима event)
  if (!wasEvent) {
    showRouteForm.value = true
  }
}

async function confirmPickMode() {
  const center = map.getCenter()
  const lat = center.lat
  const lng = center.lng

  if (pickMode.value === 'start') {
    routeStartCoords.value = { lat, lng }
    routeStartQuery.value = `${lat.toFixed(5)}, ${lng.toFixed(5)}`
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&accept-language=ru`,
        { headers: { 'User-Agent': 'ShoulderToShoulder/1.0' } }
      )
      const data = await res.json()
      if (data.display_name) {
        const parts = data.display_name.split(',').slice(0, 3).join(',').trim()
        routeStartQuery.value = parts
      }
    } catch (e) {
      if (config.isDebug) console.warn('Reverse geocoding error:', e)
    }
  } else if (pickMode.value === 'end') {
    routeEndCoords.value = { lat, lng }
    routeEndQuery.value = `${lat.toFixed(5)}, ${lng.toFixed(5)}`
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&accept-language=ru`,
        { headers: { 'User-Agent': 'ShoulderToShoulder/1.0' } }
      )
      const data = await res.json()
      if (data.display_name) {
        const parts = data.display_name.split(',').slice(0, 3).join(',').trim()
        routeEndQuery.value = parts
      }
    } catch (e) {
      if (config.isDebug) console.warn('Reverse geocoding error:', e)
    }
  } else if (pickMode.value === 'event') {
    // Режим выбора места для Event
    let address = `${lat.toFixed(5)}, ${lng.toFixed(5)}`
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&accept-language=ru`,
        { headers: { 'User-Agent': 'ShoulderToShoulder/1.0' } }
      )
      const data = await res.json()
      if (data.display_name) {
        address = data.display_name.split(',').slice(0, 3).join(',').trim()
      }
    } catch (e) {
      if (config.isDebug) console.warn('Reverse geocoding error:', e)
    }
    // Сохраняем данные и закрываем карту → MainPage откроет модалку
    try {
      localStorage.setItem('shoulder_pending_event_location', JSON.stringify({ lat, lng, address }))
      if (config.isDebug) console.log('📍 Event location saved:', { lat, lng, address })
    } catch (e) {
      if (config.isDebug) console.warn('Failed to save event location:', e)
    }
    emit('close')
    return
  }

  pickMode.value = null
  map.getContainer().style.cursor = ''
  // Возвращаем форму (кроме режима event — там модалка откроется из setEventLocation)
  if (pickMode.value !== 'event') {
    showRouteForm.value = true
  }
}

// Геолокация
async function useMyLocation() {
  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000
      })
    })
    const { latitude, longitude } = pos.coords
    routeStartCoords.value = { lat: latitude, lng: longitude }
    routeStartQuery.value = 'Моё местоположение'
  } catch (e) {
    if (config.isDebug) console.warn('Геолокация недоступна')
    // Fallback: центр Орла
    routeStartCoords.value = { lat: 52.9651, lng: 36.0785 }
    routeStartQuery.value = 'Центр города'
  }
}

// Построить маршрут: GET /route/safe?start_lat=&start_lng=&end_lat=&end_lng=
async function buildRoute() {
  if (!canBuildRoute.value) return

  isBuildingRoute.value = true

  const start = routeStartCoords.value
  const end = routeEndCoords.value
  let routeBuilt = false

  // 1. Пробуем свой бэкэнд — GET с query-параметрами
  try {
    const url = `${placesApi('/route/safe')}?start_lat=${start.lat}&start_lng=${start.lng}&end_lat=${end.lat}&end_lng=${end.lng}`
    if (config.isDebug) console.log('🗺 Запрос маршрута:', url)

    const res = await fetch(url)
    const data = await res.json()

    if (config.isDebug) console.log('📦 Ответ бэка:', data)

    // Бэк возвращает { shortest_route: {...}, safest_route: {...}, ... }
    const fast = formatRoute(data.shortest_route)
    const safety = formatRoute(data.safest_route)

    if (fast && safety) {
      routeFast.value = fast
      routeSafety.value = safety
      activeRoute.value = 'fast'
      showRouteForm.value = false
      drawRoute('fast')
      routeBuilt = true
    } else {
      if (config.isDebug) console.warn('⚠️ Бэк вернул пустые маршруты:', data)
    }
  } catch (e) {
    if (config.isDebug) console.warn('buildRoute: бэк недоступен, fallback на OSRM', e)
  }

  // 2. Fallback: прямой запрос к OSRM
  if (!routeBuilt) {
    try {
      const url = `${config.osrmBaseURL}/route/v1/foot/${start.lng},${start.lat};${end.lng},${end.lat}?steps=true&geometries=geojson&overview=full`
      if (config.isDebug) console.log('🗺 OSRM запрос:', url)

      const res = await fetch(url)
      const data = await res.json()

      if (data.code === 'Ok' && data.routes?.length > 0) {
        const r = data.routes[0]
        const osrmCoords = r.geometry.coordinates
        const coords = osrmCoords.map(c => [c[1], c[0]])
        const distM = Math.round(r.distance)
        const durMin = Math.round(r.duration / 60)

        routeFast.value = {
          geometry: r.geometry,
          coords,
          distance: distM >= 1000 ? `${(distM / 1000).toFixed(1)} км` : `${distM} м`,
          duration: durMin >= 60 ? `${Math.floor(durMin / 60)}ч ${durMin % 60}м` : `${durMin} мин`,
          _rawDistance: distM,
          _rawDuration: durMin
        }
        routeSafety.value = { ...routeFast.value }
        activeRoute.value = 'fast'
        showRouteForm.value = false
        drawRoute('fast')
        routeBuilt = true
      } else {
        if (config.isDebug) console.warn('⚠️ OSRM не вернул маршрут:', data)
      }
    } catch (e) {
      if (config.isDebug) console.warn('buildRoute: OSRM недоступен', e)
    }
  }

  // Если ничего не получилось — не скрываем форму
  if (!routeBuilt && config.isDebug) {
    console.warn('❌ Не удалось построить ни один маршрут')
  }

  isBuildingRoute.value = false
}

// Форматируем ответ бэка
// Наш формат: { coordinates: [{lat, lng}, ...], distance_m, risk_score, ... }
// OSRM формат: { geometry: {type: 'LineString', coordinates: [[lng, lat], ...]}, distance, duration }
function formatRoute(raw) {
  if (!raw) return null

  let coords
  let distM = 0
  let durMin = 0

  if (raw.coordinates && raw.coordinates.length > 0 && raw.coordinates[0].lat !== undefined) {
    // Наш формат: [{lat, lng}, ...]
    coords = raw.coordinates.map(c => [c.lat, c.lng])
    distM = Math.round(raw.distance_m || 0)
    durMin = Math.round(distM * 60 / 5000) // ~5 км/ч
  } else if (raw.geometry && raw.geometry.coordinates) {
    // OSRM формат: GeoJSON LineString
    coords = raw.geometry.coordinates.map(c => [c[1], c[0]])
    distM = Math.round(raw.distance || 0)
    durMin = Math.round((raw.duration || 0) / 60)
  } else {
    return null
  }

  return {
    geometry: { type: 'LineString', coordinates: coords.map(c => [c[1], c[0]]) },
    coords,
    distance: distM >= 1000 ? `${(distM / 1000).toFixed(1)} км` : `${distM} м`,
    duration: durMin >= 60 ? `${Math.floor(durMin / 60)}ч ${durMin % 60}м` : `${durMin} мин`,
    _rawDistance: distM,
    _rawDuration: durMin
  }
}

// Переключение маршрута
function switchRoute(type) {
  activeRoute.value = type
  drawRoute(type)
}

// Отрисовка выбранного маршрута
function drawRoute(type) {
  const route = type === 'fast' ? routeFast.value : routeSafety.value
  if (!route) return

  // Если есть готовые coords (наш формат) — используем
  let coords = route.coords
  if (!coords) {
    // Fallback: парсим GeoJSON
    const geometry = route.geometry
    if (!geometry || !geometry.coordinates) return
    coords = geometry.coordinates.map(c => [c[1], c[0]])
  }

  const color = type === 'fast' ? '#ea580c' : '#16a34a'

  // Полная очистка всех возможных слоёв
  if (routeLineLayer) {
    if (routeLineLayer.completed && routeLineLayer.remaining) {
      map.removeLayer(routeLineLayer.completed)
      map.removeLayer(routeLineLayer.remaining)
    } else {
      map.removeLayer(routeLineLayer)
    }
    routeLineLayer = null
  }

  routeLineLayer = L.polyline(
    coords,
    { color, weight: 5, opacity: 0.9, smoothFactor: 1 }
  ).addTo(map)

  map.fitBounds(routeLineLayer.getBounds(), { padding: [60, 60] })
}

function clearRoute() {
  // Останавливаем навигацию если активна
  if (isNavigating.value) {
    stopNavigation()
    return
  }

  // Очищаем слои маршрута (может быть объект или простой polyline)
  if (routeLineLayer) {
    if (routeLineLayer.completed && routeLineLayer.remaining) {
      // Навигационный режим: { completed, remaining }
      map.removeLayer(routeLineLayer.completed)
      map.removeLayer(routeLineLayer.remaining)
    } else {
      // Простой полигон
      map.removeLayer(routeLineLayer)
    }
    routeLineLayer = null
  }
  routeFast.value = null
  routeSafety.value = null
  activeRoute.value = 'fast'
  routeStartQuery.value = ''
  routeEndQuery.value = ''
  routeStartCoords.value = null
  routeEndId.value = null
  routeEndCoords.value = null
  pickMode.value = null
  // Возвращаем кнопку "Быстрый старт"
  showRouteForm.value = false
}

// ============================================
// 🧭 Навигация (GPS + перерисовка маршрута)
// ============================================

function startNavigation() {
  isNavigating.value = true

  // Сразу показываем полное расстояние маршрута
  const route = activeRoute.value === 'fast' ? routeFast.value : routeSafety.value
  if (route) {
    navRemaining.value = { distance: route.distance, duration: route.duration }
  }

  // Синхронизируем с общим стором
  setNavigation(true, {
    activeRoute: activeRoute.value,
    routeCoords: route?.coords || [],
    userPosition: null,
    navRemaining: navRemaining.value
  })

  // Запускаем GPS-отслеживание
  if ('geolocation' in navigator) {
    watchId = navigator.geolocation.watchPosition(
      (pos) => onUserPositionUpdate(pos),
      (err) => { if (config.isDebug) console.warn('GPS error:', err) },
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
    )
  }

  // Получаем начальную позицию
  navigator.geolocation.getCurrentPosition(
    (pos) => onUserPositionUpdate(pos),
    () => {},
    { enableHighAccuracy: true }
  )
}

function onUserPositionUpdate(pos) {
  const lat = pos.coords.latitude
  const lng = pos.coords.longitude
  userPosition.value = { lat, lng }

  // Синхронизируем с общим стором
  updateNavPosition({ lat, lng })

  // Обновляем маркер пользователя
  updateUserMarker()

  // Перерисовываем маршрут (пройденный/оставшийся)
  redrawRouteWithProgress()

  // Считаем оставшееся расстояние
  updateRemainingDistance()
}

function updateUserMarker() {
  if (!userPosition.value || !map) return

  if (userDotLayer) map.removeLayer(userDotLayer)

  userDotLayer = L.circleMarker(
    [userPosition.value.lat, userPosition.value.lng],
    {
      radius: 8,
      fillColor: '#3b82f6',
      color: '#fff',
      weight: 3,
      opacity: 1,
      fillOpacity: 0.9
    }
  ).addTo(map)
}

function redrawRouteWithProgress() {
  const route = activeRoute.value === 'fast' ? routeFast.value : routeSafety.value
  if (!route || !route.coords || !userPosition.value) return

  const routeCoords = route.coords
  const userLat = userPosition.value.lat
  const userLng = userPosition.value.lng

  // Находим ближайшую точку на маршруте к пользователю
  let closestIdx = 0
  let minDist = Infinity
  for (let i = 0; i < routeCoords.length; i++) {
    const d = haversineDistance(userLat, userLng, routeCoords[i][0], routeCoords[i][1])
    if (d < minDist) {
      minDist = d
      closestIdx = i
    }
  }

  // Пройденный путь (серый) — если пользователь уже сдвинулся
  const completedCoords = routeCoords.slice(0, closestIdx + 1)
  // Оставшийся путь (цвет маршрута)
  const remainingCoords = routeCoords.slice(closestIdx)

  // Удаляем старые слои
  if (routeLineLayer) {
    if (routeLineLayer.completed && routeLineLayer.remaining) {
      map.removeLayer(routeLineLayer.completed)
      map.removeLayer(routeLineLayer.remaining)
    }
    routeLineLayer = null
  }

  const routeColor = activeRoute.value === 'fast' ? '#ea580c' : '#16a34a'

  // Рисуем пройденный путь (серый) — только если есть что рисовать
  if (completedCoords.length > 1) {
    const completedLine = L.polyline(completedCoords, {
      color: '#9ca3af',
      weight: 5,
      opacity: 0.6,
      smoothFactor: 1
    }).addTo(map)

    const remainingLine = L.polyline(remainingCoords, {
      color: routeColor,
      weight: 5,
      opacity: 0.9,
      smoothFactor: 1
    }).addTo(map)

    routeLineLayer = { completed: completedLine, remaining: remainingLine }
  } else {
    // Ещё не сдвинулся — рисуем полный маршрут цветным
    routeLineLayer = L.polyline(routeCoords, {
      color: routeColor,
      weight: 5,
      opacity: 0.9,
      smoothFactor: 1
    }).addTo(map)
  }
}

function updateRemainingDistance() {
  const route = activeRoute.value === 'fast' ? routeFast.value : routeSafety.value
  if (!route || !route.coords || !userPosition.value) return

  const routeCoords = route.coords
  const userLat = userPosition.value.lat
  const userLng = userPosition.value.lng

  // Находим ближайшую точку
  let closestIdx = 0
  let minDist = Infinity
  for (let i = 0; i < routeCoords.length; i++) {
    const d = haversineDistance(userLat, userLng, routeCoords[i][0], routeCoords[i][1])
    if (d < minDist) {
      minDist = d
      closestIdx = i
    }
  }

  // Считаем оставшееся расстояние по оставшимся точкам
  let remainingM = 0
  for (let i = closestIdx; i < routeCoords.length - 1; i++) {
    remainingM += haversineDistance(
      routeCoords[i][0], routeCoords[i][1],
      routeCoords[i + 1][0], routeCoords[i + 1][1]
    )
  }

  const distM = Math.round(remainingM)
  const durMin = Math.round(distM * 60 / 5000)

  const remaining = {
    distance: distM >= 1000 ? `${(distM / 1000).toFixed(1)} км` : `${distM} м`,
    duration: durMin >= 60 ? `${Math.floor(durMin / 60)}ч ${durMin % 60}м` : `${durMin} мин`
  }

  navRemaining.value = remaining

  // Синхронизируем с общим стором
  updateNavRemaining(remaining)
}

// Формула Haversine для расстояния между двумя точками (метры)
function haversineDistance(lat1, lng1, lat2, lng2) {
  const R = 6371000
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

function stopNavigation() {
  isNavigating.value = false

  // Останавливаем GPS
  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId)
    watchId = null
  }

  // Удаляем маркер пользователя
  if (userDotLayer) {
    map.removeLayer(userDotLayer)
    userDotLayer = null
  }

  userPosition.value = null
  navRemaining.value = { distance: '0 м', duration: '0 мин' }

  // Очищаем слои маршрута (completed + remaining или простой polyline)
  if (routeLineLayer) {
    if (routeLineLayer.completed && routeLineLayer.remaining) {
      map.removeLayer(routeLineLayer.completed)
      map.removeLayer(routeLineLayer.remaining)
    } else {
      map.removeLayer(routeLineLayer)
    }
    routeLineLayer = null
  }

  // Полностью очищаем маршрут — возвращаемся к начальному состоянию
  routeFast.value = null
  routeSafety.value = null
  activeRoute.value = 'fast'
  routeStartQuery.value = ''
  routeEndQuery.value = ''
  routeStartCoords.value = null
  routeEndId.value = null
  routeEndCoords.value = null
  pickMode.value = null
  showRouteForm.value = false

  // Очищаем общий стор навигации
  setNavigation(false)
}

// ============================================

const activityTypes = [
  { key: 'running', emoji: '🏃', label: 'Бег' },
  { key: 'strength', emoji: '🏋️', label: 'Силовая' },
  { key: 'yoga', emoji: '🧘', label: 'Йога' },
  { key: 'workout', emoji: '💪', label: 'Воркаут' },
  { key: 'other', emoji: '🎯', label: 'Другое' }
]

const noiseLevels = [
  { key: 'quiet', emoji: '🤫', label: 'Тихо' },
  { key: 'moderate', emoji: '😐', label: 'Средне' },
  { key: 'loud', emoji: '📢', label: 'Шумно' }
]

const filters = ref({
  activityType: '',
  noiseLevel: '',
  lit: false,
  lockers: false,
  benches: false,
  anonymous: false
})

// Места с бэкенда
const places = ref([])

const filteredPlacesCount = computed(() => {
  return places.value.length
})

function resetFilters() {
  filters.value = {
    activityType: '',
    noiseLevel: '',
    lit: false,
    lockers: false,
    benches: false,
    anonymous: false
  }
}

async function applyFilters() {
  await fetchPlaces()
  // Чтобы ивенты не пропадали после изменения фильтров/places
  if (isNinjaMode.value) {
    await fetchEvents()
    addEventMarkers()
  }
  showFilters.value = false
}


// Получить места с бэнда (с фильтрами)
async function fetchPlaces() {
  if (config.isDebug) console.log('🗺 fetchPlaces: запрос к API, фильтры:', JSON.stringify(filters.value))
  try {
    const url = placesApi('/places')
    if (config.isDebug) console.log('🗺 fetchPlaces URL:', url)

    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()

    if (config.isDebug) console.log('📦 fetchPlaces ответ:', JSON.stringify(data, null, 2))

    // Бэк может вернуть:
    // 1. { "places": [...] } — массив мест
    // 2. { "place": {...} } — одно место
    // 3. [...] — просто массив
    // Поддерживаем все форматы
    let rawPlaces = []
    if (Array.isArray(data)) {
      rawPlaces = data
    } else if (data.places && Array.isArray(data.places)) {
      rawPlaces = data.places
    } else if (data.place && typeof data.place === 'object') {
      rawPlaces = [data.place]
    }

    if (config.isDebug) console.log('📍 Получено мест с бэка:', rawPlaces.length)

    // Маппим ответ бэкенда → внутренний формат, скипаем невалидные
    const validActivities = ['running', 'strength', 'yoga', 'workout', 'other']

    const mapped = rawPlaces
      .filter(p => {
        // Обязательные поля: id, name, lat, lon (или lng)
        const hasId = p && (p.id || p.id === 0)
        const hasName = p && typeof p.name === 'string' && p.name.trim()
        const hasLat = p && typeof p.lat === 'number'
        const hasLon = p && typeof p.lon === 'number'
        const hasLng = p && typeof p.lng === 'number'

        if (!hasId || !hasName || (!hasLat && !hasLng)) {
          if (config.isDebug) console.warn('fetchPlaces: скипнуто невалидное место', p)
          return false
        }
        return true
      })
      .map(p => {
        // Конвертируем noise_level (0-10) → string
        const noiseNum = typeof p.noise_level === 'number' ? p.noise_level : 5
        const noiseLevel = noiseNum <= 3 ? 'quiet' : noiseNum <= 6 ? 'moderate' : 'loud'

        // Конвертируем light_availability (0-10) → boolean
        const lit = typeof p.light_availability === 'number' ? p.light_availability >= 5 : false

        // conveniences → lockers/benches
        const hasConveniences = p.conveniences_availability === true

        // activity_type → валидный ключ
        const activityType = validActivities.includes(p.activity_type) ? p.activity_type : 'other'

        // image может быть null
        const image = p.image || null
        // gallery может быть null или не массивом
        const gallery = Array.isArray(p.gallery) ? p.gallery : []

        return {
          id: p.id,
          name: p.name,
          description: typeof p.description === 'string' ? p.description : '',
          lat: p.lat,
          lng: p.lon || p.lng || 0, // lon от бэка, lng как fallback
          rating: typeof p.rating === 'number' ? p.rating : 0,
          emoji: typeof p.emoji === 'string' ? p.emoji : '📍',
          category: typeof p.category === 'string' ? p.category : 'other',
          image: image,
          gallery: gallery,
          address: typeof p.address === 'string' ? p.address : '',
          activityType: activityType,
          noiseLevel: noiseLevel,
          lit: lit,
          lockers: hasConveniences,
          benches: hasConveniences,
          anonymous: p.is_anonymous === true
        }
      })

    if (config.isDebug) console.log('✅ mapped мест (до фильтрации):', mapped.length)

    // === ЛОКАЛЬНАЯ ФИЛЬТРАЦИЯ ===
    // Исключаем my_spot — они отображаются как ивенты, не как площадки
    const filtered = mapped.filter(p => {
      if (p.category === 'my_spot') return false
      if (filters.value.activityType && p.activityType !== filters.value.activityType) return false
      if (filters.value.noiseLevel && p.noiseLevel !== filters.value.noiseLevel) return false
      if (filters.value.lit && !p.lit) return false
      if (filters.value.lockers && !p.lockers) return false
      if (filters.value.benches && !p.benches) return false
      if (filters.value.anonymous && !p.anonymous) return false
      return true
    })

    if (config.isDebug) console.log('✅ после фильтрации:', filtered.length)

    places.value = filtered
    addPlaceMarkers()
  } catch (e) {
    if (config.isDebug) console.warn('fetchPlaces: API недоступен', e)
    places.value = []
    addPlaceMarkers()
  }
}

// Режим ниндзя — показать ивенты, скрыть площадки
const toggleNinjaMode = async () => {
  if (isTransitioning.value) return
  isTransitioning.value = true

  const btn = ninjaBtnRef.value
  const rect = btn.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  const maxRadius = Math.sqrt(
    Math.pow(window.innerWidth, 2) + Math.pow(window.innerHeight, 2)
  )

  const wasNinja = isNinjaMode.value

  if (!wasNinja) {
    // Вход в режим ниндзя: круг расширяется
    overlayStyle.value = {
      background: 'rgba(0, 0, 0, 0.7)',
      clipPath: `circle(0px at ${centerX}px ${centerY}px)`,
      transition: 'none'
    }

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        overlayStyle.value = {
          background: 'rgba(0, 0, 0, 0.7)',
          clipPath: `circle(${maxRadius}px at ${centerX}px ${centerY}px)`,
          transition: 'clip-path 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
        }
      })
    })

    setTimeout(async () => {
      isNinjaMode.value = true
      // Инвертируем карту для тёмного режима
      if (map) {
        map.getContainer().style.filter = 'invert(1) hue-rotate(180deg) brightness(0.8) contrast(1.2)'
      }
      // Скрываем маркеры площадок
      removePlaceMarkers()
      // Загружаем и показываем ивенты
      await fetchEvents()
      addEventMarkers()
      setTimeout(() => {
        isTransitioning.value = false
        overlayStyle.value = {}
      }, 100)
    }, 400)

  } else {
    // Выход из режима ниндзя
    overlayStyle.value = {
      background: 'rgba(0, 0, 0, 0.7)',
      clipPath: `circle(${maxRadius}px at ${centerX}px ${centerY}px)`,
      transition: 'none'
    }

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        overlayStyle.value = {
          background: 'rgba(0, 0, 0, 0.7)',
          clipPath: `circle(0px at ${centerX}px ${centerY}px)`,
          transition: 'clip-path 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
        }
      })
    })

    isNinjaMode.value = false
    // Сбрасываем фильтр карты
    if (map) {
      map.getContainer().style.filter = 'none'
    }
    // Скрываем маркеры ивентов
    removeEventMarkers()
    // Показываем маркеры площадок
    addPlaceMarkers()

    setTimeout(() => {
      isTransitioning.value = false
      overlayStyle.value = {}
    }, 400)
  }
}

// Размер маркера в зависимости от зума
const getMarkerSize = (zoom) => {
  if (zoom <= 12) return { size: 28, font: 14, border: 2 }
  if (zoom <= 14) return { size: 36, font: 18, border: 2 }
  if (zoom <= 16) return { size: 44, font: 22, border: 2 }
  return { size: 52, font: 26, border: 3 }
}

// Создание маркера площадки
const createPlaceMarker = (place) => {
  const zoom = map.getZoom()
  const { size, font, border } = getMarkerSize(zoom)
  const bg = '#fff'
  const textColor = '#1c1917'
  // При инверсии карты маркеры тоже инвертируются — добавляем контр-фильтр
  // Но только в режиме ниндзя! В обычном режиме фильтра не должно быть
  const markerFilter = isNinjaMode.value ? 'invert(1) hue-rotate(180deg)' : 'none'

  const icon = L.divIcon({
    className: 'custom-marker',
    html: `<div class="marker-emoji" style="
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      background: ${bg};
      color: ${textColor};
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: ${font}px;
      border: ${border}px solid #ea580c;
      cursor: pointer;
      user-select: none;
      filter: ${markerFilter};
    ">${place.emoji}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2]
  })

  const marker = L.marker([place.lat, place.lng], { icon })
    .addTo(map)
    .on('click', () => openPlacePopup(place))

  return marker
}

// Открытие popup с информацией о месте
const openPlacePopup = (place) => {
  map.closePopup()

  const popupContent = `
    <div class="place-popup">
      <div class="popup-gallery">
        ${place.gallery?.map((img, i) => `
          <div class="gallery-item ${i === 0 ? 'gallery-main' : ''}">
            <img src="${img}" alt="${place.name}" />
          </div>
        `).join('') || ''}
      </div>
      <div class="popup-info">
        <div class="popup-header">
          <div class="popup-title">
            <span class="popup-emoji">${place.emoji}</span>
            <div>
              <h3>${place.name}</h3>
              <p class="popup-address">${place.address || ''}</p>
            </div>
          </div>
          <div class="popup-rating">
            <span class="star">★</span>
            <span>${place.rating || '—'}</span>
          </div>
        </div>
        <p class="popup-desc">${place.description || ''}</p>
        <button class="popup-btn" data-place-id="${place.id}" data-place-name="${place.name}" data-place-lat="${place.lat}" data-place-lng="${place.lng}">
          <span class="material-symbols-outlined">directions_run</span>
          <span>Маршрут</span>
        </button>
      </div>
    </div>
  `

  const popup = L.popup({
    closeButton: true,
    autoPan: true,
    className: 'custom-popup',
    offset: [0, -10]
  })
    .setLatLng([place.lat, place.lng])
    .setContent(popupContent)
    .openOn(map)

  // Обработчик кнопки "Маршрут" после рендера popup
  setTimeout(() => {
    // Контр-фильтр для popup
    const popupEl = document.querySelector('.custom-popup .leaflet-popup-content-wrapper')
    if (popupEl) {
      popupEl.style.filter = 'invert(1) hue-rotate(180deg)'
    }
    const tipEl = document.querySelector('.custom-popup .leaflet-popup-tip')
    if (tipEl) {
      tipEl.style.filter = 'invert(1) hue-rotate(180deg)'
    }

    const btn = document.querySelector(`.popup-btn[data-place-id="${place.id}"]`)
    if (btn) {
      btn.addEventListener('click', () => {
        map.closePopup()
        openRouteToPlace(place)
      })
    }
  }, 100)
}

// Открыть форму навигации с подставленным местом
function openRouteToPlace(place) {
  // Открываем форму маршрута
  showRouteForm.value = true

  // Подставляем место в поле "Куда"
  routeEndCoords.value = { lat: place.lat, lng: place.lng }
  routeEndQuery.value = place.name
  routeEndId.value = place.id
}

// Добавление маркеров на карту
const addPlaceMarkers = () => {
  removePlaceMarkers()
  markers = places.value.map(place => createPlaceMarker(place))
}

// ============================================
// 🎯 Ивенты — режим ниндзя
// ============================================

// Загрузка ивентов с бэка
async function fetchEvents() {
  try {
    const url = eventsApi('/events')
    if (config.isDebug) console.log('🎯 fetchEvents URL:', url)

    const res = await fetch(url)
    const data = await res.json()

    if (config.isDebug) console.log('📦 fetchEvents ответ:', JSON.stringify(data, null, 2))

    let rawEvents = []
    if (Array.isArray(data)) {
      rawEvents = data
    } else if (data.events && Array.isArray(data.events)) {
      rawEvents = data.events
    } else if (data.event && typeof data.event === 'object') {
      rawEvents = [data.event]
    }

    // Маппинг ивентов
    events.value = rawEvents
      .filter(e => e && e.id && e.name && typeof e.lat === 'number' && typeof e.lon === 'number')
      .map(e => ({
        id: e.id,
        name: e.name,
        description: e.description || '',
        lat: e.lat,
        lng: e.lon,
        emoji: e.emoji || '📍',
        time: e.time || e.start_time || '',
        date: e.date || e.start_date || '',
        level: e.level || 'Любой',
        type: e.type || e.activity_type || '',
        participants: e.participants || 0,
        maxParticipants: e.max_participants || e.maxParticipants || 0,
        organizer: e.organizer || e.organizer_name || '',
        quietCompanion: e.quiet_companion || e.quietCompanion || false,
        address: e.address || '',
      }))

    if (config.isDebug) console.log('🎯 Загружено ивентов:', events.value.length)
  } catch (e) {
    if (config.isDebug) console.warn('fetchEvents: API недоступен, использую моковые данные', e)
    // Fallback — моковые ивенты
    events.value = [
      {
        id: 101, name: 'Утренняя пробежка',
        description: 'Лёгкий бег в парке для всех желающих',
        lat: 52.9690, lng: 36.0820, emoji: '🏃',
        time: '07:00', date: '2026-04-11',
        level: 'Новичок', type: 'running',
        participants: 5, maxParticipants: 10,
        organizer: 'Алексей', quietCompanion: false,
        address: 'Парк Победы, Орёл'
      },
      {
        id: 102, name: 'Йога на закате',
        description: 'Спокойная практика для расслабления',
        lat: 52.9650, lng: 36.0790, emoji: '🧘',
        time: '19:00', date: '2026-04-11',
        level: 'Средний', type: 'yoga',
        participants: 3, maxParticipants: 8,
        organizer: 'Мария', quietCompanion: true,
        address: 'Набережная, Орёл'
      },
      {
        id: 103, name: 'Силовая тренировка',
        description: 'Воркаут на турниках и брусьях',
        lat: 52.9620, lng: 36.0740, emoji: '💪',
        time: '18:00', date: '2026-04-12',
        level: 'Профи', type: 'strength',
        participants: 4, maxParticipants: 6,
        organizer: 'Дмитрий', quietCompanion: false,
        address: 'Стадион «Центральный», Орёл'
      }
    ]
  }
}

// Создание маркера ивента
const createEventMarker = (event) => {
  const zoom = map.getZoom()
  const { size, font, border } = getMarkerSize(zoom)
  // Контр-фильтр чтобы маркеры не инвертировались
  const markerFilter = 'invert(1) hue-rotate(180deg)'

  const icon = L.divIcon({
    className: 'custom-marker event-marker',
    html: `
      <div class="marker-emoji" style="
        width: ${size}px;
        height: ${size}px;
        font-size: ${font}px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #ea580c;
        border-radius: 50%;
        border: ${border}px solid #fff;
        box-shadow: 0 3px 12px rgba(234, 88, 12, 0.5);
        color: #fff;
        filter: ${markerFilter};
      ">${event.emoji || '📍'}</div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2]
  })

  const marker = L.marker([event.lat, event.lng], { icon })

  // Popup с информацией об ивенте
  const popupContent = `
    <div class="event-popup">
      <div class="event-popup-header">
        <span class="event-popup-emoji">${event.emoji || '📍'}</span>
        <h3 class="event-popup-title">${event.name}</h3>
      </div>
      ${event.description ? `<p class="event-popup-desc">${event.description}</p>` : ''}
      <div class="event-popup-info">
        ${event.time ? `<div><span class="material-symbols-outlined">schedule</span> ${event.time}${event.date ? ` • ${event.date}` : ''}</div>` : ''}
        ${event.address ? `<div><span class="material-symbols-outlined">place</span> ${event.address}</div>` : ''}
        ${event.type ? `<div><span class="material-symbols-outlined">sports</span> ${event.type}</div>` : ''}
        ${event.level ? `<div><span class="material-symbols-outlined">trending_up</span> ${event.level}</div>` : ''}
        ${event.organizer ? `<div><span class="material-symbols-outlined">person</span> ${event.organizer}</div>` : ''}
        <div><span class="material-symbols-outlined">group</span> ${event.participants}/${event.maxParticipants} участников</div>
        ${event.quietCompanion ? '<div class="event-quiet-tag">🤫 Тихий компаньон</div>' : ''}
      </div>
    </div>
  `

  marker.bindPopup(popupContent, {
    maxWidth: 280,
    className: 'event-popup-wrapper'
  })

  // Контр-фильтр для popup
  marker.on('popupopen', () => {
    setTimeout(() => {
      const popupEl = document.querySelector('.event-popup-wrapper .leaflet-popup-content-wrapper')
      if (popupEl) {
        popupEl.style.filter = 'invert(1) hue-rotate(180deg)'
      }
      const tipEl = document.querySelector('.event-popup-wrapper .leaflet-popup-tip')
      if (tipEl) {
        tipEl.style.filter = 'invert(1) hue-rotate(180deg)'
      }
    }, 10)
  })

  return marker
}

// Добавление маркеров ивентов
const addEventMarkers = () => {
  removeEventMarkers()
  eventMarkers = events.value.map(event => {
    const marker = createEventMarker(event)
    marker.addTo(map)
    return marker
  })
}

// Удаление маркеров ивентов
const removeEventMarkers = () => {
  eventMarkers.forEach(m => map.removeLayer(m))
  eventMarkers = []
}

// ============================================

// Перерисовка маркеров при зуме
const onMapZoom = () => {
  if (isNinjaMode.value) {
    addEventMarkers()
  } else {
    addPlaceMarkers()
  }
}

// Удаление маркеров (для очистки)
const removePlaceMarkers = () => {
  markers.forEach(m => map.removeLayer(m))
  markers = []
}

onMounted(async () => {
  if (config.isDebug) console.log('🗺 MapLight onMounted')
  await nextTick()

  // Экспортируем функции
  window.__setMapPickMode = setMapPickMode

  // Чтобы маркеры ивентов (my spots / участия) не пропадали после загрузки places,
  // синхронизируем режим с ниндзя/обычным и перерисовываем при получении точек.
  // Важно: после fetchPlaces() onMapZoom вызывает addPlaceMarkers(),
  // но мы хотим, чтобы ивенты тоже показывались.
  // Отображение ивентов по факту: где-то после загрузки places вызывается onMapZoom,
  // которое может перерисовать слой ивентов (или скрыть их).
  // В нашей логике события показываются всегда, когда isNinjaMode === true.
  const syncEventMarkers = () => {
    if (!map) return
    if (isNinjaMode.value) {
      addEventMarkers()
    } else {
      // В обычном режиме события не отрисовываем.
      removeEventMarkers()
    }
  }


  if (mapRef.value && !map) {

    map = L.map(mapRef.value, {
      zoomControl: false
    }).setView([52.9651, 36.0785], 14)

    // Перерисовываем места при изменении places.value
    watch(
      () => places.value,
      () => {
        if (!map) return
        if (!isNinjaMode.value) {
          addPlaceMarkers()
          // критично: при изменении places слой ивентов мог сброситься
          // поэтому синхронизируем его обратно по флагу режима
          syncEventMarkers()
        }
      },
      { deep: false }
    )



    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(map)

    L.control.zoom({
      position: 'topleft'
    }).addTo(map)

    // Перерисовка маркеров при зуме
    map.on('zoomend', onMapZoom)

    await fetchPlaces()

    // Если навигация уже активна — восстанавливаем состояние
    if (navigationStore.isNavigating && navigationStore.routeCoords.length > 0) {
      if (config.isDebug) console.log('MapLight onMounted: restoring navigation state')
      restoreNavigation()
    }

    setTimeout(() => map.invalidateSize(), 100)
  }
})

// При уничтожении компонента — очищаем карту
onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
    markers = []
  }
})

// Восстановление навигации при повторном открытии карты
function restoreNavigation() {
  if (!navigationStore.isNavigating || !navigationStore.routeCoords.length) return

  isNavigating.value = true

  // Создаём фейковые routeFast/routeSafety для совместимости с drawRoute
  const coords = navigationStore.routeCoords
  const fakeRoute = {
    geometry: { type: 'LineString', coordinates: coords.map(c => [c[1], c[0]]) },
    coords,
    distance: navigationStore.navRemaining.distance,
    duration: navigationStore.navRemaining.duration,
    _rawDistance: 0,
    _rawDuration: 0
  }

  routeFast.value = fakeRoute
  routeSafety.value = fakeRoute
  activeRoute.value = navigationStore.activeRoute
  navRemaining.value = navigationStore.navRemaining

  if (navigationStore.userPosition) {
    userPosition.value = navigationStore.userPosition
  }

  // Рисуем маршрут
  drawRoute(activeRoute.value)

  // Перезапускаем GPS
  if ('geolocation' in navigator) {
    watchId = navigator.geolocation.watchPosition(
      (pos) => onUserPositionUpdate(pos),
      (err) => { if (config.isDebug) console.warn('GPS error:', err) },
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
    )
  }
}
</script>

<style scoped>
.map-light {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #f8f9fa;
  font-family: 'Inter', sans-serif;
  color: var(--on-surface);
  overflow: hidden;
}

/* Map Canvas */
.map-canvas {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.leaflet-map {
  position: absolute;
  inset: 0;
}

/* Маркеры */

/* Search Suggestions */
.search-suggestions {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 60;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  max-height: 240px;
  overflow-y: auto;
  border: 1px solid #e7e8e9;
}

.search-suggestion-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f3f4f5;
}

.search-suggestion-item:last-child {
  border-bottom: none;
}

.search-suggestion-item:hover {
  background: #fff7ed;
}

.search-suggestion-emoji {
  font-size: 20px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #fff7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.search-suggestion-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.search-suggestion-name {
  font-size: 13px;
  font-weight: 600;
  color: #1c1917;
}

.search-suggestion-address {
  font-size: 11px;
  color: #a8a29e;
}

/* Стилизация кнопок зума Leaflet */
.leaflet-map :global(.leaflet-control-zoom) {
  position: fixed !important;
  top: 76px !important;
  left: 16px !important;
  border: none !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  backdrop-filter: blur(12px) !important;
  background: rgba(255, 255, 255, 0.25) !important;
}

.leaflet-map :global(.leaflet-control-zoom a) {
  width: 44px !important;
  height: 44px !important;
  line-height: 44px !important;
  background: transparent !important;
  color: #1c1917 !important;
  border: none !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
  font-size: 20px !important;
  font-weight: 700 !important;
  backdrop-filter: blur(8px) !important;
}

.leaflet-map :global(.leaflet-control-zoom a:first-child) {
  border-radius: 12px 12px 0 0 !important;
}

.leaflet-map :global(.leaflet-control-zoom a:last-child) {
  border-radius: 0 0 12px 12px !important;
  border-bottom: none !important;
}

.leaflet-map :global(.leaflet-control-zoom a:hover) {
  background: rgba(255, 255, 255, 0.4) !important;
}

.leaflet-map :global(.leaflet-control-attribution) {
  display: none !important;
}

/* Spread Transition Overlay */
.spread-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #1a1a1a;
  pointer-events: none;
  clip-path: circle(0 at 50% 50%);
}

.spread-overlay.active {
  pointer-events: auto;
}

/* Dark Mode */
.map-light.dark .top-bar {
  background: rgba(26, 26, 26, 0.85);
}

.map-light.dark .search-bar {
  background: rgba(38, 38, 38, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
}

.map-light.dark .search-bar input {
  color: #f0f1f2;
}

.map-light.dark .search-bar input::placeholder {
  color: #71717a;
}

.map-light.dark .search-bar span:first-child {
  color: #71717a;
}

.map-light.dark .close-btn {
  background: rgba(38, 38, 38, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
  color: #c2410c;
}

.map-light.dark .close-btn:hover {
  background: rgba(51, 51, 51, 0.8);
}

.map-light.dark .control-btn-glass {
  background: rgba(38, 38, 38, 0.6);
  border-color: rgba(255, 255, 255, 0.1);
  color: #a1a1aa;
}

.map-light.dark .control-btn-glass:hover {
  background: rgba(51, 51, 51, 0.8);
}

.map-light.dark .control-btn-ninja {
  background: #c2410c !important;
  color: white !important;
  border-color: transparent !important;
}

.map-light.dark .bottom-nav {
  background: rgba(26, 26, 26, 0.85);
}

.map-light.dark .nav-item {
  color: #71717a;
}

.map-light.dark .nav-item.active {
  background: rgba(194, 65, 12, 0.2);
  color: #c2410c;
  border: 1px solid rgba(194, 65, 12, 0.3);
}

.map-light.dark .fab-btn {
  background: #c2410c;
  color: white;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

/* Leaflet dark mode */
.map-light.dark .leaflet-map :global(.leaflet-control-zoom) {
  background: rgba(0, 0, 0, 0.3) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
}

.map-light.dark .leaflet-map :global(.leaflet-control-zoom a) {
  background: transparent !important;
  color: #f0f1f2 !important;
  border-bottom-color: rgba(255, 255, 255, 0.08) !important;
}

.map-light.dark .leaflet-map :global(.leaflet-control-zoom a:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
}

/* Popup dark mode */
.map-light.dark .leaflet-map :global(.leaflet-popup-content-wrapper) {
  background: #262626 !important;
}

.map-light.dark .leaflet-map :global(.leaflet-popup-tip) {
  background: #262626 !important;
}

.map-light.dark .leaflet-map :global(.leaflet-popup-close-button) {
  color: #f0f1f2 !important;
}

.map-light.dark :global(.popup-header h3) {
  color: #f0f1f2;
}

.map-light.dark :global(.popup-address) {
  color: #a1a1aa;
}

.map-light.dark :global(.popup-desc) {
  color: #a1a1aa;
}

.map-light.dark :global(.popup-emoji) {
  background: #333333;
}

.map-light.dark :global(.popup-rating) {
  background: rgba(194, 65, 12, 0.2);
}

.map-light.dark :global(.popup-btn) {
  background: #c2410c;
}

/* Map tile transition */
.leaflet-map :global(.leaflet-tile-pane) {
  transition: filter 0.6s ease;
}

/* Маркеры: белый фон + оранжевая рамка */
/* Стили заданы inline в createPlaceMarker */

/* Стилизация Leaflet Popup */
.leaflet-map :global(.leaflet-popup-content-wrapper) {
  background: white !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
  padding: 0 !important;
  overflow: hidden !important;
}

.leaflet-map :global(.leaflet-popup-content) {
  margin: 0 !important;
  width: 260px !important;
}

.leaflet-map :global(.leaflet-popup-tip-container) .leaflet-popup-tip {
  background: white !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.leaflet-map :global(.leaflet-popup-close-button) {
  z-index: 10 !important;
  font-size: 24px !important;
  color: white !important;
  background: rgba(0, 0, 0, 0.3) !important;
  border-radius: 50% !important;
  width: 28px !important;
  height: 28px !important;
  line-height: 28px !important;
  top: 8px !important;
  right: 8px !important;
}

.leaflet-map :global(.leaflet-popup-close-button:hover) {
  background: rgba(0, 0, 0, 0.5) !important;
}

/* Place Popup */
:global(.place-popup) {
  font-family: 'Inter', sans-serif;
}

:global(.popup-gallery) {
  display: flex;
  gap: 2px;
  height: 110px;
  overflow: hidden;
}

:global(.gallery-item) {
  flex: 1;
  height: 100%;
  overflow: hidden;
}

:global(.gallery-main) {
  flex: 3;
}

:global(.gallery-item img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

:global(.popup-info) {
  padding: 12px;
}

:global(.popup-header) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

:global(.popup-title) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:global(.popup-emoji) {
  font-size: 22px;
  width: 36px;
  height: 36px;
  background: #fff7ed;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

:global(.popup-title h3) {
  font-size: 13px;
  font-weight: 700;
  margin: 0;
  color: #1c1917;
  line-height: 1.3;
}

:global(.popup-address) {
  font-size: 10px;
  color: #787170;
  margin: 2px 0 0;
}

:global(.popup-rating) {
  display: flex;
  align-items: center;
  gap: 2px;
  background: #fff7ed;
  padding: 3px 8px;
  border-radius: 12px;
  flex-shrink: 0;
}

:global(.popup-rating .star) {
  color: #f97316;
  font-size: 12px;
}

:global(.popup-rating span:last-child) {
  font-size: 12px;
  font-weight: 700;
  color: #c2410c;
}

:global(.popup-desc) {
  font-size: 11px;
  color: #57534e;
  line-height: 1.4;
  margin: 0 0 10px;
}

:global(.popup-btn) {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: #ea580c;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 9px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.2s;
}

:global(.popup-btn:hover) {
  background: #c2410c;
}

:global(.popup-btn .material-symbols-outlined) {
  font-size: 16px;
}

.leaflet-map :global(.leaflet-container) {
  width: 100%;
  height: 100%;
}

/* ============================================
   🥷 Режим ниндзя — стили
   ============================================ */

/* Кнопка ниндзя в активном состоянии */
.control-btn-ninja.active {
  background: rgba(234, 88, 12, 0.2);
  color: #ea580c;
  border-color: rgba(234, 88, 12, 0.5);
}

/* Event marker */
:global(.event-marker) {
  z-index: 1050 !important;
}

/* Event Popup */
:global(.event-popup-wrapper) {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

:global(.event-popup-wrapper .leaflet-popup-content-wrapper) {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  padding: 0;
  overflow: hidden;
}

:global(.event-popup-wrapper .leaflet-popup-content) {
  margin: 0;
  font-family: 'Inter', sans-serif;
}

:global(.event-popup-wrapper .leaflet-popup-tip) {
  background: #fff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

:global(.event-popup) {
  padding: 16px;
  max-width: 260px;
}

:global(.event-popup-header) {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

:global(.event-popup-emoji) {
  font-size: 28px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ea580c;
  border-radius: 50%;
  flex-shrink: 0;
}

:global(.event-popup-title) {
  font-size: 16px;
  font-weight: 700;
  color: #1c1917;
  margin: 0;
  line-height: 1.3;
}

:global(.event-popup-desc) {
  font-size: 13px;
  color: #787170;
  margin: 0 0 12px;
  line-height: 1.4;
}

:global(.event-popup-info) {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

:global(.event-popup-info div) {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #44403c;
}

:global(.event-popup-info .material-symbols-outlined) {
  font-size: 16px;
  color: #ea580c;
}

:global(.event-quiet-tag) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  margin-top: 4px;
}

@keyframes ping {
  0% {
    transform: scale(1);
    opacity: 0.2;
  }
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* Top AppBar */
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  padding: 8px;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 0 0 16px 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.close-btn {
  width: 44px;
  height: 44px;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 50%;
  border: 2px solid #ea580c;
  box-shadow: 0 2px 8px rgba(234, 88, 12, 0.2);
  cursor: pointer;
  color: #ea580c;
  transition: transform 0.2s, background 0.2s;
}

.close-btn:hover {
  background: #fef3f0;
  transform: scale(1.05);
}

.close-btn:active {
  transform: scale(0.92);
}

.search-bar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  padding: 10px 16px;
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.search-bar input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  outline: none;
  color: var(--on-surface);
  font-family: 'Inter', sans-serif;
}

.search-bar input::placeholder {
  color: #a8a29e;
}

.search-bar span:first-child {
  color: #787170;
  font-size: 20px;
}

/* Map Controls */
.map-controls {
  position: fixed;
  bottom: 128px;
  right: 24px;
  z-index: 40;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: bottom 0.3s ease;
}

/* Поднятые кнопки при отображении маршрута/навигации */
.map-controls.raised {
  bottom: 300px;
  z-index: 60;
}

.control-btn {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.control-btn:active {
  transform: scale(0.9);
}

/* Прозрачная кнопка слоёв */
.control-btn-glass {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(16px);
  color: #57534e;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.control-btn-glass:hover {
  background: rgba(255, 255, 255, 0.7);
}

/* Кнопка ниндзя */
.control-btn-ninja {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(16px);
  color: #ea580c;
  border: 1px solid rgba(234, 88, 12, 0.3);
  box-shadow: 0 4px 12px rgba(234, 88, 12, 0.1);
}

.control-btn-ninja:hover {
  background: rgba(234, 88, 12, 0.15);
}

/* Кнопка геолокации */
.control-btn-primary {
  background: #ea580c;
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 16px rgba(234, 88, 12, 0.4);
}

.control-btn-primary:hover {
  background: #c2410c;
}

/* FAB Quick Start */
.fab-quick-start {
  position: fixed;
  bottom: 112px;
  left: 24px;
  z-index: 40;
}

.fab-btn {
  background: var(--primary-container);
  padding: 12px 20px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  box-shadow: 0 8px 24px rgba(194, 65, 12, 0.2);
  border: 1px solid rgba(194, 65, 12, 0.2);
  color: var(--on-primary-container);
  cursor: pointer;
  transition: transform 0.2s;
}

.fab-btn:active {
  transform: scale(0.95);
}

.fab-btn span:first-child {
  margin-right: 8px;
}

.fab-btn span:last-child {
  font-size: 14px;
  font-weight: bold;
  letter-spacing: -0.025em;
}

/* Bottom Navigation */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 2px;
  padding: 8px 4px max(20px, env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.06);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6px 4px;
  border-radius: 9999px;
  text-decoration: none;
  color: #59413a;
  transition: all 0.2s;
  min-width: 0;
  flex: 1;
  max-width: 72px;
  -webkit-tap-highlight-color: transparent;
}

.nav-item:hover {
  background: #f3f4f5;
  color: #ea580c;
}

.nav-item-active {
  background: #ea580c !important;
  color: #ffffff !important;
  padding: 6px 8px;
}

.nav-item-active:hover {
  background: #c2410c !important;
}

.nav-item .material-symbols-outlined {
  font-size: 24px;
  transition: all 0.2s;
}

.nav-item span:last-child {
}

.nav-item span:first-child {
  font-size: 24px;
}

.nav-item span:last-child {
  font-size: 10px;
  font-weight: 500;
  margin-top: 2px;
}

.filled {
  font-variation-settings: 'FILL' 1;
}

/* ============================================
   Filters Panel
   ============================================ */

.filter-toggle-btn {
  width: 40px;
  height: 40px;
  min-width: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, background 0.2s;
}

.filter-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.7);
}

.filter-toggle-btn:active {
  transform: scale(0.92);
}

.filters-panel {
  position: fixed;
  top: 72px;
  left: 0;
  right: 0;
  z-index: 45;
  background: var(--surface-container-lowest);
  border-radius: 0 0 24px 24px;
  padding: 0 16px 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease, padding 0.35s ease;
}

.filters-panel.open {
  max-height: 80dvh;
  overflow-y: auto;
  opacity: 1;
  padding: 16px 16px 20px;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filters-header h3 {
  font-size: 16px;
  font-weight: bold;
  color: #1c1917;
  margin: 0;
}

.reset-filters-btn {
  font-size: 12px;
  color: var(--primary);
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.reset-filters-btn:hover {
  background: #fff7ed;
}

.filter-group {
  margin-bottom: 16px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: #787170;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.filter-label input[type="checkbox"] {
  display: none;
}

.filter-checkbox-box {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  border: 2px solid #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.filter-label input:checked + .filter-checkbox-box {
  background: var(--primary);
  border-color: var(--primary);
}

.filter-checkbox-box .material-symbols-outlined {
  font-size: 16px;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
}

.filter-label input:checked + .filter-checkbox-box .material-symbols-outlined {
  opacity: 1;
}

.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.filter-chip {
  padding: 8px 14px;
  border-radius: 9999px;
  border: 2px solid #e7e8e9;
  background: var(--surface-container-low);
  color: #787170;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.filter-chip:hover {
  border-color: var(--primary);
  background: #fff7ed;
}

.filter-chip.active {
  border-color: var(--primary);
  background: #ffedd5;
  color: var(--primary);
}

.apply-filters-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #ea580c, #f97316);
  color: white;
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 8px;
}

.apply-filters-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(234, 88, 12, 0.3);
}

.apply-filters-btn:active {
  transform: scale(0.98);
}

.apply-filters-btn .material-symbols-outlined {
  font-size: 20px;
}

/* ============================================
   Route Panel
   ============================================ */

.route-panel {
  position: fixed;
  top: 72px;
  left: 0;
  right: 0;
  z-index: 46;
  background: var(--surface-container-lowest);
  border-radius: 0 0 24px 24px;
  padding: 0 16px 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease, padding 0.35s ease;
}

.route-panel.open {
  max-height: 90dvh;
  overflow-y: auto;
  opacity: 1;
  padding: 16px 16px 20px;
}

.route-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.route-panel-header h3 {
  font-size: 16px;
  font-weight: bold;
  color: #1c1917;
  margin: 0;
}

.route-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: var(--surface-container-high);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #787170;
  transition: background 0.2s;
}

.route-close:hover {
  background: #d1d5db;
}

.route-field {
  margin-bottom: 14px;
}

.route-field label {
  font-size: 11px;
  font-weight: 600;
  color: #787170;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 6px;
}

.route-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface-container-low);
  border-radius: 12px;
  padding: 0 12px;
  border: 1px solid #e7e8e9;
  transition: border-color 0.2s;
}

.route-input-row:focus-within {
  border-color: var(--primary);
}

.route-input-row input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px 0;
  font-size: 14px;
  color: #1c1917;
  outline: none;
  font-family: 'Inter', sans-serif;
}

.route-dot {
  font-size: 18px;
  flex-shrink: 0;
}

.start-dot {
  color: #22c55e;
}

.end-dot {
  color: #ea580c;
}

.route-geo-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  transition: background 0.2s;
  flex-shrink: 0;
}

.route-geo-btn:hover {
  background: rgba(234, 88, 12, 0.1);
}

.route-geo-btn .material-symbols-outlined {
  font-size: 20px;
}

/* Dropdown */
.route-dropdown {
  position: relative;
  margin-top: 4px;
  background: var(--surface-container-lowest);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid #e7e8e9;
  z-index: 10;
}

.route-dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.route-dropdown-item:hover {
  background: #fff7ed;
}

.route-dropdown-item.selected {
  background: #ffedd5;
}

.route-place-emoji {
  font-size: 18px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #fff7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.route-place-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.route-place-name {
  font-size: 13px;
  font-weight: 600;
  color: #1c1917;
}

.route-place-address {
  font-size: 11px;
  color: #a8a29e;
}

/* Build Button */
.route-build-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #ea580c, #f97316);
  color: white;
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s;
  margin-top: 4px;
}

.route-build-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(234, 88, 12, 0.3);
}

.route-build-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.route-build-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.route-build-btn .material-symbols-outlined {
  font-size: 20px;
}

/* Pick on Map buttons */
.route-pick-mode {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.route-pick-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 10px;
  border: 2px solid #e7e8e9;
  background: var(--surface-container-low);
  color: #787170;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}

.route-pick-btn:hover {
  border-color: var(--primary);
}

.route-pick-btn .material-symbols-outlined {
  font-size: 18px;
}

/* "Начать навигацию" кнопка */
.nav-start-bar {
  position: relative;
  margin-bottom: 8px;
}

/* Floating "Начать навигацию" button */
.nav-start-float-btn {
  position: fixed;
  bottom: 210px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
}

.nav-start-float-btn button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border-radius: 9999px;
  border: none;
  background: linear-gradient(135deg, #ea580c, #f97316);
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 8px 32px rgba(234, 88, 12, 0.5);
  font-family: 'Inter', sans-serif;
}

.nav-start-float-btn button:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 40px rgba(234, 88, 12, 0.6);
}

.nav-start-float-btn button:active {
  transform: scale(0.95);
}

.nav-start-float-btn .material-symbols-outlined {
  font-size: 22px;
}

/* Nav start button transition */
.nav-start-fade-enter-active,
.nav-start-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.nav-start-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.nav-start-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

/* Контейнер для кнопок маршрутов */

.nav-start-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #16a34a, #22c55e);
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 20px rgba(22, 163, 74, 0.4);
  font-family: 'Inter', sans-serif;
}

.nav-start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(22, 163, 74, 0.5);
}

.nav-start-btn:active {
  transform: scale(0.98);
}

.nav-start-btn .material-symbols-outlined {
  font-size: 22px;
}

/* Контейнер для навигации + кнопки маршрутов */
.route-bar-group {
  position: fixed;
  bottom: 96px;
  left: 16px;
  right: 16px;
  z-index: 55;
}

/* Navigation Bar (при навигации) */
.nav-bar-overlay {
  position: fixed;
  bottom: 96px;
  left: 16px;
  right: 16px;
  z-index: 55;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border-radius: 16px;
  padding: 12px 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  gap: 16px;
}

/* route-toggle-bar внутри route-bar-group — без собственного позиционирования */
.route-toggle-bar-overlay {
  display: flex;
  align-items: stretch;
  gap: 8px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.map-light.dark .route-toggle-bar-overlay {
  background: rgba(26, 26, 26, 0.9);
  border-color: rgba(255, 255, 255, 0.08);
}

/* Кнопки переключения маршрутов */
.route-bar-group .route-toggle-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 8px;
  border-radius: 12px;
  border: 2px solid transparent;
  background: rgba(255, 255, 255, 0.5);
  color: #787170;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}

.map-light.dark .route-bar-group .route-toggle-btn {
  background: rgba(38, 38, 38, 0.6);
}

.route-bar-group .route-toggle-btn:hover {
  background: rgba(234, 88, 12, 0.1);
}

.route-bar-group .route-toggle-btn.active {
  border-color: var(--primary);
  background: #ffedd5;
  color: #1c1917;
}

.map-light.dark .route-bar-group .route-toggle-btn.active {
  background: rgba(194, 65, 12, 0.2);
  color: #f0f1f2;
}

.route-bar-group .route-toggle-icon {
  font-size: 16px;
}

.route-bar-group .route-toggle-btn span:nth-child(2) {
  font-size: 11px;
  font-weight: 700;
}

.route-bar-group .route-toggle-meta {
  font-size: 10px;
  color: #a8a29e;
}

.route-bar-group .route-toggle-btn.active .route-toggle-meta {
  color: #ea580c;
  font-weight: 600;
}

.route-bar-group .route-close-overlay {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(234, 88, 12, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ea580c;
  transition: background 0.2s;
  align-self: center;
}

.route-bar-group .route-close-overlay:hover {
  background: rgba(234, 88, 12, 0.2);
}

.route-bar-group .route-close-overlay .material-symbols-outlined {
  font-size: 20px;
}

/* Toggle bar transition */
.route-toggle-fade-enter-active,
.route-toggle-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.route-toggle-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.route-toggle-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.map-light.dark .nav-bar-overlay {
  background: rgba(26, 26, 26, 0.9);
  border-color: rgba(255, 255, 255, 0.08);
}

.nav-bar-info {
  flex: 1;
  display: flex;
  gap: 20px;
}

.nav-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-bar-item .material-symbols-outlined {
  font-size: 20px;
  color: #ea580c;
}

.nav-bar-item > div {
  display: flex;
  flex-direction: column;
}

.nav-bar-value {
  font-size: 14px;
  font-weight: 700;
  color: #1c1917;
}

.map-light.dark .nav-bar-value {
  color: #f0f1f2;
}

.nav-bar-label {
  font-size: 10px;
  color: #a8a29e;
  font-weight: 500;
}

/* Stop Navigation Button */
.nav-stop-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 12px;
  border: 2px solid #dc2626;
  background: transparent;
  color: #dc2626;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
  white-space: nowrap;
}

.nav-stop-btn:hover {
  background: #dc2626;
  color: white;
}

.nav-stop-btn .material-symbols-outlined {
  font-size: 18px;
}

/* Navigation bar transition */
.nav-bar-fade-enter-active,
.nav-bar-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.nav-bar-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.nav-bar-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* ============================================
   Pick Point Overlay (иголка по центру)
   ============================================ */

.pick-overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

/* Иголка — фиксирована по центру экрана */
.pick-pin {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -100%);
  z-index: 61;
  width: 36px;
  height: 52px;
  pointer-events: none;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
  animation: pin-bounce 1.5s ease-in-out infinite;
}

@keyframes pin-bounce {
  0%, 100% { transform: translate(-50%, -100%); }
  50% { transform: translate(-50%, -105%); }
}

.pick-pin svg {
  width: 100%;
  height: 100%;
}

/* Подсказка */
.pick-hint {
  position: fixed;
  top: calc(50% + 40px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 61;
  pointer-events: none;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  padding: 6px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.map-light.dark .pick-hint {
  background: rgba(26, 26, 26, 0.9);
}

.pick-hint-text {
  font-size: 12px;
  font-weight: 600;
  color: #1c1917;
  white-space: nowrap;
}

.map-light.dark .pick-hint-text {
  color: #f0f1f2;
}

/* Кнопки */
.pick-actions {
  position: fixed;
  bottom: 112px;
  left: 16px;
  right: 16px;
  z-index: 61;
  display: flex;
  gap: 12px;
  pointer-events: auto;
}

.pick-cancel-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 14px;
  border-radius: 12px;
  border: 2px solid #e7e8e9;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  color: #787170;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.map-light.dark .pick-cancel-btn {
  background: rgba(38, 38, 38, 0.9);
  color: #a1a1aa;
}

.pick-cancel-btn:hover {
  border-color: #dc2626;
  color: #dc2626;
}

.pick-cancel-btn .material-symbols-outlined {
  font-size: 20px;
}

.pick-confirm-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: var(--primary-container);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 16px rgba(249, 115, 22, 0.3);
}

.pick-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(234, 88, 12, 0.3);
}

.pick-confirm-btn .material-symbols-outlined {
  font-size: 20px;
}

/* Transition */
.pick-overlay-fade-enter-active,
.pick-overlay-fade-leave-active {
  transition: opacity 0.25s ease;
}

.pick-overlay-fade-enter-from,
.pick-overlay-fade-leave-to {
  opacity: 0;
}

/* Route Toggle Bar — переключение маршрутов (внутри формы, удалён) */

/* Route Toggle Bar Overlay — поверх карты над bottom-nav */
.route-toggle-bar-overlay {
  position: fixed;
  bottom: 96px;
  left: 16px;
  right: 16px;
  z-index: 45;
  display: flex;
  align-items: stretch;
  gap: 8px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.map-light.dark .route-toggle-bar-overlay {
  background: rgba(26, 26, 26, 0.9);
  border-color: rgba(255, 255, 255, 0.08);
}

.route-toggle-bar-overlay .route-toggle-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 8px;
  border-radius: 12px;
  border: 2px solid transparent;
  background: rgba(255, 255, 255, 0.5);
  color: #787170;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}

.map-light.dark .route-toggle-bar-overlay .route-toggle-btn {
  background: rgba(38, 38, 38, 0.6);
}

.route-toggle-bar-overlay .route-toggle-btn:hover {
  background: rgba(234, 88, 12, 0.1);
}

.route-toggle-bar-overlay .route-toggle-btn.active {
  border-color: var(--primary);
  background: #ffedd5;
  color: #1c1917;
}

.map-light.dark .route-toggle-bar-overlay .route-toggle-btn.active {
  background: rgba(194, 65, 12, 0.2);
  color: #f0f1f2;
}

.route-toggle-bar-overlay .route-toggle-icon {
  font-size: 16px;
}

.route-toggle-bar-overlay .route-toggle-btn span:nth-child(2) {
  font-size: 11px;
  font-weight: 700;
}

.route-toggle-bar-overlay .route-toggle-meta {
  font-size: 10px;
  color: #a8a29e;
}

.route-toggle-bar-overlay .route-toggle-btn.active .route-toggle-meta {
  color: #ea580c;
  font-weight: 600;
}

.route-close-overlay {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(234, 88, 12, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ea580c;
  transition: background 0.2s;
  align-self: center;
}

.route-close-overlay:hover {
  background: rgba(234, 88, 12, 0.2);
}

.route-close-overlay .material-symbols-outlined {
  font-size: 20px;
}

/* Toggle transition */
.route-toggle-fade-enter-active,
.route-toggle-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.route-toggle-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.route-toggle-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* FAB transition */
.fab-fade-enter-active,
.fab-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fab-fade-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.fab-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* ============================================
   🐅 Loading Overlay — анимация тигра
   ============================================ */

.loading-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 20px;
}

.loading-text {
  color: #ea580c;
  font-size: 28px;
  font-weight: 800;
  text-align: center;
  padding: 0 24px;
  text-transform: uppercase;
  letter-spacing: 1px;
  animation: text-pulse 2s ease-in-out infinite;
}

.loading-video-wrapper {
  position: relative;
  width: 95vw;
  max-width: 700px;
  aspect-ratio: 1 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  overflow: hidden;
}

.loading-tiger {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  animation: tiger-bounce 1.5s ease-in-out infinite;
}

@keyframes tiger-bounce {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.03);
  }
}

@keyframes text-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.loading-overlay-fade-enter-active,
.loading-overlay-fade-leave-active {
  transition: opacity 0.3s ease;
}

.loading-overlay-fade-enter-from,
.loading-overlay-fade-leave-to {
  opacity: 0;
}
</style>
