<template>
  <div class="rating-page">
    <!-- Top Navigation Bar -->
    <header class="top-nav">
      <div class="top-nav-left">
        <div class="avatar-small">
          <img :src="currentUser.avatar_url || defaultAvatar" alt="Аватар" />
        </div>
        <h1 class="brand-title">Рейтинг</h1>
      </div>
      <div class="top-nav-right">
        <button class="icon-btn" aria-label="Фильтр" @click="toggleFilter">
          <span class="material-symbols">filter_list</span>
        </button>
      </div>
    </header>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button
        class="filter-tab"
        :class="{ active: activeFilter === 'reliability' }"
        @click="activeFilter = 'reliability'"
      >
        <span class="material-symbols">verified_user</span>
        <span>Надёжность</span>
      </button>
      <button
        class="filter-tab"
        :class="{ active: activeFilter === 'empathy' }"
        @click="activeFilter = 'empathy'"
      >
        <span class="material-symbols">favorite</span>
        <span>Эмпатия</span>
      </button>
    </div>

    <main class="main-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <span class="material-symbols loading-icon">progress_activity</span>
        <p>Загрузка рейтинга...</p>
      </div>

      <!-- User Cards List -->
      <div v-else-if="sortedUsers.length > 0" class="users-list">
        <div
          v-for="(user, index) in sortedUsers"
          :key="user.user_id"
          class="user-card"
          :class="{
            'user-card-first': index === 0,
            'user-card-second': index === 1,
            'user-card-third': index === 2,
            'user-card-current': user.user_id === currentUserId,
          }"
        >
          <!-- Medal Badge -->
          <div v-if="index < 3" class="medal-badge" :class="`medal-${index + 1}`">
            <span class="material-symbols" :data-filled="true">{{ getMedalIcon(index + 1) }}</span>
          </div>
          <div v-else class="rank-badge">{{ index + 1 }}</div>

          <!-- User Info -->
          <div class="user-info">
            <div class="user-avatar">
              <img :src="user.avatar_url || defaultAvatar" alt="Аватар" />
            </div>
            <div class="user-details">
              <h3 class="user-name">{{ user.display_name || 'Пользователь' }}</h3>
              <div class="user-meta">
                <span class="meta-item" v-if="user.city">
                  <span class="material-symbols meta-icon">location_on</span>
                  {{ user.city }}
                </span>
                <span class="meta-item" v-if="user.fitness_level">
                  <span class="material-symbols meta-icon">fitness_center</span>
                  {{ getFitnessLevelLabel(user.fitness_level) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Score -->
          <div class="user-score" :class="`score-${activeFilter}`">
            <span class="score-value">{{ getScoreValue(user) }}</span>
            <span class="score-label">{{ getScoreLabel() }}</span>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <span class="material-symbols empty-icon">emoji_events</span>
        <p>Пока нет данных для отображения</p>
      </div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/" class="nav-item">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/'">map</span>
        <span>Карта</span>
      </router-link>
      <router-link to="/events" class="nav-item">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/events'">event</span>
        <span>Ивенты</span>
      </router-link>
      <router-link to="/profile" class="nav-item">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/profile'">person</span>
        <span>Профиль</span>
      </router-link>
      <router-link to="/rating" class="nav-item nav-item-active">
        <span class="material-symbols-outlined" data-filled="true">emoji_events</span>
        <span>Рейтинг</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../api/index'
import defaultAvatar from '../assets/default-avatar.svg'

const router = useRouter();

const currentUser = ref({
  avatar_url: '',
  display_name: '',
});

const currentUserId = ref(null);
const users = ref([]);
const loading = ref(true);
const activeFilter = ref('reliability');

const fitnessLevelLabels = {
  beginner: 'Начинающий',
  intermediate: 'Средний',
  advanced: 'Продвинутый',
};

const getFitnessLevelLabel = (level) => fitnessLevelLabels[level] || '';

const getMedalIcon = (rank) => {
  const icons = { 1: 'emoji_events', 2: 'emoji_events', 3: 'emoji_events' };
  return icons[rank] || 'star';
};

const getScoreValue = (user) => {
  if (activeFilter.value === 'reliability') {
    return user.reliability_score?.toFixed(1) || '0.0';
  }
  return user.empathy_score || '0';
};

const getScoreLabel = () => {
  return activeFilter.value === 'reliability' ? '%' : 'баллов';
};

const sortedUsers = computed(() => {
  const sorted = [...users.value].sort((a, b) => {
    if (activeFilter.value === 'reliability') {
      return (b.reliability_score || 0) - (a.reliability_score || 0);
    }
    return (b.empathy_score || 0) - (a.empathy_score || 0);
  });
  return sorted;
});

const toggleFilter = () => {
  activeFilter.value = activeFilter.value === 'reliability' ? 'empathy' : 'reliability';
};

function decodeToken() {
  const token = localStorage.getItem('token');
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload;
  } catch {
    return null;
  }
}

const loadRating = async () => {
  loading.value = true;
  try {
    // Load current user info
    const payload = decodeToken();
    if (payload) {
      currentUserId.value = payload.sub || payload.user_id;
    }

    const data = await authApi.getProfile();
    currentUser.value = {
      avatar_url: data.avatar_url || '',
      display_name: data.display_name || '',
    };

    // Load rating leaderboard
    const ratingData = await authApi.getRating();
    // Assuming the API returns a list of users with scores
    // If it returns a single user's rating, adjust accordingly
    if (Array.isArray(ratingData)) {
      users.value = ratingData;
    } else {
      // If single user rating, create a mock list
      users.value = [
        {
          user_id: currentUserId.value,
          display_name: data.display_name,
          avatar_url: data.avatar_url,
          city: data.city || data.preferences?.city,
          fitness_level: data.fitness_level,
          reliability_score: ratingData.reliability_score || 100,
          empathy_score: ratingData.empathy_score || 0,
          total_events: ratingData.total_events || 0,
          completed_events: ratingData.completed_events || 0,
        },
      ];
    }
  } catch (e) {
    console.error('Failed to load rating:', e.message);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadRating();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.rating-page {
  min-height: 100vh;
  background: #f3f4f5;
  font-family: 'Inter', sans-serif;
  color: #191c1d;
  padding-bottom: 80px;
}

/* ===== Top Nav ===== */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: #f3f4f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
}

.top-nav-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  overflow: hidden;
  background: #e1e3e4;
}

.avatar-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.brand-title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.top-nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #59413a;
  padding: 0;
  display: flex;
  transition: opacity 0.15s;
}

.icon-btn:hover {
  opacity: 0.8;
}

/* ===== Filter Tabs ===== */
.filter-tabs {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  max-width: 768px;
  margin: 0 auto;
}

.filter-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: #ffffff;
  border: 2px solid transparent;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #59413a;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}

.filter-tab .material-symbols {
  font-size: 20px;
}

.filter-tab.active {
  background: #ea580c;
  color: #ffffff;
  border-color: #ea580c;
}

.filter-tab.active .material-symbols {
  color: #ffffff;
}

/* ===== Main ===== */
.main-content {
  max-width: 768px;
  margin: 0 auto;
  padding: 0 16px 32px;
}

/* ===== Loading State ===== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 16px;
}

.loading-icon {
  font-size: 48px;
  color: #ea580c;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}

/* ===== Empty State ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 16px;
}

.empty-icon {
  font-size: 64px;
  color: #d1d5d8;
}

.empty-state p {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}

/* ===== Users List ===== */
.users-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ===== User Card ===== */
.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #ffffff;
  border-radius: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* First, second, third place styling */
.user-card-first {
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  border: 2px solid #ea580c;
}

.user-card-second {
  background: linear-gradient(135deg, #f3f4f5, #e7e8e9);
  border: 2px solid #9ca3af;
}

.user-card-third {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 2px solid #d97706;
}

.user-card-current {
  box-shadow: 0 0 0 2px #ea580c;
}

/* ===== Medal Badge ===== */
.medal-badge {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.medal-badge .material-symbols {
  font-size: 24px;
}

.medal-1 {
  background: linear-gradient(135deg, #fbbf24, #d97706);
  color: #ffffff;
}

.medal-2 {
  background: linear-gradient(135deg, #9ca3af, #6b7280);
  color: #ffffff;
}

.medal-3 {
  background: linear-gradient(135deg, #d97706, #92400e);
  color: #ffffff;
}

.rank-badge {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f5;
  font-size: 16px;
  font-weight: 700;
  color: #59413a;
  flex-shrink: 0;
}

/* ===== User Info ===== */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 9999px;
  overflow: hidden;
  background: #e1e3e4;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  min-width: 0;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  color: #9ca3af;
}

.meta-icon {
  font-size: 14px;
}

/* ===== User Score ===== */
.user-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 11px;
  font-weight: 500;
  color: #9ca3af;
  margin-top: 4px;
}

.score-reliability .score-value {
  color: #ea580c;
}

.score-empathy .score-value {
  color: #0069de;
}

/* ===== Bottom Nav ===== */
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
  text-align: center;
  line-height: 1.2;
}

.nav-item-active {
  background: #ea580c !important;
  color: #ffffff !important;
  padding: 6px 8px;
}

.nav-item-active:hover {
  background: #ea580c !important;
}

/* ===== Material Symbols ===== */
.material-symbols {
  font-family: 'Material Symbols Outlined';
  display: inline-block;
  line-height: 1;
  text-transform: none;
  letter-spacing: normal;
  word-wrap: normal;
  white-space: nowrap;
  direction: ltr;
  font-size: 24px;
}

.material-symbols[data-filled="true"] {
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

/* ===== Dark Theme ===== */
.dark-theme .rating-page {
  background: #0f0f1a;
  color: #e0e0e0;
}

.dark-theme .top-nav {
  background: #0f0f1a;
}

.dark-theme .filter-tab {
  background: #1a1a2e;
  color: #a0a0b0;
}

.dark-theme .filter-tab.active {
  background: #ea580c;
  color: #ffffff;
}

.dark-theme .user-card {
  background: #1a1a2e;
}

.dark-theme .user-card-first {
  background: linear-gradient(135deg, #1a1a2e, #2a1a0e);
}

.dark-theme .user-card-second {
  background: linear-gradient(135deg, #1a1a2e, #2a2a3e);
}

.dark-theme .user-card-third {
  background: linear-gradient(135deg, #1a1a2e, #2a2a1e);
}

.dark-theme .rank-badge {
  background: #16213e;
  color: #a0a0b0;
}

.dark-theme .user-name {
  color: #e0e0e0;
}

.dark-theme .bottom-nav {
  background: rgba(26, 26, 46, 0.9);
}

.dark-theme .nav-item:hover {
  background: #16213e;
}
</style>
