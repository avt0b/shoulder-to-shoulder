<template>
  <div class="events-page">
    <!-- Top Navigation -->
    <nav class="top-nav">
      <div class="nav-brand">
        <button class="back-btn" @click="$emit('close')">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <span class="page-title">Ивенты</span>
      </div>
      <button class="icon-button" @click="openCreateModal">
        <span class="material-symbols-outlined">add</span>
      </button>
    </nav>

    <!-- Main Content -->
    <main class="content">
      <!-- Filters -->
      <section class="filters-section">
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </section>

      <!-- Events List -->
      <section class="events-list">
        <div
          v-for="event in filteredEvents"
          :key="event.id"
          class="event-card"
          :class="{ 'event-card-joined': event.isJoined }"
        >
          <div class="event-header">
            <div class="event-emoji">{{ event.emoji }}</div>
            <div class="event-info">
              <h3 class="event-name">{{ event.name }}</h3>
              <div class="event-meta">
                <span class="material-symbols-outlined">schedule</span>
                <span>{{ event.date }}, {{ event.time }}</span>
                <span class="material-symbols-outlined">location_on</span>
                <span>{{ event.locationShort }}</span>
              </div>
            </div>
          </div>

          <p class="event-description" v-if="event.description">{{ event.description }}</p>

          <div class="event-tags">
            <span class="event-level" :class="`level-${event.level.toLowerCase()}`">{{ event.level }}</span>
            <span class="event-type" v-if="event.type">{{ event.type }}</span>
            <span class="event-quiet" v-if="event.quietCompanion">🤫 Тихий компаньон</span>
          </div>

          <div class="event-footer">
            <div class="avatars-row">
              <img
                v-for="(avatar, i) in event.avatars.slice(0, 3)"
                :key="i"
                class="avatar-sm"
                :src="avatar"
                alt="User"
              />
              <div class="avatar-more" v-if="event.moreCount > 0">+{{ event.moreCount }}</div>
            </div>
            <div class="event-actions">
              <span class="participants-count">{{ event.participants }}/{{ event.maxParticipants }}</span>
              <button
                class="action-btn"
                :class="{ 'action-btn-joined': event.isJoined }"
                @click="event.isJoined ? leaveEvent(event.id) : joinEvent(event.id)"
              >
                <span class="material-symbols-outlined">{{ event.isJoined ? 'check_circle' : 'person_add' }}</span>
                <span>{{ event.isJoined ? 'Участвую' : 'Присоединиться' }}</span>
              </button>
            </div>
          </div>
        </div>

        <div v-if="filteredEvents.length === 0" class="empty-state">
          <span class="material-symbols-outlined empty-icon">event_busy</span>
          <h3>Нет мероприятий</h3>
          <p>В этой категории пока ничего нет. Создайте первое мероприятие!</p>
        </div>
      </section>
    </main>

    <!-- FAB -->
    <div class="fab-create" @click="openCreateModal">
      <button class="fab-btn">
        <span class="material-symbols-outlined">add</span>
      </button>
    </div>

    <!-- Create Event Modal -->
    <div class="modal-overlay" v-if="showCreateModal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Создать встречу</h2>
          <button class="modal-close" @click="closeModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <form class="modal-form" @submit.prevent="submitEvent">
          <!-- Название -->
          <div class="form-group">
            <label>Название</label>
            <input v-model="form.name" type="text" placeholder="Утренняя пробежка" required />
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

          <!-- Выбор места (поиск + dropdown) -->
          <div class="form-group location-group">
            <label>Место проведения</label>
            <div class="location-search">
              <span class="material-symbols-outlined search-icon">location_on</span>
              <input
                v-model="locationQuery"
                type="text"
                placeholder="Начните вводить адрес..."
                @input="onLocationSearch"
                @focus="showLocationDropdown = true"
                @blur="hideLocationDropdownDelayed"
                ref="locationInputRef"
              />
            </div>
            <div class="location-dropdown" v-if="showLocationDropdown && filteredPlaces.length > 0">
              <div
                v-for="place in filteredPlaces"
                :key="place.id"
                class="location-option"
                :class="{ 'location-option-selected': form.locationId === place.id }"
                @mousedown="selectLocation(place)"
              >
                <span class="location-option-emoji">{{ place.emoji }}</span>
                <div class="location-option-info">
                  <span class="location-option-name">{{ place.name }}</span>
                  <span class="location-option-address">{{ place.address }}</span>
                </div>
              </div>
            </div>
            <div v-if="form.locationId" class="location-selected">
              <span class="material-symbols-outlined">check_circle</span>
              <span>Выбрано: {{ selectedLocationName }}</span>
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

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <a href="#" class="nav-item" :class="{ active: activeNav === 'map' }" @click.prevent="handleNav('map')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'map' }">map</span>
        <span>Карта</span>
      </a>
      <a href="#" class="nav-item active" @click.prevent>
        <span class="material-symbols-outlined filled">event</span>
        <span>Ивенты</span>
      </a>
      <a href="#" class="nav-item" :class="{ active: activeNav === 'routes' }" @click.prevent="handleNav('routes')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'routes' }">directions_run</span>
        <span>Маршруты</span>
      </a>
      <a href="#" class="nav-item" :class="{ active: activeNav === 'profile' }" @click.prevent="handleNav('profile')">
        <span class="material-symbols-outlined" :class="{ filled: activeNav === 'profile' }">person</span>
        <span>Профиль</span>
      </a>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { config, api } from '../config'

const emit = defineEmits(['close', 'navigate'])

const activeNav = ref('events')
const activeTab = ref('all')
const showCreateModal = ref(false)

const tabs = [
  { key: 'all', label: 'Все' },
  { key: 'running', label: 'Бег' },
  { key: 'powerlifting', label: 'Пауэрлифтинг' },
  { key: 'stretching', label: 'Растяжка' },
  { key: 'gymnastics', label: 'Гимнастика' },
  { key: 'my', label: 'Мои' }
]

const eventTypes = [
  { key: 'running', emoji: '🏃', label: 'Бег' },
  { key: 'powerlifting', emoji: '🏋️', label: 'Пауэрлифтинг' },
  { key: 'stretching', emoji: '🧘', label: 'Растяжка' },
  { key: 'gymnastics', emoji: '🤸', label: 'Гимнастика' }
]

const typeEmoji = {
  running: '🏃',
  powerlifting: '🏋️',
  stretching: '🧘',
  gymnastics: '🤸'
}

const typeLabels = {
  running: 'Бег',
  powerlifting: 'Пауэрлифтинг',
  stretching: 'Растяжка',
  gymnastics: 'Гимнастика'
}

// Заглушки всех мероприятий
const mockEvents = [
  {
    id: 1,
    name: 'Утренняя пробежка',
    emoji: '🏃',
    date: 'Сегодня',
    time: '07:00',
    locationShort: 'Парк Победы',
    location: 'Парк Победы, ул. Комсомольская',
    description: 'Лёгкий бег трусцой по парку. Темп разговорный, подойдёт для начинающих.',
    level: 'Новичок',
    type: 'running',
    quietCompanion: false,
    participants: 5,
    maxParticipants: 10,
    isJoined: false,
    avatars: [
      'https://lh3.googleusercontent.com/aida-public/AB6AXuCaPrzntHOHOKvG0BIVPpc_3b2THNM8JxRVn-Vy0qppvVs3OLYoEP_NiK5WnNkQJA1y6sWyVhCQ8dx2z99T-AdmkCaWD0LXCxgot0',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBE_honUQO8Mm-QEHIB3Bz94CyHvcv9VD7wLKYfJGSxND4d3rQNIYkCNg_qVQePsYqUC1Jy4-b1crYdzSN-S7OGgnWogDfbARxu',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuDZu_-XWMjzYuGka2A9dsf14T394twZ1a7cCoJh4pgNf66M6xmaf1fy2Y5u_H1MRrf88srxGCmp_Q5ds3_uMC8oyOiF0gh3Hv541'
    ],
    moreCount: 3
  },
  {
    id: 2,
    name: 'Силовая на турниках',
    emoji: '💪',
    date: 'Сегодня',
    time: '18:30',
    locationShort: 'Площадка ул. Гая',
    location: 'Спортивная площадка, ул. Гая',
    description: 'Подтягивания, отжимания, выходы силой. Разминка + основная часть.',
    level: 'Средний',
    type: 'gymnastics',
    quietCompanion: false,
    participants: 3,
    maxParticipants: 6,
    isJoined: true,
    avatars: [
      'https://lh3.googleusercontent.com/aida-public/AB6AXuC2URqWk5H4FTDLDLL0v1ywXo2oDhzArVrw_IEetPVa6vnn1NyW1eW8iBJz_J5WnNkQJA1y6sWyVhCQ8dx2z99T',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuDpfv2jdSpqPq9LfvhaIC8_axb5WLqMdlPMo9iVnmCZV8e7fY4XQvMbhDbl0SVzSyfN91CMhBYOC6FX2iGTaTWJ5qQkAwtiWjRwE9'
    ],
    moreCount: 1
  },
  {
    id: 3,
    name: 'Йога на набережной',
    emoji: '🧘',
    date: 'Завтра',
    time: '08:00',
    locationShort: 'Набережная Оки',
    location: 'Набережная Оки, Орёл',
    description: 'Утренняя йога на свежем воздухе. Коврик с собой!',
    level: 'Открыто',
    type: 'stretching',
    quietCompanion: true,
    participants: 8,
    maxParticipants: 10,
    isJoined: false,
    avatars: [
      'https://lh3.googleusercontent.com/aida-public/AB6AXuCaPrzntHOHOKvG0BIVPpc_3b2THNM8JxRVn-Vy0qppvVs3OLYoEP_NiK5WnNkQJA1y6sWyVhCQ8dx2z99T-AdmkCaWD0LXCxgot0',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBE_honUQO8Mm-QEHIB3Bz94CyHvcv9VD7wLKYfJGSxND4d3rQNIYkCNg_qVQePsYqUC1Jy4-b1crYdzSN-S7OGgnWogDfbARxu',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuDZu_-XWMjzYuGka2A9dsf14T394twZ1a7cCoJh4pgNf66M6xmaf1fy2Y5u_H1MRrf88srxGCmp_Q5ds3_uMC8oyOiF0gh3Hv541'
    ],
    moreCount: 6
  },
  {
    id: 4,
    name: 'Жим лёжа — прогрессия',
    emoji: '🏋️',
    date: 'Сегодня',
    time: '17:00',
    locationShort: 'Стадион «Центральный»',
    location: 'Стадион «Центральный», ул. Ленина',
    description: 'Работа над максимумом жима. Разминка 60%, рабочие подходы 80-90%.',
    level: 'Продвинутый',
    type: 'powerlifting',
    quietCompanion: true,
    participants: 2,
    maxParticipants: 4,
    isJoined: false,
    avatars: [
      'https://lh3.googleusercontent.com/aida-public/AB6AXuC2URqWk5H4FTDLDLL0v1ywXo2oDhzArVrw_IEetPVa6vnn1NyW1eW8iBJz_J5WnNkQJA1y6sWyVhCQ8dx2z99T',
      'https://lh3.googleusercontent.com/aida-public/AB6AXuDpfv2jdSpqPq9LfvhaIC8_axb5WLqMdlPMo9iVnmCZV8e7fY4XQvMbhDbl0SVzSyfN91CMhBYOC6FX2iGTaTWJ5qQkAwtiWjRwE9'
    ],
    moreCount: 0
  },
  {
    id: 5,
    name: 'Растяжка после тренировки',
    emoji: '🤸',
    date: 'Завтра',
    time: '21:00',
    locationShort: 'Парк Победы',
    location: 'Парк Победы, ул. Комсомольская',
    description: 'Стретчинг и восстановление после тяжёлых тренировок.',
    level: 'Новичок',
    type: 'stretching',
    quietCompanion: false,
    participants: 4,
    maxParticipants: 8,
    isJoined: false,
    avatars: [
      'https://lh3.googleusercontent.com/aida-public/AB6AXuCaPrzntHOHOKvG0BIVPpc_3b2THNM8JxRVn-Vy0qppvVs3OLYoEP_NiK5WnNkQJA1y6sWyVhCQ8dx2z99T-AdmkCaWD0LXCxgot0'
    ],
    moreCount: 4
  }
]

// Места с полными данными
const places = ref([
  { id: 1, name: 'Парк Победы', address: 'ул. Комсомольская, Орёл', lat: 52.9690, lng: 36.0820, emoji: '🏃' },
  { id: 2, name: 'Стадион «Центральный»', address: 'ул. Ленина, Орёл', lat: 52.9620, lng: 36.0740, emoji: '🏋️' },
  { id: 3, name: 'Набережная Оки', address: 'Набережная Оки, Орёл', lat: 52.9670, lng: 36.0680, emoji: '🧘' },
  { id: 4, name: 'Спортивная площадка', address: 'ул. Гая, Орёл', lat: 52.9610, lng: 36.0860, emoji: '💪' }
])

// Все мероприятия
const allEvents = ref([])

// Поиск места
const locationQuery = ref('')
const showLocationDropdown = ref(false)
const locationInputRef = ref(null)
let hideDropdownTimer = null

const filteredPlaces = computed(() => {
  if (!locationQuery.value.trim()) return places.value
  const q = locationQuery.value.toLowerCase()
  return places.value.filter(p =>
    p.name.toLowerCase().includes(q) || p.address.toLowerCase().includes(q)
  )
})

const selectedLocationName = computed(() => {
  const place = places.value.find(p => p.id === form.value.locationId)
  return place ? `${place.emoji} ${place.name} — ${place.address}` : ''
})

function onLocationSearch() {
  showLocationDropdown.value = true
}

function selectLocation(place) {
  form.value.locationId = place.id
  locationQuery.value = place.name
  showLocationDropdown.value = false
}

function hideLocationDropdownDelayed() {
  hideDropdownTimer = setTimeout(() => {
    showLocationDropdown.value = false
  }, 200)
}

// Форма нового мероприятия
const form = ref({
  name: '',
  type: '',
  maxParticipants: 4,
  date: '',
  time: '',
  quietCompanion: false,
  locationId: ''
})

// Валидация
const isFormValid = computed(() => {
  return form.value.name &&
    form.value.type &&
    form.value.date &&
    form.value.time &&
    form.value.locationId
})

// Фильтрация
const filteredEvents = computed(() => {
  if (activeTab.value === 'my') {
    return allEvents.value.filter(e => e.isJoined)
  }
  if (activeTab.value === 'all') {
    return allEvents.value
  }
  return allEvents.value.filter(e => e.type === activeTab.value)
})

// ============================================
// 🔌 API + LocalStorage
// ============================================

const STORAGE_KEY = 'shoulder_events'

function loadFromLocalStorage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
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

// Получить все мероприятия
async function fetchAllEvents() {
  try {
    const res = await fetch(api('/events'))
    const data = await res.json()
    allEvents.value = data.events
    return data.events
  } catch (e) {
    if (config.isDebug) console.warn('fetchAllEvents: API недоступен')

    // Пробуем localStorage
    const stored = loadFromLocalStorage()
    if (stored && stored.length > 0) {
      allEvents.value = stored
      return stored
    }

    // Fallback на моки
    allEvents.value = mockEvents
    return mockEvents
  }
}

// Записаться на мероприятие
async function joinEvent(eventId, userId = 1) {
  try {
    const res = await fetch(api(`/events/${eventId}/join`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    })
    const data = await res.json()
    const event = allEvents.value.find(e => e.id === eventId)
    if (event) {
      event.isJoined = true
      event.participants = data.participants
    }
    return data
  } catch (e) {
    if (config.isDebug) console.warn(`joinEvent: API недоступен`)
    const event = allEvents.value.find(e => e.id === eventId)
    if (event && event.participants < event.maxParticipants) {
      event.isJoined = true
      event.participants++
      saveToLocalStorage(allEvents.value)
    }
    return null
  }
}

// Отписаться от мероприятия
async function leaveEvent(eventId, userId = 1) {
  try {
    const res = await fetch(api(`/events/${eventId}/leave?user_id=${userId}`), {
      method: 'DELETE'
    })
    const data = await res.json()
    const event = allEvents.value.find(e => e.id === eventId)
    if (event) {
      event.isJoined = false
      event.participants = data.participants
    }
    return data
  } catch (e) {
    if (config.isDebug) console.warn(`leaveEvent: API недоступен`)
    const event = allEvents.value.find(e => e.id === eventId)
    if (event) {
      event.isJoined = false
      event.participants--
      saveToLocalStorage(allEvents.value)
    }
    return null
  }
}

// Создать мероприятие — бэк + localStorage fallback
async function submitEventToBackend(eventData) {
  try {
    const res = await fetch(api('/events'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(eventData)
    })
    const data = await res.json()
    allEvents.value.unshift(data.event)
    saveToLocalStorage(allEvents.value)
    return data.event
  } catch (e) {
    if (config.isDebug) console.warn('submitEventToBackend: API недоступен, сохраняем локально')

    // LocalStorage fallback
    const newEventObj = {
      id: Date.now(),
      name: eventData.name,
      emoji: typeEmoji[eventData.type] || '🏋️',
      date: eventData.date,
      time: eventData.time,
      locationShort: eventData.locationShort,
      location: eventData.location,
      description: eventData.description || '',
      level: 'Открыто',
      type: eventData.type,
      quietCompanion: eventData.quietCompanion,
      participants: 1,
      maxParticipants: eventData.maxParticipants,
      isJoined: true,
      avatars: ['https://lh3.googleusercontent.com/aida-public/AB6AXuDpfv2jdSpqPq9LfvhaIC8_axb5WLqMdlPMo9iVnmCZV8e7fY4XQvMbhDbl0SVzSyfN91CMhBYOC6FX2iGTaTWJ5qQkAwtiWjRwE9blPtdUDmNm-4m8trXbyzsMZRYDbkMcn0tHAEwV7HDDzalxua2JqK3qpMES04PRV9y4wsePZPWgNtwrV-VwSTlTD1f4jdt8EH1Ku4My8rwhXBhs7Zl7kUsQmMG619SEjGC9TCyPrQhaslXv1EAD9w4loswmmyy4-4QVmLnRcF0'],
      moreCount: 0
    }

    allEvents.value.unshift(newEventObj)
    saveToLocalStorage(allEvents.value)
    return newEventObj
  }
}

// Открыть модалку
function openCreateModal() {
  showCreateModal.value = true
  // Установить дату по умолчанию — сегодня
  const today = new Date()
  form.value.date = today.toISOString().split('T')[0]
  nextTick(() => {
    if (locationInputRef.value) locationInputRef.value.focus()
  })
}

// Закрыть модалку
function closeModal() {
  showCreateModal.value = false
  if (hideDropdownTimer) clearTimeout(hideDropdownTimer)
  resetForm()
}

// Сброс формы
function resetForm() {
  form.value = {
    name: '',
    type: '',
    maxParticipants: 4,
    date: '',
    time: '',
    quietCompanion: false,
    locationId: ''
  }
  locationQuery.value = ''
  showLocationDropdown.value = false
}

// Отправка формы
function submitEvent() {
  if (!isFormValid.value) return

  const location = places.value.find(p => p.id === form.value.locationId)
  const eventData = {
    name: form.value.name,
    type: form.value.type,
    date: form.value.date,
    time: form.value.time,
    locationId: form.value.locationId,
    locationShort: location?.name || '',
    location: `${location?.name}, ${location?.address}`,
    description: '',
    quietCompanion: form.value.quietCompanion,
    maxParticipants: form.value.maxParticipants,
    user_id: 1
  }

  submitEventToBackend(eventData)
  closeModal()
}

// Навигация
function handleNav(nav) {
  activeNav.value = nav
  if (nav !== 'events') {
    emit('navigate', nav)
  }
}

onMounted(async () => {
  await fetchAllEvents()
})
</script>

<style scoped>
.events-page {
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

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  color: var(--primary);
}

.back-btn:hover {
  background: rgba(120, 113, 108, 0.1);
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  letter-spacing: -0.025em;
  color: #1c1917;
  text-transform: uppercase;
}

.icon-button {
  padding: 8px;
  border-radius: 50%;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.2s;
  color: var(--primary);
}

.icon-button:hover {
  background: rgba(120, 113, 108, 0.1);
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

/* Filters */
.filters-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  transition: all 0.2s;
}

.tab.active {
  background: var(--primary);
  color: white;
  font-weight: bold;
}

/* Events List */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Event Card */
.event-card {
  background: var(--surface-container-lowest);
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.event-card-joined {
  border-left: 4px solid var(--primary);
}

.event-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.event-emoji {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #fff7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.event-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-name {
  font-size: 16px;
  font-weight: bold;
  color: #1c1917;
  margin: 0;
}

.event-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--primary);
}

.event-meta .material-symbols-outlined {
  font-size: 16px;
}

.event-description {
  font-size: 13px;
  color: #787170;
  line-height: 1.4;
  margin: 0;
}

.event-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.event-level {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.level-новичок {
  background: #dcfce7;
  color: #15803d;
}

.level-средний {
  background: #fef3c7;
  color: #b45309;
}

.level-продвинутый {
  background: #fee2e2;
  color: #b91c1c;
}

.level-открыто {
  background: #e0e7ff;
  color: #4338ca;
}

.event-type {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  background: #f5f5f4;
  color: #787170;
}

.event-quiet {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  background: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.event-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.avatars-row {
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
  margin-left: -4px;
}

.avatar-sm:first-child {
  margin-left: 0;
}

.avatar-more {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--surface-container-high);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  color: #787170;
  border: 2px solid white;
  margin-left: -4px;
}

.event-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.participants-count {
  font-size: 12px;
  color: #a8a29e;
  font-weight: 500;
  white-space: nowrap;
}

.action-btn {
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
  white-space: nowrap;
  flex-shrink: 0;
}

.action-btn:hover {
  background: #ea580c;
  transform: scale(1.05);
}

.action-btn .material-symbols-outlined {
  font-size: 18px;
}

.action-btn-joined {
  background: var(--surface-container-high);
  color: #16a34a;
}

.action-btn-joined:hover {
  background: #d1d5db;
  color: #dc2626;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: #a8a29e;
}

.empty-icon {
  font-size: 64px;
  font-variation-settings: 'FILL' 1;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #787170;
  margin: 0 0 8px;
}

.empty-state p {
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

/* FAB */
.fab-create {
  position: fixed;
  bottom: 112px;
  right: 24px;
  z-index: 40;
}

.fab-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--primary-container);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.3);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.fab-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 32px rgba(249, 115, 22, 0.4);
}

.fab-btn:active {
  transform: scale(0.95);
}

.fab-btn .material-symbols-outlined {
  font-size: 28px;
}

/* Modal */
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

.location-search {
  position: relative;
  display: flex;
  align-items: center;
}

.location-search .search-icon {
  position: absolute;
  left: 12px;
  color: #a8a29e;
  font-size: 20px;
  pointer-events: none;
}

.location-search input {
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
}

.location-search input:focus {
  border-color: var(--primary);
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
