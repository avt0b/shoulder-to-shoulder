<template>
  <div class="rating-page">
    <!-- Top Navigation Bar -->
    <header class="top-nav">
      <div class="top-nav-left">
        <div class="avatar-small">
          <img :src="currentUser.avatar_url || defaultAvatar" alt="Аватар" />
        </div>
        <div class="top-nav-user">
          <h1 class="brand-title">{{ currentUser.display_name || 'Пользователь' }}</h1>
          <span class="user-login">{{ currentUser.login || '' }}</span>
        </div>
      </div>
      <div class="top-nav-right">
        <button class="icon-btn" aria-label="Найти себя" @click="scrollToMyself">
          <span class="material-symbols">my_location</span>
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
          :ref="user.user_id === currentUserId ? 'myCardRef' : undefined"
          class="user-card"
          :class="{
            'user-card-highlighted': user.user_id === highlightedUserId,
          }"
          @click="user.user_id !== currentUserId && openUserProfile(user.user_id)"
          :style="{ cursor: user.user_id !== currentUserId ? 'pointer' : 'default' }"
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
                <span class="meta-item" v-if="user.age">
                  <span class="material-symbols meta-icon">cake</span>
                  {{ user.age }}
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

    <!-- Public Profile Modal -->
    <div v-if="showProfileModal" class="modal-overlay" @click.self="closeProfileModal">
      <div class="modal-content">
        <button class="modal-close" @click="closeProfileModal">
          <span class="material-symbols">close</span>
        </button>

        <div v-if="loadingProfile" class="profile-modal-loading">
          <span class="material-symbols loading-icon">progress_activity</span>
          <p>Загрузка профиля...</p>
        </div>

        <div v-else-if="viewedProfile" class="profile-modal-body">
          <!-- Avatar -->
          <div class="profile-modal-avatar">
            <img :src="viewedProfile.avatar_url || defaultAvatar" alt="Аватар" />
          </div>

          <!-- Name -->
          <h2 class="profile-modal-name">{{ viewedProfile.display_name || 'Пользователь' }}</h2>

          <!-- Meta info -->
          <div class="profile-modal-meta">
            <span class="meta-item" v-if="viewedProfile.city">
              <span class="material-symbols meta-icon">location_on</span>
              {{ viewedProfile.city }}
            </span>
            <span class="meta-item" v-if="viewedProfile.age">
              <span class="material-symbols meta-icon">cake</span>
              {{ viewedProfile.age }} лет
            </span>
            <span class="meta-item" v-if="viewedProfile.fitness_level">
              <span class="material-symbols meta-icon">fitness_center</span>
              {{ getFitnessLevelLabel(viewedProfile.fitness_level) }}
            </span>
          </div>

          <!-- Bio -->
          <p v-if="viewedProfile.bio" class="profile-modal-bio">{{ viewedProfile.bio }}</p>

          <!-- Stats -->
          <div class="profile-modal-stats">
            <div class="stat-item">
              <span class="material-symbols stat-icon">verified_user</span>
              <span class="stat-label">Надёжность</span>
              <span class="stat-value">{{ (viewedProfile.reliability_score || 0).toFixed(1) }}%</span>
            </div>
            <div class="stat-item">
              <span class="material-symbols stat-icon">favorite</span>
              <span class="stat-label">Эмпатия</span>
              <span class="stat-value">{{ viewedProfile.empathy_score || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="material-symbols stat-icon">event_available</span>
              <span class="stat-label">Мероприятий</span>
              <span class="stat-value">{{ viewedProfile.joined_events_count || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="material-symbols stat-icon">check_circle</span>
              <span class="stat-label">Посещено</span>
              <span class="stat-value">{{ viewedProfile.attended_events_count || 0 }}</span>
            </div>
          </div>

          <!-- Badges -->
          <div v-if="viewedProfile.badges && viewedProfile.badges.length > 0" class="profile-modal-badges">
            <h3 class="badges-title">Достижения</h3>
            <div class="badges-list">
              <span v-for="(badge, i) in viewedProfile.badges" :key="i" class="badge-chip">
                <span class="material-symbols badge-icon">emoji_events</span>
                {{ badge }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

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
import { authApi, toProxyUrl } from '../api/index'
import defaultAvatar from '../assets/default-avatar.svg'

const router = useRouter();

const currentUser = ref({
  avatar_url: '',
  display_name: '',
  login: '',
});

const currentUserId = ref(null);
const users = ref([]);
const loading = ref(true);
const activeFilter = ref('reliability');
const myCardRef = ref(null);
const highlightedUserId = ref(null);

// Public profile modal
const showProfileModal = ref(false);
const loadingProfile = ref(false);
const viewedProfile = ref(null);

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

const openUserProfile = async (userId) => {
  if (userId === currentUserId.value) return;
  showProfileModal.value = true;
  loadingProfile.value = true;
  viewedProfile.value = null;
  try {
    const profile = await authApi.getPublicProfile(userId);
    // Находим рейтинг из текущего списка
    const userInList = users.value.find(u => u.user_id === userId);
    viewedProfile.value = {
      ...profile,
      empathy_score: userInList?.empathy_score ?? 0,
      reliability_score: userInList?.reliability_score ?? 0,
      joined_events_count: profile.joined_events_count ?? 0,
      attended_events_count: profile.attended_events_count ?? 0,
      avatar_url: toProxyUrl(profile.avatar_url),
    };
  } catch (e) {
    console.error('Failed to load profile:', e.message);
  } finally {
    loadingProfile.value = false;
  }
};

const closeProfileModal = () => {
  showProfileModal.value = false;
  loadingProfile.value = false;
  viewedProfile.value = null;
};

const scrollToMyself = () => {
  if (!currentUserId.value) return;
  const el = Array.isArray(myCardRef.value) ? myCardRef.value[0] : myCardRef.value;
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  highlightedUserId.value = currentUserId.value;
  setTimeout(() => {
    highlightedUserId.value = null;
  }, 2000);
};

const loadRating = async () => {
  loading.value = true;
  try {
    // Получаем ID текущего пользователя из токена
    const payload = decodeToken();
    if (payload) {
      currentUserId.value = payload.sub || payload.user_id;
    }

    // Загружаем профиль текущего пользователя для отображения в шапке
    const profileData = await authApi.getProfile();
    currentUser.value = {
      avatar_url: toProxyUrl(profileData.avatar_url) || '',
      display_name: profileData.display_name || '',
      login: profileData.phone_number || '',
    };

    // Загружаем список всех пользователей с рейтингами
    const listData = await authApi.getAllUsers();
    if (listData && Array.isArray(listData.users)) {
      users.value = listData.users.map(u => ({
        ...u,
        avatar_url: toProxyUrl(u.avatar_url),
      }));
    } else if (Array.isArray(listData)) {
      users.value = listData.map(u => ({
        ...u,
        avatar_url: toProxyUrl(u.avatar_url),
      }));
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
  padding-bottom: 72px;
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

.top-nav-user {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 0;
}

.brand-title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1.2;
}

.user-login {
  font-size: 11px;
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
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
  padding: 0 12px 80px;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ===== Loading State ===== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 16px 80px;
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
  padding: 48px 16px 80px;
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

/* ===== User Card ===== */
.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #ffffff;
  border-radius: 16px;
  min-width: 0;
}

/* ===== Medal Badge ===== */
.medal-badge {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.medal-badge .material-symbols {
  font-size: 20px;
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
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f5;
  font-size: 14px;
  font-weight: 700;
  color: #59413a;
}

.user-card-highlighted {
  animation: highlightPulse 0.5s ease-in-out 2;
  box-shadow: 0 0 0 3px #ea580c, 0 0 20px rgba(234, 88, 12, 0.3);
}

@keyframes highlightPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
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
  width: 40px;
  height: 40px;
  min-width: 40px;
  border-radius: 9999px;
  overflow: hidden;
  background: #e1e3e4;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  min-width: 0;
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 2px;
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
  font-size: 11px;
  color: #9ca3af;
  white-space: nowrap;
}

.meta-icon {
  font-size: 13px;
}

/* ===== User Score ===== */
.user-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 52px;
  flex-shrink: 0;
}

.score-value {
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 10px;
  font-weight: 500;
  color: #9ca3af;
  margin-top: 2px;
}

@media (max-width: 380px) {
  .score-value {
    font-size: 16px;
  }
  .score-label {
    font-size: 9px;
  }
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

/* ===== Profile Modal ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.modal-content {
  background: #ffffff;
  border-radius: 20px;
  width: 100%;
  max-width: 420px;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.08);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #59413a;
  z-index: 1;
  transition: background 0.15s;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.15);
}

.modal-close .material-symbols {
  font-size: 20px;
}

.profile-modal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 24px;
}

.loading-icon {
  font-size: 36px;
  color: #ea580c;
  animation: spin 1s linear infinite;
}

.profile-modal-body {
  padding: 32px 20px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-modal-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: #e1e3e4;
  margin-bottom: 16px;
}

.profile-modal-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-modal-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 12px;
  text-align: center;
  color: #191c1d;
}

.profile-modal-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.profile-modal-meta .meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #9ca3af;
}

.profile-modal-meta .meta-icon {
  font-size: 16px;
}

.profile-modal-bio {
  font-size: 14px;
  color: #59413a;
  text-align: center;
  line-height: 1.5;
  margin: 0 0 20px;
  padding: 12px 16px;
  background: #f3f4f5;
  border-radius: 12px;
  width: 100%;
  box-sizing: border-box;
}

.profile-modal-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  width: 100%;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px;
  background: #f3f4f5;
  border-radius: 12px;
}

.stat-icon {
  font-size: 24px;
  color: #ea580c;
}

.stat-label {
  font-size: 11px;
  font-weight: 500;
  color: #9ca3af;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #191c1d;
}

.profile-modal-badges {
  width: 100%;
}

.badges-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px;
  color: #59413a;
}

.badges-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.badge-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  color: #c2410c;
}

.badge-icon {
  font-size: 16px;
}

/* Dark theme modal */
.dark-theme .modal-content {
  background: #1a1a2e;
}

.dark-theme .modal-close {
  background: rgba(255, 255, 255, 0.1);
  color: #e0e0e0;
}

.dark-theme .modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.dark-theme .profile-modal-name {
  color: #e0e0e0;
}

.dark-theme .profile-modal-bio {
  background: #16213e;
  color: #a0a0b0;
}

.dark-theme .stat-item {
  background: #16213e;
}

.dark-theme .stat-value {
  color: #e0e0e0;
}

.dark-theme .badges-title {
  color: #a0a0b0;
}

.dark-theme .badge-chip {
  background: #2a1a0e;
  border-color: #4a2a1e;
  color: #ea580c;
}
</style>
