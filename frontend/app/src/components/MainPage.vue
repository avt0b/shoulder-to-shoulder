<template>
  <div class="main-page">
    <!-- Top Navigation -->
    <nav class="top-nav">
      <div class="nav-brand">
        <div class="avatar-wrapper">
          <div class="avatar">
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuDpfv2jdSpqPq9LfvhaIC8_axb5WLqMdlPMo9iVnmCZV8e7fY4XQvMbhDbl0SVzSyfN91CMhBYOC6FX2iGTaTWJ5qQkAwtiWjRwE9blPtdUDmNm-4m8trXbyzsMZRYDbkMcn0tHAEwV7HDDzalxua2JqK3qpMES04PRV9y4wsePZPWgNtwrV-VwSTlTD1f4jdt8EH1Ku4My8rwhXBhs7Zl7kUsQmMG619SEjGC9TCyPrQhaslXv1EAD9w4loswmmyy4-4QVmLnRcF0" alt="Profile" />
          </div>
          <div class="badge">94%</div>
        </div>
        <div class="brand-text">
          <span class="brand-title">Плечом к плечу</span>
          <span class="brand-subtitle">Empathy: 12</span>
        </div>
      </div>
      <button class="icon-button">
        <span class="material-symbols-outlined">search</span>
      </button>
    </nav>

    <!-- Main Content -->
    <main class="content">
      <!-- Search Card -->
      <section class="search-card">
        <div class="search-input">
          <span class="material-symbols-outlined">search</span>
          <input type="text" placeholder="Найти место или группу..." />
        </div>
        <div class="location-btn">
          <span class="material-symbols-outlined">my_location</span>
        </div>
      </section>

      <!-- Map Card -->
      <section class="map-card" @click="$emit('expand-map')">
        <div ref="mapRef" class="map-container"></div>

        <!-- Map Overlay -->
        <div class="map-overlay">
          <div class="map-controls">
            <button class="control-btn">
              <span class="material-symbols-outlined">layers</span>
            </button>
            <button class="control-btn">
              <span class="material-symbols-outlined">my_location</span>
            </button>
          </div>
        </div>

        <!-- Expand Icon -->
        <div class="expand-icon">
          <span class="material-symbols-outlined">open_in_full</span>
        </div>
      </section>

      <!-- Meetups Section -->
      <section class="meetups-section">
        <div class="section-header">
          <h2>Сегодня</h2>
          <div class="tabs">
            <button class="tab active">Тренировка</button>
            <button class="tab">Растяжка</button>
            <button class="tab">Тишина</button>
            <button class="tab">Вечер</button>
          </div>
        </div>

        <button class="create-btn">
          <span class="material-symbols-outlined">add_circle</span>
          <span>Создать встречу</span>
        </button>

        <!-- Ваши мероприятия (динамические карточки) -->
        <div class="my-meetups-section">
          <div class="section-header">
            <h2>Ваши мероприятия</h2>
          </div>
          <div class="meetup-cards">
            <div class="meetup-card" :class="{ 'border-primary': meetup.isJoined }" v-for="meetup in myMeetups" :key="meetup.id">
              <div class="meetup-header">
                <div class="meetup-info">
                  <div class="meetup-time">
                    <span class="material-symbols-outlined">schedule</span>
                    <span>{{ meetup.time }} • {{ meetup.locationShort }}</span>
                  </div>
                  <h3>{{ meetup.name }}</h3>
                </div>
                <div class="meetup-level">{{ meetup.level }}</div>
              </div>
              <div class="meetup-footer">
                <div class="avatars">
                  <img v-for="(avatar, i) in meetup.avatars.slice(0, 3)" :key="i" class="avatar-sm" :src="avatar" alt="User" />
                  <div class="avatar-sm avatar-more" v-if="meetup.moreCount > 0">+{{ meetup.moreCount }}</div>
                </div>
                <div class="join-section">
                  <span class="join-count">{{ meetup.participants }}/{{ meetup.maxParticipants }} участников</span>
                  <button class="join-btn" :class="{ 'join-btn-joined': meetup.isJoined }" :title="meetup.isJoined ? 'Участвую' : 'Присоединиться'">
                    <span class="material-symbols-outlined">{{ meetup.isJoined ? 'check_circle' : 'directions_run' }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Safety Card -->
      <section class="safety-card">
        <div class="safety-header">
          <div class="safety-title">
            <span class="material-symbols-outlined filled">verified_user</span>
            <h4>Безопасный маршрут</h4>
          </div>
          <div class="safety-rating">
            <span>4.2/5</span>
          </div>
        </div>
        <div class="safety-content">
          <div class="safety-map">
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuDQnOZ9kJFn_XJCo19Q5i3LlgCgpLMasEaQetpeNOpbailZRBIr6ZlqaLK5LggPgb7yg_JA2iZ0x4GImC78SI2SaWS3-xY6YXwVWf8KvNmjAGm0Lr6b8gvV5ACn3J3rpOXcUBNLp_M5rPrrFM7m5H5N22h8v2xCOXFVgsH4va2a5PjB8HqB11fLrCYqgdUQ8jEGdLs0EIcAuiueu3j0GqkNTFPDYmrK6b-8r053HrqtJVBMIhVT9aZyYZBo6wF1UfMo2Rzci97r19I" alt="Safety Map" />
            <div class="safety-map-overlay"></div>
          </div>
          <div class="safety-info">
            <div class="safety-progress">
              <div class="safety-progress-bar" style="width: 84%"></div>
            </div>
            <p class="safety-text">
              Безопасность: 4.2/5 • Освещённая зона • <span class="highlight">3 человека рядом</span>
            </p>
          </div>
        </div>
      </section>
    </main>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <a href="#" class="nav-item" :class="{ active: activeNav === 'map' }" @click.prevent="handleNavClick('map')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'map' }">map</span>
        <span>Карта</span>
      </a>
      <a href="#" class="nav-item" :class="{ active: activeNav === 'groups' }" @click.prevent="handleNavClick('groups')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'groups' }">group</span>
        <span>Группы</span>
      </a>
      <a href="#" class="nav-item" :class="{ active: activeNav === 'routes' }" @click.prevent="handleNavClick('routes')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'routes' }">directions_run</span>
        <span>Маршруты</span>
      </a>
      <a href="#" class="nav-item" :class="{ active: activeNav === 'profile' }" @click.prevent="handleNavClick('profile')">
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
import { config, api } from '../config'

const emit = defineEmits(['expand-map'])

const activeNav = ref('map')
const mapRef = ref(null)
let map = null

// Ваши мероприятия — заглушка (заменить на API)
const myMeetups = ref([])

// Заглушка данных
const mockMeetups = [
  {
    id: 1,
    name: 'Вечернее кардио',
    time: '19:00',
    locationShort: 'Парк',
    location: 'Парк Победы',
    level: 'Новичок',
    participants: 3,
    maxParticipants: 5,
    isJoined: true,
    avatars: [
      'https://lh3.googleusercontent.com/aida-public/AB6AXuCaPrzntHOHOKvG0BIVPpc_3b2THNM8JxRVn-Vy0qppvVs3OLYoEPBUmcOdAbbYL66LZ6swLoWGWnM2a8lrbZU_2FeRJB6V09iN7R7gCdvzG70oNaGwQHuTDTuWLxFZIcsCuyPKDTxTTlCa-mIDWw_u6ICDWyE7PTSipMhDpdIaIRBWarjXJOQpXw5xQtV9t9i6PKTqJsG-cMsz5IH400UKj9VD_MVWUHv6Rp7fSO9oCivO9qH9carbZ6v8a4p63_S046k5bphL43U',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBE_honUQO8Mm-QEHIB3Bz94CyHvcv9VD7wLKYfJGSxND4d3rQNIYkCNg_qVQePsYqUC1Jy4-b1crYdzSN-S7OGgnWogDfbARxuOKErajv7ODK6tavnPTZcFSFrmOmDrbzzIfPj5GSkjn5JIPc3o782XNLA4rrC7Nwxr80tj710WdoTF327craU0496uTzPJI0jeoDAlN3sgoYDDJfoWqkLus8ZYMhGwciYtEaoLiCc99uhOxpdQXA4D1tUt4kuiNqmec6U7SsoXt0',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuDZu_-XWMjzYuGka2A9dsf14T394twZ1a7cCoJh4pgNf66M6xmaf1fy2Y5u_H1MRrf88srxGCmp_Q5ds3_uMC8oyOiF0gh3Hv541T9PEV2VM1_jsojZRXaVXhRhpu2_3tJNiG2y85-X-dc'
    ],
    moreCount: 2
  },
  {
    id: 2,
    name: 'Основы калистеники',
    time: '20:30',
    locationShort: 'Уличная арена',
    location: 'Стадион «Центральный»',
    level: 'Открыто',
    participants: 1,
    maxParticipants: 8,
    isJoined: false,
    avatars: [
      'https://lh3.googleusercontent.com/aida-public/AB6AXuC2URqWk5H4FTDLDLL0v1ywXo2oDhzArVrw_IEetPVa6vnn1NyW1eW8iBJz_J5WnNkQJA1y6sWyVhCQ8dx2z99T-AdmkCaWD0LXCxgot0-E197igZDCR7JUuvmkCtYRblPeE6Wjg8gxrcUaJAvfV61C25ooLIYUaw0LFJ1wOCnoZKVw-FWUwz8RCILbaS1VHjgzKr9vEynAzX17xSyornMJSlm8PumM0yW4Iw-DPW5UCSbeCVxAHDcjpPUSjEB7rcgNvt4tt5tU3jQ'
    ],
    moreCount: 4
  }
]

// ============================================
// 🔌 API HANDLES
// ============================================

// --- Places (места на карте) ---
const places = ref([])

// 1. Получить все места
async function fetchPlaces() {
  try {
    const res = await fetch(api('/places'))
    const data = await res.json()
    places.value = data.places
    return data.places
  } catch (e) {
    if (config.isDebug) console.warn('fetchPlaces: API недоступен')
    return []
  }
}

// 2. Получить одно место по ID
async function fetchPlaceById(id) {
  try {
    const res = await fetch(api(`/places/${id}`))
    const data = await res.json()
    return data.place
  } catch (e) {
    if (config.isDebug) console.warn(`fetchPlaceById: не удалось загрузить #${id}`)
    return null
  }
}

// 4. Ближайшие места (геолокация)
async function fetchNearbyPlaces(lat, lng, radius = 2000) {
  try {
    const res = await fetch(
      api(`/places/nearby?lat=${lat}&lng=${lng}&radius=${radius}`)
    )
    const data = await res.json()
    return data.places
  } catch (e) {
    if (config.isDebug) console.warn('fetchNearbyPlaces: API недоступен')
    return []
  }
}

// --- Маршруты (OSRM) ---

// 3. Построить маршрут
async function fetchRoute(startLat, startLng, endLat, endLng) {
  try {
    const url = `${config.osrmBaseURL}/route/v1/foot/${startLng},${startLat};${endLng},${endLat}?steps=true&geometries=geojson&overview=full`
    const res = await fetch(url)
    const data = await res.json()
    if (data.code === 'Ok' && data.routes?.length > 0) {
      return {
        distance: data.routes[0].distance,
        duration: data.routes[0].duration,
        geometry: data.routes[0].geometry,
        steps: data.routes[0].legs?.[0]?.steps?.map(s => ({
          instruction: s.maneuver?.instruction || s.name,
          distance: s.distance,
          duration: s.duration
        })) || []
      }
    }
    return null
  } catch (e) {
    if (config.isDebug) console.warn('fetchRoute: OSRM недоступен')
    return null
  }
}

// --- Мероприятия (meetups) ---

// 5. Получить мероприятия пользователя
async function fetchMyMeetups() {
  try {
    const res = await fetch(api('/meetups/my'))
    const data = await res.json()
    myMeetups.value = data.meetups
  } catch (e) {
    if (config.isDebug) console.warn('fetchMyMeetups: API недоступен, используем заглушку')
    myMeetups.value = mockMeetups
  }
}

// 6. Записаться на мероприятие
async function joinMeetup(meetupId, userId) {
  try {
    const res = await fetch(api(`/meetups/${meetupId}/join`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    })
    const data = await res.json()
    const meetup = myMeetups.value.find(m => m.id === meetupId)
    if (meetup) {
      meetup.isJoined = true
      meetup.participants = data.participants
    }
    return data
  } catch (e) {
    if (config.isDebug) console.warn(`joinMeetup: ошибка #${meetupId}`)
    return null
  }
}

// 7. Отписаться от мероприятия
async function leaveMeetup(meetupId, userId) {
  try {
    const res = await fetch(api(`/meetups/${meetupId}/leave?user_id=${userId}`), {
      method: 'DELETE'
    })
    const data = await res.json()
    const meetup = myMeetups.value.find(m => m.id === meetupId)
    if (meetup) {
      meetup.isJoined = false
      meetup.participants = data.participants
    }
    return data
  } catch (e) {
    if (config.isDebug) console.warn(`leaveMeetup: ошибка #${meetupId}`)
    return null
  }
}

// ============================================

const handleNavClick = (nav) => {
  activeNav.value = nav
}

onMounted(async () => {
  await nextTick()

  if (mapRef.value && !map) {
    // Орёл — координаты центра
    map = L.map(mapRef.value, {
      zoomControl: false,
      attributionControl: false,
      dragging: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      touchZoom: true
    }).setView([52.9651, 36.0785], 14)

    // Максимально подробная карта OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(map)

    setTimeout(() => map.invalidateSize(), 100)
  }

  // Загружаем мероприятия (заглушка или API)
  await fetchMyMeetups()
})
</script>

<style scoped>
.main-page {
  min-height: 100dvh;
  background: var(--surface-container-low);
  padding-bottom: 128px;
  width: 100%;
}

/* Top Navigation */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(248, 249, 250, 0.8);
  backdrop-filter: blur(24px);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ea580c, #fea182);
  padding: 2px;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid var(--surface-container-lowest);
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: var(--primary);
  color: white;
  font-size: 8px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 9999px;
  border: 2px solid var(--surface-container-lowest);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 20px;
  font-weight: bold;
  letter-spacing: -0.025em;
  color: #1c1917;
  text-transform: uppercase;
}

.brand-subtitle {
  font-size: 10px;
  font-weight: 500;
  color: var(--primary);
}

.icon-button {
  padding: 8px;
  border-radius: 50%;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.2s;
}

.icon-button:hover {
  background: rgba(120, 113, 108, 0.1);
}

.icon-button .material-symbols-outlined {
  color: #9a3412;
}

/* Content */
.content {
  margin-top: 80px;
  padding: 0 16px;
  width: 100%;
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Search Card */
.search-card {
  background: var(--surface-container-lowest);
  padding: 12px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  flex: 1;
  background: var(--surface-container-low);
  border-radius: 9999px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
  color: var(--on-surface);
}

.search-input input::placeholder {
  color: #a8a29e;
}

.location-btn {
  background: var(--primary-container);
  color: white;
  padding: 10px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.location-btn .material-symbols-outlined {
  font-size: 20px;
}

/* Map Card */
.map-card {
  position: relative;
  height: 320px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.2s;
}

.map-card:hover {
  transform: scale(1.01);
}

.map-container {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.map-container :global(.leaflet-container) {
  width: 100%;
  height: 100%;
  filter: grayscale(30%);
}

.map-overlay {
  position: absolute;
  inset: 0;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  pointer-events: none;
  z-index: 10;
}

.map-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-self: flex-end;
  pointer-events: auto;
}

.control-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-container-lowest);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  border: none;
  cursor: pointer;
  color: var(--on-surface);
}

.expand-icon {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  pointer-events: auto;
}

/* Meetups Section */
.meetups-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.025em;
  padding: 0 4px;
}

.tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.tabs::-webkit-scrollbar {
  display: none;
}

.tab {
  flex: none;
  background: var(--surface-container-high);
  color: var(--on-surface-variant);
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  white-space: nowrap;
}

.tab.active {
  background: var(--primary);
  color: white;
  font-weight: bold;
}

.create-btn {
  width: 100%;
  background: linear-gradient(135deg, #ea580c, #f97316);
  padding: 16px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: white;
  border: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  transition: transform 0.2s;
}

.create-btn:active {
  transform: scale(0.98);
}

.create-btn span {
  font-weight: bold;
  letter-spacing: 0.025em;
}

/* Meetup Cards */
.meetup-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meetup-card {
  background: var(--surface-container-lowest);
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meetup-card.border-primary {
  border-left: 4px solid var(--primary);
}

.meetup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.meetup-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meetup-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary);
}

.meetup-time span:first-child {
  font-size: 14px;
}

.meetup-time span:last-child {
  font-size: 12px;
  font-weight: 900;
}

.meetup-info h3 {
  font-size: 16px;
  font-weight: bold;
}

.meetup-level {
  background: #f5f5f4;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
  color: #787170;
  text-transform: uppercase;
}

.meetup-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatars {
  display: flex;
  margin-left: -8px;
}

.avatar-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid white;
  object-fit: cover;
}

.avatar-more {
  background: var(--surface-container-high);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  color: #787170;
}

.join-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.join-count {
  font-size: 12px;
  color: #a8a29e;
  font-weight: 500;
}

.join-btn {
  background: var(--primary-container);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
}

.join-btn .material-symbols-outlined {
  font-size: 20px;
}

.join-btn-secondary {
  background: var(--surface-container-high);
  color: var(--on-surface-variant);
}

/* My Meetups — Ваши мероприятия */
.my-meetups-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.join-btn-joined {
  background: var(--surface-container-high);
  color: #16a34a;
}

/* Safety Card */
.safety-card {
  background: var(--surface-container-lowest);
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.safety-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.safety-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.safety-title .material-symbols-outlined {
  color: #16a34a;
  font-variation-settings: 'FILL' 1;
}

.safety-title h4 {
  font-size: 14px;
  font-weight: bold;
}

.safety-rating {
  background: #f0fdf4;
  padding: 4px 12px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
}

.safety-rating span {
  font-size: 12px;
  font-weight: bold;
  color: #15803d;
}

.safety-content {
  display: flex;
  gap: 16px;
}

.safety-map {
  width: 96px;
  height: 64px;
  border-radius: 8px;
  background: #f5f5f4;
  overflow: hidden;
  position: relative;
}

.safety-map img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(100%) opacity(0.5);
}

.safety-map-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(34, 197, 94, 0.2), transparent);
}

.safety-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}

.safety-progress {
  height: 8px;
  width: 100%;
  background: var(--surface-container-high);
  border-radius: 9999px;
  overflow: hidden;
}

.safety-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #fb923c);
  border-radius: 9999px;
}

.safety-text {
  font-size: 10px;
  color: #787170;
  line-height: 1.4;
}

.safety-text .highlight {
  color: var(--primary);
  font-weight: 600;
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
  padding: 8px 16px 24px;
  background: rgba(248, 249, 250, 0.8);
  backdrop-filter: blur(24px);
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.04);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 20px;
  border-radius: 9999px;
  text-decoration: none;
  color: #787170;
  transition: all 0.2s;
}

.nav-item:hover {
  color: #ea580c;
}

.nav-item.active {
  background: #ffedd5;
  color: #ea580c;
}

.filled {
  font-variation-settings: 'FILL' 1;
}

.nav-item span:first-child {
  font-size: 24px;
}

.nav-item span:last-child {
  font-size: 11px;
  font-weight: 500;
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
