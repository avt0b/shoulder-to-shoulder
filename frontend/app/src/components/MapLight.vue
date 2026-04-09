<template>
  <div class="map-light" :class="{ dark: isDarkMode }">
    <!-- Route Navigator -->
    <RouteNavigator v-if="showRouteNavigator" @close="showRouteNavigator = false" />

    <!-- Map Canvas -->
    <main v-else class="map-canvas">
      <div ref="mapRef" class="leaflet-map"></div>
    </main>

    <!-- Spread Transition Overlay -->
    <div v-if="!showRouteNavigator"
      class="spread-overlay" 
      :class="{ active: isTransitioning }"
      :style="overlayStyle"
    ></div>

    <!-- Top AppBar -->
    <header v-if="!showRouteNavigator" class="top-bar">
      <button class="close-btn" @click="$emit('close')">
        <span class="material-symbols-outlined">close</span>
      </button>
      <div class="search-bar">
        <span class="material-symbols-outlined">search</span>
        <input type="text" placeholder="Поиск мест..." />
      </div>
    </header>

    <!-- Map Controls -->
    <div v-if="!showRouteNavigator" class="map-controls">
      <button class="control-btn control-btn-glass" title="Слои">
        <span class="material-symbols-outlined">layers</span>
      </button>
      <button class="control-btn control-btn-ninja" ref="ninjaBtnRef" @click="toggleDarkMode" title="Режим ниндзя">
        <span class="material-symbols-outlined">sports_martial_arts</span>
      </button>
      <button class="control-btn control-btn-primary" title="Моё местоположение">
        <span class="material-symbols-outlined filled">my_location</span>
      </button>
    </div>

    <!-- FAB Quick Start -->
    <div v-if="!showRouteNavigator" class="fab-quick-start">
      <button class="fab-btn" @click="showRouteNavigator = true">
        <span class="material-symbols-outlined">directions_run</span>
        <span>Быстрый старт</span>
      </button>
    </div>

    <!-- Bottom Navigation -->
    <nav v-if="!showRouteNavigator" class="bottom-nav">
      <a href="#" class="nav-item" :class="{ active: activeNav === 'map' }" @click.prevent="handleNav('map')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'map' }">map</span>
        <span>Карта</span>
      </a>
      <a href="#" class="nav-item" :class="{ active: activeNav === 'sessions' }" @click.prevent="handleNav('sessions')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'sessions' }">fitness_center</span>
        <span>Сессии</span>
      </a>
      <a href="#" class="nav-item" :class="{ active: activeNav === 'pulse' }" @click.prevent="handleNav('pulse')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'pulse' }">sensors</span>
        <span>Пульс</span>
      </a>
      <a href="#" class="nav-item" :class="{ active: activeNav === 'profile' }" @click.prevent="handleNav('profile')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'profile' }">person</span>
        <span>Профиль</span>
      </a>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import RouteNavigator from './RouteNavigator.vue'

const emit = defineEmits(['close'])

const activeNav = ref('map')
const mapRef = ref(null)
const ninjaBtnRef = ref(null)
const showRouteNavigator = ref(false)
let map = null
let markers = []
let isDarkMode = ref(false)
let isTransitioning = ref(false)
let overlayStyle = ref({})

// Заглушка — позже данные придут с бэкенда
const places = [
  {
    id: 1, name: 'Парк Победы',
    description: 'Отличное место для утренних пробежек и групповых тренировок.',
    lat: 52.9690, lng: 36.0820, rating: 4.7, emoji: '🏃',
    image: 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=300&h=200&fit=crop',
    gallery: [
      'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=300&h=200&fit=crop'
    ],
    category: 'park', address: 'ул. Комсомольская, Орёл'
  },
  {
    id: 2, name: 'Стадион «Центральный»',
    description: 'Беговые дорожки, тренажёры. Открыт с 6:00 до 22:00.',
    lat: 52.9620, lng: 36.0740, rating: 4.5, emoji: '🏋️',
    image: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300&h=200&fit=crop',
    gallery: [
      'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=300&h=200&fit=crop'
    ],
    category: 'stadium', address: 'ул. Ленина, Орёл'
  },
  {
    id: 3, name: 'Набережная Оки',
    description: 'Живописный маршрут вдоль реки. Подходит для прогулок и йоги.',
    lat: 52.9670, lng: 36.0680, rating: 4.8, emoji: '🧘',
    image: 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=300&h=200&fit=crop',
    gallery: [
      'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300&h=200&fit=crop'
    ],
    category: 'river', address: 'Набережная Оки, Орёл'
  },
  {
    id: 4, name: 'Спортивная площадка',
    description: 'Турники, брусья, воркаут-зона. Бесплатно, круглосуточно.',
    lat: 52.9610, lng: 36.0860, rating: 4.3, emoji: '💪',
    image: 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=300&h=200&fit=crop',
    gallery: [
      'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=300&h=200&fit=crop'
    ],
    category: 'playground', address: 'ул. Гая, Орёл'
  }
]

const handleNav = (nav) => {
  activeNav.value = nav
}

// Анимация растекания от кнопки ниндзя
const toggleDarkMode = () => {
  if (isTransitioning.value) return
  isTransitioning.value = true

  const btn = ninjaBtnRef.value
  const rect = btn.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  const maxRadius = Math.sqrt(
    Math.pow(window.innerWidth, 2) + Math.pow(window.innerHeight, 2)
  )

  const wasDark = isDarkMode.value

  if (!wasDark) {
    // Светлый → Тёмный: круг расширяется от кнопки
    overlayStyle.value = {
      background: '#1a1a1a',
      clipPath: `circle(0px at ${centerX}px ${centerY}px)`,
      transition: 'none'
    }

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        overlayStyle.value = {
          background: '#1a1a1a',
          clipPath: `circle(${maxRadius}px at ${centerX}px ${centerY}px)`,
          transition: 'clip-path 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
        }
      })
    })

    setTimeout(() => {
      isDarkMode.value = true
      if (map) {
        map.getContainer().style.filter = 'invert(1) hue-rotate(180deg) brightness(0.8) contrast(1.2)'
      }
      setTimeout(() => {
        isTransitioning.value = false
        overlayStyle.value = {}
      }, 100)
    }, 400)

  } else {
    // Тёмный → Светлый: тёмный круг сворачивается к кнопке
    overlayStyle.value = {
      background: '#1a1a1a',
      clipPath: `circle(${maxRadius}px at ${centerX}px ${centerY}px)`,
      transition: 'none'
    }

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        overlayStyle.value = {
          background: '#1a1a1a',
          clipPath: `circle(0px at ${centerX}px ${centerY}px)`,
          transition: 'clip-path 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
        }
      })
    })

    // Сразу переключаем тему — overlay ещё покрывает экран
    isDarkMode.value = false
    if (map) {
      map.getContainer().style.filter = 'none'
    }

    setTimeout(() => {
      isTransitioning.value = false
      overlayStyle.value = {}
    }, 400)
  }
}

// Создание кастомного маркера с эмодзи
const createPlaceMarker = (place) => {
  const icon = L.divIcon({
    className: 'custom-marker',
    html: `
      <div class="marker-emoji" style="
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        border: 3px solid #f97316;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
      ">${place.emoji}</div>
    `,
    iconSize: [44, 44],
    iconAnchor: [22, 22]
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
        ${place.gallery.map((img, i) => `
          <div class="gallery-item ${i === 0 ? 'gallery-main' : ''}">
            <img src="${img}" alt="${place.name}" />
          </div>
        `).join('')}
      </div>
      <div class="popup-info">
        <div class="popup-header">
          <div class="popup-title">
            <span class="popup-emoji">${place.emoji}</span>
            <div>
              <h3>${place.name}</h3>
              <p class="popup-address">${place.address}</p>
            </div>
          </div>
          <div class="popup-rating">
            <span class="star">★</span>
            <span>${place.rating}</span>
          </div>
        </div>
        <p class="popup-desc">${place.description}</p>
        <button class="popup-btn">
          <span class="material-symbols-outlined">directions_run</span>
          <span>Маршрут</span>
        </button>
      </div>
    </div>
  `

  L.popup({
    closeButton: true,
    autoPan: true,
    className: 'custom-popup',
    offset: [0, -10]
  })
    .setLatLng([place.lat, place.lng])
    .setContent(popupContent)
    .openOn(map)
}

// Добавление маркеров на карту
const addPlaceMarkers = () => {
  markers = places.map(place => createPlaceMarker(place))
}

// Удаление маркеров (для очистки)
const removePlaceMarkers = () => {
  markers.forEach(m => map.removeLayer(m))
  markers = []
}

onMounted(async () => {
  await nextTick()

  if (mapRef.value && !map) {
    map = L.map(mapRef.value, {
      zoomControl: false
    }).setView([52.9651, 36.0785], 14)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(map)

    L.control.zoom({
      position: 'topleft'
    }).addTo(map)

    addPlaceMarkers()

    setTimeout(() => map.invalidateSize(), 100)
  }
})
</script>

<style scoped>
.map-light {
  position: fixed;
  inset: 0;
  background: var(--background);
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

/* Стилизация кнопок зума Leaflet */
.leaflet-map :global(.leaflet-control-zoom) {
  position: fixed !important;
  top: 76px !important;
  left: 16px !important;
  border: none !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12) !important;
}

.leaflet-map :global(.leaflet-control-zoom a) {
  width: 44px !important;
  height: 44px !important;
  line-height: 44px !important;
  background: white !important;
  color: #ea580c !important;
  border: none !important;
  font-size: 20px !important;
}

.leaflet-map :global(.leaflet-control-zoom a:hover) {
  background: #fef3f2 !important;
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
.map-light.dark .leaflet-map :global(.leaflet-control-zoom a) {
  background: #262626 !important;
  color: #c2410c !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.map-light.dark .leaflet-map :global(.leaflet-control-zoom a:hover) {
  background: #333333 !important;
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

/* Кастомные маркеры-эмодзи */
:global(.custom-marker .marker-emoji:hover) {
  transform: scale(1.15);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.map-light.dark :global(.custom-marker .marker-emoji) {
  border-color: #c2410c !important;
  box-shadow: 0 2px 12px rgba(194, 65, 12, 0.4) !important;
}

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
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border-radius: 0 0 16px 16px;
}

.close-btn {
  width: 40px;
  height: 40px;
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  color: #ea580c;
  transition: transform 0.2s, background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.7);
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
  background: var(--primary-container);
  color: var(--on-primary-container);
  border: none;
  box-shadow: 0 4px 16px rgba(249, 115, 22, 0.3);
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
  padding: 12px 24px 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.04);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6px 20px;
  border-radius: 9999px;
  text-decoration: none;
  color: #787170;
  transition: all 0.2s;
}

.nav-item.active {
  background: #ffedd5;
  color: #ea580c;
  transform: scale(0.95);
}

.nav-item.active .material-symbols-outlined {
  font-variation-settings: 'FILL' 1;
}

.nav-item:hover:not(.active) {
  color: #ea580c;
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
</style>
