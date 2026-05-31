<template>
  <div class="main-page">
    <!-- Top Navigation -->
    <nav class="top-nav">
      <div class="nav-brand">
        <div class="avatar-wrapper">
          <div class="avatar">
            <img :src="avatarUrl" alt="Profile" />
          </div>
          <div class="badge">{{ profileData?.reliability_score ? Math.round(profileData.reliability_score) + '%' : '—' }}</div>
        </div>
        <div class="brand-text">
          <span class="brand-title">Плечом к плечу</span>
          <span class="brand-subtitle">{{ isLoadingProfile ? 'Загрузка...' : `Empathy: ${empathyScore}` }}</span>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="content">
      <!-- Map Card -->
      <section class="map-card" @click="openMapLight()">
        <div ref="mapRef" class="map-container"></div>

        <!-- Map Overlay -->
        <div class="map-overlay">
          <div class="map-controls">
            <button class="control-btn" title="Моё местоположение">
              <span class="material-symbols-outlined">my_location</span>
            </button>
          </div>
        </div>

        <!-- Expand Icon -->
        <div class="expand-icon">
          <span class="material-symbols-outlined">open_in_full</span>
        </div>
      </section>

      <!-- Navigation Info Bar (показывается при активной навигации) -->
      <section v-if="isNavigating" class="nav-info-section">
        <div class="nav-info-card">
          <div class="nav-info-icon">
            <span class="material-symbols-outlined">navigation</span>
          </div>
          <div class="nav-info-data">
            <div class="nav-info-row">
              <span class="material-symbols-outlined">straighten</span>
              <span class="nav-info-value">{{ navRemaining.distance }}</span>
            </div>
            <div class="nav-info-row">
              <span class="material-symbols-outlined">schedule</span>
              <span class="nav-info-value">{{ navRemaining.duration }}</span>
            </div>
          </div>
          <div class="nav-info-label">Осталось</div>
        </div>
      </section>

      <!-- Meetups Section -->
      <section class="meetups-section">
        <div class="section-header">
          <h2>Ваши встречи</h2>
          <span class="see-all" @click="router.push('/events')">Все встречи →</span>
        </div>

        <button class="create-btn" type="button" @click.stop="openCreateModal">
          <span class="material-symbols-outlined">add_circle</span>
          <span>Создать встречу</span>
        </button>

        <!-- My Meetup Cards -->
        <div class="meetup-cards">
          <div
            class="meetup-card border-primary"
            v-for="meetup in myMeetups"
            :key="meetup.id"
            @click="openMeetupDetail(meetup)"
          >
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

            <p class="meetup-desc" v-if="meetup.description">{{ meetup.description }}</p>

            <div class="meetup-tags" v-if="meetup.type || meetup.quietCompanion">
              <span class="meetup-type-tag" v-if="meetup.type">{{ meetup.type }}</span>
              <span class="meetup-quiet-tag" v-if="meetup.quietCompanion">🤫 Тихий</span>
            </div>

            <div class="meetup-footer">
              <div class="avatars">
                <img v-for="(avatar, i) in meetup.avatars.slice(0, 3)" :key="i" class="avatar-sm" :src="avatar" alt="User" />
                <div class="avatar-sm avatar-more" v-if="meetup.moreCount > 0">+{{ meetup.moreCount }}</div>
              </div>
              <div class="join-section">
                <span class="join-count">{{ meetup.participants }}/{{ meetup.maxParticipants }} участников</span>
                <button
                  class="join-btn"
                  :class="{ 'join-btn-joined': meetup.isJoined }"
                  @click.stop="meetup.isJoined ? handleLeaveMeetup(meetup.id) : handleJoinMeetup(meetup.id)"
                >
                  <span class="material-symbols-outlined">{{ meetup.isJoined ? 'check_circle' : 'directions_run' }}</span>
                  <span>{{ meetup.isJoined ? 'Участвую' : 'Присоединиться' }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-if="myMeetups.length === 0" class="meetup-empty">
            <span class="material-symbols-outlined empty-icon">event_busy</span>
            <p>Вы пока не записаны ни на одно мероприятие</p>
            <button class="empty-cta" @click="router.push('/events')">Найти встречу</button>
          </div>
        </div>
      </section>

      <!-- Fun Fact Card -->
      <section class="fact-card">
        <div class="fact-header">
          <div class="fact-title">
            <span class="material-symbols-outlined filled">lightbulb</span>
            <h4>Интересный факт</h4>
          </div>
        </div>
        <div class="fact-content">
          <div class="fact-emoji">{{ currentFact.emoji }}</div>
          <p class="fact-text">{{ currentFact.text }}</p>
          <div class="fact-source">{{ currentFact.source }}</div>
        </div>
      </section>
    </main>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/" class="nav-item" active-class="nav-item-active">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/'">map</span>
        <span>Карта</span>
      </router-link>
      <router-link to="/events" class="nav-item" active-class="nav-item-active">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/events'">event</span>
        <span>Ивенты</span>
      </router-link>
      <router-link to="/profile" class="nav-item" active-class="nav-item-active">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/profile'">person</span>
        <span>Профиль</span>
      </router-link>
      <router-link to="/rating" class="nav-item" active-class="nav-item-active">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/rating'">emoji_events</span>
        <span>Рейтинг</span>
      </router-link>
    </nav>

    <!-- Create Event Modal -->
    <div class="modal-overlay" v-if="showCreateModal" @click="closeModalAndReset">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Создать встречу</h2>
          <button class="modal-close" @click="closeModalAndReset">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <!-- Error Message -->
        <div v-if="formError" class="form-error" style="margin: 16px 20px 0; padding: 12px; background-color: #fee; border-left: 4px solid #ea580c; border-radius: 4px; color: #c00; font-size: 14px;">
          <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 18px; margin-right: 8px;">error</span>
          {{ formError }}
        </div>

        <form class="modal-form" @submit.prevent="submitEvent">
          <!-- Название -->
          <div class="form-group">
            <label>Название</label>
            <input v-model="form.name" type="text" placeholder="Утренняя пробежка" required />
          </div>

          <!-- Описание -->
          <div class="form-group">
            <label>Описание</label>
            <textarea v-model="form.description" placeholder="Лёгкий бег трусцой по парку. Темп разговорный, подойдёт для начинающих." rows="3"></textarea>
          </div>

          <!-- Тип мероприятия -->
          <div class="form-group">
            <label>Тип мероприятия</label>
            <div class="type-selector">
              <button
                v-for="type in eventTypes"
                :key="type.key"
                type="button"
                class="type-btn"
                :class="{ 'type-btn-active': form.type === type.key }"
                @click="form.type = type.key"
              >
                <span class="type-emoji">{{ type.emoji }}</span>
                <span class="type-name">{{ type.label }}</span>
              </button>
            </div>
          </div>

          <!-- Количество участников -->
          <div class="form-group">
            <label>Количество участников: {{ form.maxParticipants }}</label>
            <div class="counter-row">
              <button type="button" class="counter-btn" @click="form.maxParticipants = Math.max(2, form.maxParticipants - 1)">
                <span class="material-symbols-outlined">remove</span>
              </button>
              <input
                v-model.number="form.maxParticipants"
                type="range"
                min="2"
                max="10"
                step="1"
                class="range-slider"
              />
              <button type="button" class="counter-btn" @click="form.maxParticipants = Math.min(10, form.maxParticipants + 1)">
                <span class="material-symbols-outlined">add</span>
              </button>
            </div>
            <div class="counter-labels">
              <span>2</span>
              <span>10</span>
            </div>
          </div>

          <!-- Дата и время -->
          <div class="form-row">
            <div class="form-group">
              <label>Дата</label>
              <input v-model="form.date" type="date" required />
            </div>
            <div class="form-group">
              <label>Время</label>
              <input v-model="form.time" type="time" required />
            </div>
          </div>

          <!-- Тихий компаньон -->
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.quietCompanion" />
              <span class="checkbox-box">
                <span class="material-symbols-outlined checkbox-icon">check</span>
              </span>
              <span class="checkbox-text">
                🤫 Тихий компаньон
                <small>— пометка для спокойной тренировки без лишних разговоров</small>
              </span>
            </label>
          </div>

          <!-- Уровень -->
          <div class="form-group">
            <label>Уровень подготовки</label>
            <div class="level-selector">
              <button
                v-for="lvl in mainLevels"
                :key="lvl.key"
                type="button"
                class="level-btn"
                :class="{ 'level-btn-active': form.level === lvl.key }"
                @click="form.level = lvl.key"
              >
                <span class="level-emoji">{{ lvl.emoji }}</span>
                <span class="level-name">{{ lvl.label }}</span>
              </button>
            </div>
          </div>

          <!-- Место проведения -->
          <div class="form-group location-group">
            <label>Место проведения</label>

            <!-- Табы выбора способа -->
            <div class="location-tabs">
              <button class="location-tab" :class="{ active: locationMode === 'meetup' }" @click="locationMode = 'meetup'">
                <span class="material-symbols-outlined">sports_martial_arts</span>
                <span>Места</span>
              </button>
              <button class="location-tab" :class="{ active: locationMode === 'address' }" @click="locationMode = 'address'">
                <span class="material-symbols-outlined">edit_location</span>
                <span>Адрес</span>
              </button>
              <button class="location-tab" :class="{ active: locationMode === 'map' }" @click="locationMode = 'map'">
                <span class="material-symbols-outlined">map</span>
                <span>На карте</span>
              </button>
            </div>

            <!-- Режим: выбор Meetup из списка -->
            <div v-if="locationMode === 'meetup'" class="location-meetup-list">
              <input
                v-model="locationQuery"
                type="text"
                placeholder="Поиск места..."
                @input="showLocationDropdown = true"
                @focus="showLocationDropdown = true"
                @blur="hideLocationDropdownDelayed"
              />
              <div class="location-dropdown" v-if="showLocationDropdown && filteredMeetups.length > 0">
                <div
                  v-for="meetup in filteredMeetups"
                  :key="meetup.id"
                  class="location-option"
                  :class="{ 'location-option-selected': form.meetupId === meetup.id }"
                  @mousedown="selectMeetup(meetup)"
                >
                  <span class="location-option-emoji">{{ meetup.emoji }}</span>
                  <div class="location-option-info">
                    <span class="location-option-name">{{ meetup.name }}</span>
                    <span class="location-option-address">{{ meetup.address }}</span>
                  </div>
                </div>
              </div>
              <div v-if="form.meetupId" class="location-selected">
                <span class="material-symbols-outlined">check_circle</span>
                <span>{{ selectedMeetupName }}</span>
              </div>
            </div>

            <!-- Режим: ввод адреса вручную -->
            <div v-if="locationMode === 'address'" class="location-address-input">
              <input
                v-model="form.customAddress"
                type="text"
                placeholder="Введите адрес проведения..."
                @input="form.meetupId = null"
              />
            </div>

            <!-- Режим: указать на карте -->
            <div v-if="locationMode === 'map'" class="location-map-pick">
              <button class="pick-on-map-btn" @click="openMapForPick">
                <span class="material-symbols-outlined">pin_drop</span>
                <span>Указать точку на карте</span>
              </button>
              <div v-if="form.customLat && form.customLng" class="location-selected">
                <span class="material-symbols-outlined">check_circle</span>
                <span>{{ form.customAddress || `${form.customLat.toFixed(5)}, ${form.customLng.toFixed(5)}` }}</span>
              </div>
            </div>
          </div>

          <!-- Кнопка отправки -->
          <button type="submit" class="submit-btn" :disabled="!isFormValid">
            <span class="material-symbols-outlined">event_available</span>
            <span>Создать встречу</span>
          </button>
        </form>
      </div>
    </div>

    <!-- Meetup Detail Modal -->
    <div class="modal-overlay" v-if="selectedMeetup" @click="closeMeetupDetail">
      <div class="meetup-detail-modal" @click.stop>
        <div class="meetup-detail-header">
          <div class="meetup-detail-emoji">{{ selectedMeetup.emoji || '🏋️' }}</div>
          <div class="meetup-detail-title-area">
            <h2>{{ selectedMeetup.name }}</h2>
            <div class="meetup-detail-meta">
              <span class="material-symbols-outlined">schedule</span>
              <span>{{ selectedMeetup.time }} • {{ selectedMeetup.location }}</span>
            </div>
          </div>
          <button class="meetup-detail-close" @click="closeMeetupDetail">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="meetup-detail-body">
          <!-- Теги -->
          <div class="meetup-detail-tags" v-if="selectedMeetup.type || selectedMeetup.quietCompanion">
            <span class="meetup-detail-tag" v-if="selectedMeetup.type">{{ selectedMeetup.type }}</span>
            <span class="meetup-detail-tag quiet" v-if="selectedMeetup.quietCompanion">🤫 Тихий компаньон</span>
            <span class="meetup-detail-tag level">{{ selectedMeetup.level }}</span>
          </div>

          <!-- Описание -->
          <p class="meetup-detail-desc" v-if="selectedMeetup.description">{{ selectedMeetup.description }}</p>

          <!-- Участники -->
          <div class="meetup-detail-participants">
            <h4>Участники</h4>
            <div class="meetup-detail-avatars">
              <img v-for="(avatar, i) in selectedMeetup.avatars?.slice(0, 6)" :key="i" class="meetup-detail-avatar" :src="avatar" alt="User" />
              <div class="meetup-detail-avatar-more" v-if="selectedMeetup.moreCount > 0">+{{ selectedMeetup.moreCount }}</div>
            </div>
            <div class="meetup-detail-count">
              <span>{{ selectedMeetup.participants }}/{{ selectedMeetup.maxParticipants }} записано</span>
            </div>
          </div>

          <!-- Кнопка действия -->
          <button
            class="meetup-detail-action"
            :class="{ joined: selectedMeetup.isJoined }"
            @click="selectedMeetup.isJoined ? handleLeaveMeetup(selectedMeetup.id) : handleJoinMeetup(selectedMeetup.id)"
          >
            <span class="material-symbols-outlined">{{ selectedMeetup.isJoined ? 'check_circle' : 'directions_run' }}</span>
            <span>{{ selectedMeetup.isJoined ? 'Вы участвуете' : 'Присоединиться' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- MapLight — полноэкранная карта (модальный оверлей) -->
    <transition name="maplight-fade">
      <MapLight v-if="showMapLight" @close="closeMapLight" />
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { config, placesApi, eventsApi } from '../config'
import { authApi } from '../api'
import { navigationStore } from '../stores/navigation'
import MapLight from './MapLight.vue'

const router = useRouter()
const mapRef = ref(null)
const showMapLight = ref(false)
let map = null
let miniRouteLayer = null
let miniUserLayer = null

// ============================================
// 👤 Профиль пользователя
// ============================================

const profileData = ref(null)
const empathyScore = ref(0)
const avatarUrl = ref('')
const isLoadingProfile = ref(true)

// Загрузка профиля пользователя
async function loadProfile() {
  try {
    isLoadingProfile.value = true
    const [profile, rating] = await Promise.all([
      authApi.getProfile(),
      authApi.getRating()
    ])
    
    profileData.value = profile
    empathyScore.value = rating?.empathy_score || 0
    
    // Получаем аватар из профиля
    if (profile?.avatar_url) {
      avatarUrl.value = profile.avatar_url
    } else {
      // Fallback — дефолтный аватар
      avatarUrl.value = 'https://via.placeholder.com/48?text=Avatar'
    }
    
    if (config.isDebug) console.log('👤 Profile loaded:', { profile, rating })
  } catch (e) {
    if (config.isDebug) console.warn('loadProfile error:', e)
    // fallback на дефолтные значения
    empathyScore.value = 0
    avatarUrl.value = 'https://via.placeholder.com/48?text=Avatar'
  } finally {
    isLoadingProfile.value = false
  }
}

// Подписка на навигацию из общего стора
const isNavigating = computed(() => navigationStore.isNavigating)
const navRemaining = computed(() => navigationStore.navRemaining)

// ============================================
// 🗺 Полноэкранная карта (MapLight)
// ============================================

function openMapLight() {
  showMapLight.value = true
}

function closeMapLight() {
  showMapLight.value = false
  // Проверяем есть ли координаты от MapLight (пользователь выбрал точку)
  setTimeout(() => {
    try {
      const pending = localStorage.getItem('shoulder_pending_event_location')
      const source = localStorage.getItem('shoulder_pending_event_source')
      if (pending) {
        const { lat, lng, address } = JSON.parse(pending)
        localStorage.removeItem('shoulder_pending_event_location')
        localStorage.removeItem('shoulder_pending_event_source')
        if (config.isDebug) console.log('📍 Event location received from MapLight:', { lat, lng, address, source })

        if (source === 'events_page') {
          localStorage.setItem('shoulder_event_location_ready', JSON.stringify({ lat, lng, address }))
          if (config.isDebug) console.log('📍 Redirecting back to EventsPage')
          router.push('/events')
        } else {
          // Стандартный путь — открываем модалку на MainPage
          form.value.customLat = lat
          form.value.customLng = lng
          form.value.customAddress = address
          form.value.meetupId = null
          locationMode.value = 'map'
          showCreateModal.value = true
        }
      }
    } catch (e) {
      if (config.isDebug) console.warn('closeMapLight: location restore error:', e)
    }
  }, 200)
}

// ============================================
// 📋 Детали мероприятия (модалка)
// ============================================

const selectedMeetup = ref(null)

function openMeetupDetail(meetup) {
  selectedMeetup.value = meetup
}

function closeMeetupDetail() {
  selectedMeetup.value = null
}

// ============================================
// 💡 Интересные факты (смена каждые 3 минуты)
// ============================================

const funFacts = [
  { emoji: '🏃', text: 'За один час бега человек сжигает в среднем 600-800 калорий. Это как съесть целую пиццу!', source: 'Исследование Harvard Medical School' },
  { emoji: '💪', text: 'Первые турники появились в России в начале XIX века. Их называли «шведские стенки».', source: 'История спорта' },
  { emoji: '🧘', text: 'Йога существует более 5000 лет. Это одна из древнейших физических практик в мире.', source: 'Древняя Индия' },
  { emoji: '🏋️', text: 'Мировой рекорд в жиме лёжа — 355 кг. Это как поднять четырёх средних медведей!', source: 'IPF World Records' },
  { emoji: '🌳', text: 'Парк Победы в Орле — одно из самых освещённых мест для вечерних пробежек в городе.', source: 'Местные жители' },
  { emoji: '🦌', text: 'После 30 минут прогулки в парке уровень кортизола (гормона стресса) снижается на 16%.', source: 'Journal of Environmental Psychology' },
  { emoji: '⚡', text: 'Утренняя тренировка повышает метаболизм на 15% на весь оставшийся день.', source: 'British Journal of Nutrition' },
  { emoji: '🧠', text: 'Физическая активность увеличивает объём гиппокампа — части мозга, отвечающей за память.', source: 'NeuroImage, 2020' },
  { emoji: '🤸', text: 'Гимнастика развивает координацию лучше любого другого вида спорта.', source: 'Спортивная наука' },
  { emoji: '🏃‍♀️', text: 'Бег на свежем воздухе сжигает на 10% больше калорий, чем на беговой дорожке.', source: 'Journal of Sports Science' },
  { emoji: '💧', text: 'За час интенсивной тренировки человек теряет до 1 литра воды. Не забывайте пить!', source: 'American Council on Exercise' },
  { emoji: '🌙', text: 'Вечерние тренировки улучшают качество сна, если заканчиваются за 2 часа до сна.', source: 'Sleep Medicine Reviews' },
  { emoji: '🥇', text: 'Стадион «Центральный» в Орле был построен в 1962 году. Ему более 60 лет!', source: 'История Орла' },
  { emoji: '🫁', text: 'Во время бега лёгкие перерабатывают до 100 литров воздуха в минуту.', source: 'Pulmonary Medicine' },
  { emoji: '🏆', text: 'Регулярные тренировки увеличивают продолжительность жизни на 3-7 лет.', source: 'WHO, 2020' },
]

const currentFactIndex = ref(0)
const factSecondsLeft = ref(180) // 3 минуты
let factTimer = null

const currentFact = computed(() => funFacts[currentFactIndex.value % funFacts.length])

const factTimerDisplay = computed(() => {
  const m = Math.floor(factSecondsLeft.value / 60)
  const s = factSecondsLeft.value % 60
  return `${m}:${s.toString().padStart(2, '0')}`
})

function startFactTimer() {
  factTimer = setInterval(() => {
    factSecondsLeft.value--
    if (factSecondsLeft.value <= 0) {
      currentFactIndex.value = (currentFactIndex.value + 1) % funFacts.length
      factSecondsLeft.value = 180
    }
  }, 1000)
}

function stopFactTimer() {
  if (factTimer) {
    clearInterval(factTimer)
    factTimer = null
  }
}

// Ваши мероприятия — заглушка (заменить на API)
const myMeetups = ref([])

// ============================================
// 🏟 Места (загружаются с сервера через GET /places)
// ============================================

const meetups = ref([])
const locationQuery = ref('')
const showLocationDropdown = ref(false)
let hideDropdownTimer = null

// Режим выбора места: 'meetup' | 'address' | 'map'
const locationMode = ref('meetup')

// Загрузка списка мест с бэка (GET /places)
async function fetchMeetups() {
  try {
    const res = await fetch(placesApi('/places'))
    const data = await res.json()
    
    // Маппим ответ бэкенда → внутренний формат
    const validActivities = ['running', 'strength', 'yoga', 'workout', 'other']
    
    meetups.value = (data.places || [])
      .filter(p => p.id && p.name && typeof p.lat === 'number' && typeof p.lon === 'number')
      .map(p => ({
        id: p.id,
        name: p.name,
        address: p.address || '',
        lat: p.lat,
        lng: p.lon,
        emoji: p.emoji || '📍',
        activityType: validActivities.includes(p.activity_type) ? p.activity_type : 'other',
      }))
      
    if (config.isDebug) console.log('📍 fetchMeetups: загружено мест:', meetups.value.length)
  } catch (e) {
    if (config.isDebug) console.warn('fetchMeetups: API недоступен, использую fallback', e)
    // Fallback — минимум данных
    meetups.value = []
  }
}

const filteredMeetups = computed(() => {
  if (!locationQuery.value.trim()) return meetups.value
  const q = locationQuery.value.toLowerCase()
  return meetups.value.filter(p =>
    p.name.toLowerCase().includes(q) || p.address.toLowerCase().includes(q)
  )
})

const selectedMeetupName = computed(() => {
  const m = meetups.value.find(p => p.id === form.value.meetupId)
  return m ? `${m.emoji} ${m.name} — ${m.address}` : ''
})

// ============================================
// 📝 Форма создания встречи
// ============================================

const showCreateModal = ref(false)
const formError = ref('') // Error message для валидации
const formErrorTimeout = ref(null)

const eventTypes = [
  { key: 'running', emoji: '🏃', label: 'Бег' },
  { key: 'strength', emoji: '🏋️', label: 'Силовая' },
  { key: 'yoga', emoji: '🧘', label: 'Йога' },
  { key: 'workout', emoji: '💪', label: 'Воркаут' },
  { key: 'other', emoji: '🎯', label: 'Другое' }
]

const typeEmoji = {
  running: '🏃',
  strength: '🏋️',
  yoga: '🧘',
  workout: '💪',
  other: '🎯'
}

const mainLevels = [
  { key: 'Новичок', emoji: '🌱', label: 'Новичок' },
  { key: 'Средний', emoji: '⚡', label: 'Средний' },
  { key: 'Профи', emoji: '🔥', label: 'Профи' }
]

const form = ref({
  name: '',
  description: '',
  type: '',
  maxParticipants: 4,
  date: '',
  time: '',
  quietCompanion: false,
  level: 'Новичок',
  // Место: либо meetupId, либо customAddress + координаты
  meetupId: null,
  customAddress: '',
  customLat: null,
  customLng: null
})

const isFormValid = computed(() => {
  if (!form.value.name || !form.value.type || !form.value.date || !form.value.time) return false
  // Нужно либо выбранное место, либо адрес, либо координаты
  if (form.value.meetupId) return true
  if (locationMode.value === 'address' && form.value.customAddress.trim()) return true
  if (locationMode.value === 'map' && form.value.customLat && form.value.customLng) return true
  return false
})

function selectMeetup(meetup) {
  form.value.meetupId = meetup.id
  form.value.customAddress = ''
  form.value.customLat = null
  form.value.customLng = null
  locationQuery.value = meetup.name
  showLocationDropdown.value = false
}

function hideLocationDropdownDelayed() {
  hideDropdownTimer = setTimeout(() => {
    showLocationDropdown.value = false
  }, 200)
}

function openCreateModal() {
  showCreateModal.value = true
  locationMode.value = 'meetup'
  const today = new Date()
  form.value.date = today.toISOString().split('T')[0]
  // Обновляем список мест при открытии модалки
  fetchMeetups()
}

function closeModal() {
  showCreateModal.value = false
  formError.value = ''
  if (formErrorTimeout.value) clearTimeout(formErrorTimeout.value)
  if (hideDropdownTimer) clearTimeout(hideDropdownTimer)
  // Останавливаем проверку pending location — модалка закрыта
  if (window.__mainPagePendingCheckInterval) {
    clearInterval(window.__mainPagePendingCheckInterval)
    window.__mainPagePendingCheckInterval = null
  }
}

function closeModalAndReset() {
  closeModal()
  resetForm()
}

function resetForm() {
  form.value = {
    name: '',
    description: '',
    type: '',
    maxParticipants: 4,
    date: '',
    time: '',
    quietCompanion: false,
    level: 'Новичок',
    meetupId: null,
    customAddress: '',
    customLat: null,
    customLng: null
  }
  locationQuery.value = ''
  locationMode.value = 'meetup'
  showLocationDropdown.value = false
}

// ============================================
// 🗺 Указать место на карте
// ============================================

function openMapForPick() {
  // Не закрываем модалку полностью — просто скрываем
  // чтобы форма не сбрасывалась
  showCreateModal.value = false
  showMapLight.value = true
  setTimeout(() => {
    if (window.__setMapPickMode) {
      window.__setMapPickMode('event')
    }
  }, 500)
}

// Вызывается из MapLight когда пользователь выбрал точку на карте
function setEventLocation(lat, lng, address) {
  form.value.customLat = lat
  form.value.customLng = lng
  form.value.customAddress = address || `${lat.toFixed(5)}, ${lng.toFixed(5)}`
  form.value.meetupId = null
  locationMode.value = 'map'
  // Снова открываем модалку
  setTimeout(() => {
    showCreateModal.value = true
  }, 300)
}

// LocalStorage
const STORAGE_KEY = 'shoulder_events'

function loadFromLocalStorage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) return JSON.parse(stored)
  } catch (e) {
    console.warn('LocalStorage parse error:', e)
  }
  return null
}

function saveToLocalStorage(events) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(events))
  } catch (e) {
    console.warn('LocalStorage save error:', e)
  }
}

// Создать мероприятие — бэк (places + events) + localStorage fallback
async function submitEventToBackend(eventData) {
  try {
    let spotId = null

    // Если место из базы — используем его ID
    if (eventData.meetupId) {
      spotId = eventData.meetupId
    } else {
      // Своё место — создаём через places service
      const placePayload = {
        name: eventData.locationShort,
        description: eventData.description || '',
        lat: eventData.customLat,
        lon: eventData.customLng,
        address: eventData.customAddress || eventData.locationShort,
        rating: 0,
        emoji: '📍',
        category: 'my_spot',
        image: '',
        gallery: [],
        is_anonymous: eventData.anonymous,
        activity_type: eventData.type,
        noise_level: 0,
        light_availability: 0,
        conveniences_availability: false
      }

      if (config.isDebug) console.log('📍 Создаём место:', placePayload)

      const placeRes = await fetch(placesApi('/places/create'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(placePayload)
      })
      const placeData = await placeRes.json()
      spotId = placeData.place?.id || placeData.id
      if (config.isDebug) console.log('✅ Место создано, spot_id:', spotId)
    }

    // Создаём event
    const eventPayload = {
      spot_id: spotId,
      title: eventData.name,
      description: eventData.description,
      max_participants: eventData.maxParticipants,
      duration_minutes: 60,
      start_time: eventData.startTime,
      photo_url: null,
      anonymous: eventData.anonymous
    }

    if (config.isDebug) console.log('📅 Создаём event:', eventPayload)

    const res = await fetch(eventsApi('/events'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(localStorage.getItem('token') ? { Authorization: `Bearer ${localStorage.getItem('token')}` } : {}) },
      body: JSON.stringify(eventPayload)
    })
    const data = await res.json()

    if (data.event) {
      myMeetups.value.unshift(data.event)
    }
    const allStored = loadFromLocalStorage() || []
    allStored.unshift(data.event)
    saveToLocalStorage(allStored)
    return data.event
  } catch (e) {
    if (config.isDebug) console.warn('submitEventToBackend: API недоступен, localStorage', e)

    const newEventObj = {
      id: Date.now(),
      name: eventData.name,
      emoji: typeEmoji[eventData.type] || '🏋️',
      date: eventData.date,
      time: eventData.time,
      locationShort: eventData.locationShort,
      location: eventData.location,
      description: eventData.description,
      level: eventData.level,
      type: eventData.type,
      quietCompanion: eventData.quietCompanion,
      anonymous: eventData.anonymous,
      participants: 1,
      maxParticipants: eventData.maxParticipants,
      isJoined: true,
      avatars: ['https://lh3.googleusercontent.com/aida-public/AB6AXuDpfv2jdSpqPq9LfvhaIC8_axb5WLqMdlPMo9iVnmCZV8e7fY4XQvMbhDbl0SVzSyfN91CMhBYOC6FX2iGTaTWJ5qQkAwtiWjRwE9blPtdUDmNm-4m8trXbyzsMZRYDbkMcn0tHAEwV7HDDzalxua2JqK3qpMES04PRV9y4wsePZPWgNtwrV-VwSTlTD1f4jdt8EH1Ku4My8rwhXBhs7Zl7kUsQmMG619SEjGC9TCyPrQhaslXv1EAD9w4loswmmyy4-4QVmLnRcF0'],
      moreCount: 0
    }

    myMeetups.value.unshift(newEventObj)
    syncMyMeetupsLocal()
    return newEventObj
  }
}

function submitEvent() {
  if (!isFormValid.value) return

  // Валидация: событие должно быть минимум на 30 минут позже текущего времени
  const now = new Date()
  const startTime = new Date(`${form.value.date}T${form.value.time}:00`)
  const minStartTime = new Date(now.getTime() + 30 * 60 * 1000) // сейчас + 30 минут
  
  if (startTime < minStartTime) {
    formError.value = 'Событие должно быть запланировано минимум на 30 минут позже текущего времени'
    
    // Очищаем ошибку через 5 секунд
    if (formErrorTimeout.value) clearTimeout(formErrorTimeout.value)
    formErrorTimeout.value = setTimeout(() => {
      formError.value = ''
    }, 5000)
    return
  }

  let locationShort = ''
  let location = ''

  if (locationMode.value === 'meetup' && form.value.meetupId) {
    const m = meetups.value.find(p => p.id === form.value.meetupId)
    locationShort = m?.name || ''
    location = m ? `${m.name}, ${m.address}` : ''
  } else if (locationMode.value === 'address') {
    locationShort = form.value.customAddress
    location = form.value.customAddress
  } else if (locationMode.value === 'map') {
    locationShort = form.value.customAddress || `${form.value.customLat.toFixed(5)}, ${form.value.customLng.toFixed(5)}`
    location = form.value.customAddress || `${form.value.customLat.toFixed(5)}, ${form.value.customLng.toFixed(5)}`
  }

  // Формируем ISO datetime для start_time
  const startTimeIso = startTime.toISOString()

  const eventData = {
    name: form.value.name,
    description: form.value.description,
    type: form.value.type,
    date: form.value.date,
    time: form.value.time,
    startTime: startTimeIso,
    meetupId: form.value.meetupId,
    customAddress: form.value.customAddress || null,
    customLat: form.value.customLat,
    customLng: form.value.customLng,
    locationShort,
    location,
    quietCompanion: form.value.quietCompanion,
    anonymous: form.value.quietCompanion, // quietCompanion → anonymous
    level: form.value.level,
    maxParticipants: form.value.maxParticipants,
    user_id: 1
  }

  submitEventToBackend(eventData)
  closeModal()
}

// ============================================
// 🤝 Присоединиться / Отписаться (API + localStorage)
// ============================================

// Бэк эндпоинты (Swagger):
// POST /api/v1/events/{event_id}/join
// POST /api/v1/events/{event_id}/cancel  (не DELETE!)
// POST /api/v1/events/{event_id}/checkin

async function handleJoinMeetup(meetupId, userId = 1) {
  try {
    const res = await fetch(eventsApi(`/events/${meetupId}/join`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(localStorage.getItem('token') ? { Authorization: `Bearer ${localStorage.getItem('token')}` } : {}) },
      body: JSON.stringify({ user_id: userId })
    })

    const data = await res.json()

    const idx = myMeetups.value.findIndex(m => m.id === meetupId)
    if (idx !== -1) {
      myMeetups.value[idx] = { ...myMeetups.value[idx], isJoined: true, participants: data.participants }
    }
    // Обновляем выбранное мероприятие если оно открыто
    if (selectedMeetup.value && selectedMeetup.value.id === meetupId) {
      selectedMeetup.value.isJoined = true
      selectedMeetup.value.participants = data.participants
    }
    syncMyMeetupsLocal()
    return data
  } catch (e) {
    if (config.isDebug) console.warn(`handleJoinMeetup: API недоступен, localStorage`)

    const idx = myMeetups.value.findIndex(m => m.id === meetupId)
    if (idx !== -1) {
      const m = myMeetups.value[idx]
      if (m.participants < m.maxParticipants && !m.isJoined) {
        myMeetups.value[idx] = { ...m, isJoined: true, participants: m.participants + 1 }
      }
    }
    syncMyMeetupsLocal()
    return null
  }
}

async function handleLeaveMeetup(meetupId, userId = 1) {
  try {
    const res = await fetch(eventsApi(`/events/${meetupId}/cancel`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(localStorage.getItem('token') ? { Authorization: `Bearer ${localStorage.getItem('token')}` } : {}) },
      body: JSON.stringify({ user_id: userId })
    })

    const data = await res.json()

    const idx = myMeetups.value.findIndex(m => m.id === meetupId)
    if (idx !== -1) {
      myMeetups.value[idx] = { ...myMeetups.value[idx], isJoined: false, participants: data.participants }
    }
    // Обновляем выбранное мероприятие если оно открыто
    if (selectedMeetup.value && selectedMeetup.value.id === meetupId) {
      selectedMeetup.value.isJoined = false
      selectedMeetup.value.participants = data.participants
    }
    syncMyMeetupsLocal()
    return data
  } catch (e) {
    if (config.isDebug) console.warn(`handleLeaveMeetup: API недоступен, localStorage`)

    const idx = myMeetups.value.findIndex(m => m.id === meetupId)
    if (idx !== -1) {
      const m = myMeetups.value[idx]
      if (m.isJoined) {
        myMeetups.value[idx] = { ...m, isJoined: false, participants: m.participants - 1 }
      }
    }
    syncMyMeetupsLocal()
    return null
  }
}

// Checkin на мероприятие (новый эндпоинт из Swagger)
async function handleCheckinMeetup(meetupId, userId = 1) {
  try {
    const res = await fetch(eventsApi(`/events/${meetupId}/checkin`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(localStorage.getItem('token') ? { Authorization: `Bearer ${localStorage.getItem('token')}` } : {}) },
      body: JSON.stringify({ user_id: userId })
    })

    const data = await res.json()
    return data
  } catch (e) {
    if (config.isDebug) console.warn(`handleCheckinMeetup: API недоступен`)
    return null
  }
}

// ============================================
// 🔌 API HANDLES
// ============================================

// --- Places (места на карте) ---
const places = ref([])

// 1. Получить все места
async function fetchPlaces() {
  try {
    const res = await fetch(placesApi('/places'))
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
    const res = await fetch(placesApi(`/places/${id}`))
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
      placesApi(`/places/nearby?lat=${lat}&lng=${lng}&radius=${radius}`)
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

// Заглушка данных — мои мероприятия
const mockMeetups = [
  {
    id: 1,
    name: 'Вечернее кардио',
    time: '19:00',
    locationShort: 'Парк',
    location: 'Парк Победы',
    level: 'Новичок',
    description: 'Лёгкое кардио для разогрева перед основной тренировкой.',
    participants: 3,
    maxParticipants: 5,
    isJoined: true,
    type: 'Бег',
    quietCompanion: false,
    avatars: [
      'https://lh3.googleusercontent.com/aida-public/AB6AXuCaPrzntHOHOKvG0BIVPpc_3b2THNM8JxRVn-Vy0qppvVs3OLYoEPBUmcOdAbbYL66LZ6swLoWGWnM2a8lrbZU_2FeRJB6V09iN7R7gCdvzG70oNaGwQHuTDTuWLxFZIcsCuyPKDTxTTlCa-mIDWw_u6ICDWyE7PTSipMhDpdIaIRBWarjXJOQpXw5xQtV9t9i6PKTqJsG-cMsz5IH400UKj9VD_MVWUHv6Rp7fSO9oCivO9qH9carbZ6v8a4p63_S046k5bphL43U',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBE_honUQO8Mm-QEHIB3Bz94CyHvcv9VD7wLKYfJGSxND4d3rQNIYkCNg_qVQePsYqUC1Jy4-b1crYdzSN-S7OGgnWogDfbARxuOKErajv7ODK6tavnPTZcFSFrmOmDrbzzIfPj5GSkjn5JIPc3o782XNLA4rrC7Nwxr80tj710WdoTF327craU0496uTzPJI0jeoDAlN3sgoYDDJfoWqkLus8ZYMhGwciYtEaoLiCc99uhOxpdQXA4D1tUt4kuiNqmec6U7SsoXt0',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuDZu_-XWMjzYuGka2A9dsf14T394twZ1a7cCoJh4pgNf66M6xmaf1fy2Y5u_H1MRrf88srxGCmp_Q5ds3_uMC8oyOiF0gh3Hv541T9PEV2VM1_jsojZRXaVXhRhpu2_3tJNiG2y85-X-dc'
    ],
    moreCount: 2
  }
]

// 5. Получить мои мероприятия
// Читаем из localStorage (EventsPage сохраняет при join/leave)
const MY_MEETUPS_KEY = 'shoulder_my_meetups'

async function fetchMyMeetups() {
  try {
    const stored = localStorage.getItem(MY_MEETUPS_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      myMeetups.value = parsed
      if (config.isDebug) console.log('📋 fetchMyMeetups: из localStorage,', parsed.length, 'встреч')
      return
    }

    // Fallback на моки
    myMeetups.value = mockMeetups
  } catch (e) {
    if (config.isDebug) console.warn('fetchMyMeetups: ошибка', e)
    myMeetups.value = mockMeetups
  }
}

// Слушаем изменения localStorage (join/leave из EventsPage)
window.addEventListener('storage', (e) => {
  if (e.key === MY_MEETUPS_KEY) {
    if (config.isDebug) console.log('📋 MainPage: обновление моих встреч из storage')
    fetchMyMeetups()
  }
})

// Синхронизация: сохраняем мои встречи в localStorage
function syncMyMeetupsLocal() {
  try {
    localStorage.setItem(MY_MEETUPS_KEY, JSON.stringify(myMeetups.value))
    window.dispatchEvent(new Event('storage'))
  } catch (e) {
    console.warn('syncMyMeetupsLocal error:', e)
  }
}

// ============================================

onMounted(async () => {
  await nextTick()

  // Загружаем профиль пользователя
  await loadProfile()

  // Экспортируем функцию для MapLight
  window.__setMapPickMode = null
  window.setEventLocation = setEventLocation

  // Загружаем meetups
  await fetchMeetups()

  // Проверяем пришёл ли пользователь с EventsPage для выбора точки
  const eventSource = localStorage.getItem('shoulder_pending_event_source')
  if (eventSource === 'events_page') {
    if (config.isDebug) console.log('📍 EventsPage user — opening MapLight in event mode')
    // Открываем MapLight
    showMapLight.value = true
    // Устанавливаем режим event после монтирования MapLight
    await nextTick()
    setTimeout(() => {
      if (window.__setMapPickMode) {
        window.__setMapPickMode('event')
      }
    }, 300)
  }

  // Проверяем есть ли pending location от карты
  // Небольшая задержка чтобы MapLight успел сохранить данные
  setTimeout(() => {
    try {
      const pending = localStorage.getItem('shoulder_pending_event_location')
      const source = localStorage.getItem('shoulder_pending_event_source')
      if (pending) {
        const { lat, lng, address } = JSON.parse(pending)
        localStorage.removeItem('shoulder_pending_event_location')
        localStorage.removeItem('shoulder_pending_event_source')
        if (config.isDebug) console.log('📍 Pending location restored:', { lat, lng, address, source })

        if (source === 'events_page') {
          // Сохраняем координаты для EventsPage
          localStorage.setItem('shoulder_event_location_ready', JSON.stringify({ lat, lng, address }))
          // Возвращаемся на EventsPage
          if (config.isDebug) console.log('📍 Redirect back to EventsPage')
          // Навигация через router
          router.push('/events')
          // Ждём пока EventsPage смонтируется и заберёт данные
          setTimeout(() => {
            window.__eventsPageLocationReady = { lat, lng, address }
          }, 300)
        } else {
          // Открываем модалку с данными
          form.value.customLat = lat
          form.value.customLng = lng
          form.value.customAddress = address
          form.value.meetupId = null
          locationMode.value = 'map'
          showCreateModal.value = true
        }
      }
    } catch (e) {
      if (config.isDebug) console.warn('Pending location restore error:', e)
    }
  }, 200)

  // Периодическая проверка pending location (для случая когда EventsPage → MapLight → MainPage)
  // MainPage уже смонтирован, а данные появляются после выбора точки на карте
  const pendingCheckInterval = setInterval(() => {
    try {
      const pending = localStorage.getItem('shoulder_pending_event_location')
      const source = localStorage.getItem('shoulder_pending_event_source')
      if (pending) {
        const { lat, lng, address } = JSON.parse(pending)
        localStorage.removeItem('shoulder_pending_event_location')
        localStorage.removeItem('shoulder_pending_event_source')
        if (config.isDebug) console.log('📍 Pending location restored (interval):', { lat, lng, address, source })

        if (source === 'events_page') {
          localStorage.setItem('shoulder_event_location_ready', JSON.stringify({ lat, lng, address }))
          router.push('/events')
          setTimeout(() => {
            window.__eventsPageLocationReady = { lat, lng, address }
          }, 300)
        } else {
          form.value.customLat = lat
          form.value.customLng = lng
          form.value.customAddress = address
          form.value.meetupId = null
          locationMode.value = 'map'
          showCreateModal.value = true
        }
        clearInterval(pendingCheckInterval)
        window.__mainPagePendingCheckInterval = null
      }
    } catch (e) {}
  }, 500)

  window.__mainPagePendingCheckInterval = pendingCheckInterval

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

    // Если навигация уже активна — рисуем маршрут на мини-карте
    if (navigationStore.isNavigating && navigationStore.routeCoords.length > 0) {
      if (config.isDebug) console.log('MainPage onMounted: navigation active, drawing mini route')
      drawMiniRoute()
    }
  }

  // Загружаем мероприятия (заглушка или API)
  await fetchMyMeetups()

  // Запускаем таймер фактов
  startFactTimer()
})

onUnmounted(() => {
  stopFactTimer()
  // Очищаем интервал проверки pending location
  if (window.__mainPagePendingCheckInterval) {
    clearInterval(window.__mainPagePendingCheckInterval)
    window.__mainPagePendingCheckInterval = null
  }
})

// Отслеживаем изменения навигации — рисуем маршрут на мини-карте
watch(
  () => navigationStore.isNavigating,
  async (val) => {
    await nextTick()
    if (config.isDebug) console.log('MainPage nav watch:', val, 'map:', !!map)
    if (val && map) {
      drawMiniRoute()
    } else if (!val) {
      clearMiniRoute()
    }
  },
  { immediate: true }
)

watch(
  () => navigationStore.routeCoords.length,
  async (len) => {
    await nextTick()
    if (config.isDebug) console.log('MainPage routeCoords watch:', len, 'map:', !!map)
    if (map && navigationStore.isNavigating && len > 0) {
      drawMiniRoute()
    }
  }
)

watch(
  () => navigationStore.userPosition,
  async (pos) => {
    await nextTick()
    if (config.isDebug) console.log('MainPage userPos watch:', pos, 'map:', !!map)
    if (map && navigationStore.isNavigating) {
      drawMiniRoute()
    }
  }
)

function drawMiniRoute() {
  if (!map) {
    if (config.isDebug) console.warn('drawMiniRoute: map not ready')
    return
  }
  clearMiniRoute()

  const coords = navigationStore.routeCoords
  if (!coords || coords.length === 0) {
    if (config.isDebug) console.warn('drawMiniRoute: no coords')
    return
  }

  if (config.isDebug) console.log('drawMiniRoute: drawing', coords.length, 'points')

  const routeColor = navigationStore.routeColor

  // Рисуем маршрут
  miniRouteLayer = L.polyline(coords, {
    color: routeColor,
    weight: 4,
    opacity: 0.9,
    smoothFactor: 1
  }).addTo(map)

  // Точка пользователя
  if (navigationStore.userPosition) {
    miniUserLayer = L.circleMarker(
      [navigationStore.userPosition.lat, navigationStore.userPosition.lng],
      {
        radius: 6,
        fillColor: '#3b82f6',
        color: '#fff',
        weight: 2,
        fillOpacity: 0.9
      }
    ).addTo(map)
  }

  // Фитим карту под маршрут
  try {
    map.fitBounds(miniRouteLayer.getBounds(), { padding: [20, 20] })
  } catch (e) {}
}

function clearMiniRoute() {
  if (miniRouteLayer) {
    map.removeLayer(miniRouteLayer)
    miniRouteLayer = null
  }
  if (miniUserLayer) {
    map.removeLayer(miniUserLayer)
    miniUserLayer = null
  }
}
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.see-all {
  font-size: 13px;
  color: var(--primary);
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.see-all:hover {
  opacity: 0.7;
}

/* Navigation Info Section */
.nav-info-section {
  margin-top: -8px;
}

.nav-info-card {
  background: var(--surface-container-lowest);
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 16px;
  border: 2px solid var(--primary);
  animation: navPulse 2s ease-in-out infinite;
}

@keyframes navPulse {
  0%, 100% { border-color: var(--primary); }
  50% { border-color: #f97316; }
}

.nav-info-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ea580c, #f97316);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-info-icon .material-symbols-outlined {
  font-size: 24px;
  color: white;
}

.nav-info-data {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-info-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-info-row .material-symbols-outlined {
  font-size: 18px;
  color: var(--primary);
}

.nav-info-value {
  font-size: 14px;
  font-weight: 700;
  color: #1c1917;
}

.nav-info-label {
  font-size: 11px;
  font-weight: 600;
  color: #a8a29e;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
}

/* Tabs */
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

/* Meetup Tabs */
.meetup-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.meetup-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 12px;
  border: 2px solid #e7e8e9;
  background: var(--surface-container-low);
  color: #787170;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.meetup-tab.active {
  border-color: var(--primary);
  background: #ffedd5;
  color: var(--primary);
}

.meetup-tab:hover:not(.active) {
  border-color: var(--primary);
  background: #fff7ed;
}

/* Meetup Description */
.meetup-desc {
  font-size: 12px;
  color: #787170;
  line-height: 1.4;
  margin: 0;
}

/* Meetup Tags */
.meetup-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.meetup-type-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  background: #f5f5f4;
  color: #787170;
}

.meetup-quiet-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  background: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

/* Join Button with text */
.join-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-width: 155px;
  background: var(--primary-container);
  color: white;
  padding: 8px 14px;
  border-radius: 9999px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.join-btn:hover {
  background: #ea580c;
  transform: scale(1.05);
}

.join-btn .material-symbols-outlined {
  font-size: 18px;
}

/* Empty state */
.meetup-empty {
  text-align: center;
  padding: 32px 16px;
  color: #a8a29e;
}

.meetup-empty .empty-icon {
  font-size: 48px;
  font-variation-settings: 'FILL' 1;
  display: block;
  margin-bottom: 12px;
}

.meetup-empty p {
  font-size: 14px;
  margin: 0;
}

.empty-cta {
  margin-top: 16px;
  background: var(--primary-container);
  color: white;
  padding: 10px 20px;
  border-radius: 9999px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-cta:hover {
  background: #ea580c;
  transform: scale(1.05);
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
  gap: 12px;
  flex-wrap: wrap;
}

.avatars {
  display: flex;
  flex-shrink: 0;
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
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.join-count {
  font-size: 12px;
  color: #a8a29e;
  font-weight: 500;
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

/* Fun Fact Card */
.fact-card {
  background: var(--surface-container-lowest);
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-left: 4px solid #f59e0b;
}

.fact-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fact-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.fact-title .material-symbols-outlined {
  color: #f59e0b;
  font-variation-settings: 'FILL' 1;
}

.fact-title h4 {
  font-size: 14px;
  font-weight: bold;
  color: #1c1917;
}

.fact-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.fact-emoji {
  font-size: 36px;
  line-height: 1;
}

.fact-text {
  font-size: 13px;
  color: #57534e;
  line-height: 1.5;
  margin: 0;
}

.fact-source {
  font-size: 10px;
  color: #a8a29e;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ============================================
   Meetup Detail Modal
   ============================================ */

.meetup-detail-modal {
  position: relative;
  width: 100%;
  max-width: 480px;
  max-height: 85dvh;
  overflow-y: auto;
  background: var(--surface-container-lowest);
  border-radius: 24px 24px 0 0;
  animation: slideUp 0.3s ease;
}

.meetup-detail-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e7e8e9;
  position: relative;
}

.meetup-detail-emoji {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #fff7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.meetup-detail-title-area {
  flex: 1;
}

.meetup-detail-title-area h2 {
  font-size: 20px;
  font-weight: bold;
  color: #1c1917;
  margin: 0 0 6px;
}

.meetup-detail-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--primary);
}

.meetup-detail-meta .material-symbols-outlined {
  font-size: 16px;
}

.meetup-detail-close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: var(--surface-container-high);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #787170;
  transition: background 0.2s;
  flex-shrink: 0;
}

.meetup-detail-close:hover {
  background: #d1d5db;
}

.meetup-detail-body {
  padding: 20px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.meetup-detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meetup-detail-tag {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  background: #f5f5f4;
  color: #787170;
}

.meetup-detail-tag.quiet {
  background: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.meetup-detail-tag.level {
  background: #e0e7ff;
  color: #4338ca;
}

.meetup-detail-desc {
  font-size: 14px;
  color: #57534e;
  line-height: 1.6;
  margin: 0;
}

.meetup-detail-participants h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1c1917;
  margin: 0 0 12px;
}

.meetup-detail-avatars {
  display: flex;
  gap: 0;
  margin-bottom: 8px;
}

.meetup-detail-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid white;
  object-fit: cover;
  margin-left: -8px;
}

.meetup-detail-avatar:first-child {
  margin-left: 0;
}

.meetup-detail-avatar-more {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-container-high);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  color: #787170;
  border: 2px solid white;
  margin-left: -8px;
}

.meetup-detail-count {
  font-size: 13px;
  color: #a8a29e;
}

.meetup-detail-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: var(--primary-container);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.meetup-detail-action:hover {
  background: #ea580c;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(234, 88, 12, 0.3);
}

.meetup-detail-action.joined {
  background: var(--surface-container-high);
  color: #16a34a;
}

.meetup-detail-action.joined:hover {
  background: #d1d5db;
  color: #dc2626;
}

.meetup-detail-action .material-symbols-outlined {
  font-size: 20px;
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
  font-size: 11px;
  font-weight: 500;
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ============================================
   Modal (Create Event)
   ============================================ */

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: var(--surface-container-lowest);
  border-radius: 24px 24px 0 0;
  padding: 24px;
  width: 100%;
  max-width: 480px;
  max-height: 90dvh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: bold;
  color: #1c1917;
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
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

.modal-close:hover {
  background: #d1d5db;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #787170;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-group input[type="text"],
.form-group input[type="date"],
.form-group input[type="time"],
.form-group select,
.form-group textarea {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e7e8e9;
  background: var(--surface-container-low);
  font-size: 14px;
  color: #1c1917;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--primary);
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-row .form-group {
  flex: 1;
}

/* Type Selector */
.type-selector {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

/* Level Selector */
.level-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.level-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 4px;
  border-radius: 12px;
  border: 2px solid #e7e8e9;
  background: var(--surface-container-low);
  cursor: pointer;
  transition: all 0.2s;
}

.level-btn:hover {
  border-color: var(--primary);
  background: #fff7ed;
}

.level-btn-active {
  border-color: var(--primary);
  background: #ffedd5;
  box-shadow: 0 2px 8px rgba(234, 88, 12, 0.2);
}

.level-emoji {
  font-size: 24px;
}

.level-name {
  font-size: 11px;
  font-weight: 600;
  color: #787170;
}

.level-btn-active .level-name {
  color: var(--primary);
}

.type-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 4px;
  border-radius: 12px;
  border: 2px solid #e7e8e9;
  background: var(--surface-container-low);
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn:hover {
  border-color: var(--primary);
  background: #fff7ed;
}

.type-btn-active {
  border-color: var(--primary);
  background: #ffedd5;
  box-shadow: 0 2px 8px rgba(234, 88, 12, 0.2);
}

.type-emoji {
  font-size: 24px;
}

.type-name {
  font-size: 10px;
  font-weight: 600;
  color: #787170;
}

.type-btn-active .type-name {
  color: var(--primary);
}

/* Counter / Range */
.counter-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.counter-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: var(--surface-container-high);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  transition: background 0.2s;
  flex-shrink: 0;
}

.counter-btn:hover {
  background: #d1d5db;
}

.counter-btn .material-symbols-outlined {
  font-size: 20px;
}

.range-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e7e8e9;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(234, 88, 12, 0.3);
}

.range-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 8px rgba(234, 88, 12, 0.3);
}

.counter-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #a8a29e;
  margin-top: 2px;
}

/* Checkbox */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
  text-transform: none;
  letter-spacing: normal;
  font-size: 14px;
  color: #1c1917;
  padding: 12px;
  border-radius: 12px;
  background: var(--surface-container-low);
  border: 1px solid #e7e8e9;
  transition: all 0.2s;
}

.checkbox-label:hover {
  border-color: var(--primary);
  background: #fff7ed;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.checkbox-box {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 2px solid #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.checkbox-label input:checked + .checkbox-box {
  background: var(--primary);
  border-color: var(--primary);
}

.checkbox-icon {
  font-size: 18px;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
}

.checkbox-label input:checked + .checkbox-box .checkbox-icon {
  opacity: 1;
}

.checkbox-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.checkbox-text small {
  font-size: 11px;
  color: #a8a29e;
  font-weight: 400;
}

/* Location Search */
.location-group {
  position: relative;
}

/* Табы выбора способа */
.location-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}

.location-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 4px;
  border-radius: 8px;
  border: 2px solid #e7e8e9;
  background: var(--surface-container-low);
  color: #787170;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.location-tab:hover {
  border-color: var(--primary);
}

.location-tab.active {
  border-color: var(--primary);
  background: #ffedd5;
  color: var(--primary);
}

.location-tab .material-symbols-outlined {
  font-size: 16px;
}

/* Список meetup-ов */
.location-meetup-list {
  position: relative;
}

.location-meetup-list input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border-radius: 12px;
  border: 1px solid #e7e8e9;
  background: var(--surface-container-low);
  font-size: 14px;
  color: #1c1917;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: border-color 0.2s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='%23a8a29e'%3E%3Cpath d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: 12px center;
}

.location-meetup-list input:focus {
  border-color: var(--primary);
}

/* Адрес вручную */
.location-address-input input {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e7e8e9;
  background: var(--surface-container-low);
  font-size: 14px;
  color: #1c1917;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: border-color 0.2s;
}

.location-address-input input:focus {
  border-color: var(--primary);
}

/* Выбор на карте */
.location-map-pick {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pick-on-map-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border-radius: 12px;
  border: 2px dashed #e7e8e9;
  background: transparent;
  color: var(--primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.pick-on-map-btn:hover {
  border-color: var(--primary);
  background: rgba(234, 88, 12, 0.05);
}

.pick-on-map-btn .material-symbols-outlined {
  font-size: 20px;
}

.location-selected {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #dcfce7;
  border-radius: 8px;
  font-size: 12px;
  color: #15803d;
  font-weight: 500;
}

.location-selected .material-symbols-outlined {
  font-size: 18px;
}

.location-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 60;
  background: var(--surface-container-lowest);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e7e8e9;
}

.location-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.location-option:hover {
  background: #fff7ed;
}

.location-option-selected {
  background: #ffedd5;
}

.location-option-emoji {
  font-size: 20px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #fff7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.location-option-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.location-option-name {
  font-size: 14px;
  font-weight: 600;
  color: #1c1917;
}

.location-option-address {
  font-size: 12px;
  color: #a8a29e;
}

.location-selected {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #dcfce7;
  border-radius: 8px;
  font-size: 12px;
  color: #15803d;
  font-weight: 500;
  margin-top: 6px;
}

.location-selected .material-symbols-outlined {
  font-size: 18px;
}

/* Submit Button */
.submit-btn {
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
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(234, 88, 12, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn .material-symbols-outlined {
  font-size: 20px;
}
</style>

<style>
/* Анимация MapLight — без scoped, так как это модальный оверлей */
.maplight-fade-enter-active,
.maplight-fade-leave-active {
  transition: opacity 0.3s ease;
}

.maplight-fade-enter-from,
.maplight-fade-leave-to {
  opacity: 0;
}
</style>
