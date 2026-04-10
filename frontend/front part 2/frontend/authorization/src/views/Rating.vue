<template>
  <div class="rating-page">
    <!-- Top Navigation Bar -->
    <header class="top-nav">
      <div class="top-nav-left">
        <div class="avatar-small">
          <img :src="userAvatar || defaultAvatar" alt="Аватар" />
        </div>
        <h1 class="brand-title">{{ userName || 'Имя Фамилия' }}</h1>
      </div>
      <div class="top-nav-right">
        <button class="icon-btn" @click="$router.push('/profile')" aria-label="Профиль">
          <span class="material-symbols">person</span>
        </button>
      </div>
    </header>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-tabs">
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'reliability' }"
          @click="activeFilter = 'reliability'"
        >
          <span class="material-symbols">verified_user</span>
          <span>По надёжности</span>
        </button>
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'empathy' }"
          @click="activeFilter = 'empathy'"
        >
          <span class="material-symbols">favorite</span>
          <span>По симпатии</span>
        </button>
      </div>
    </div>

    <main class="main-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <span class="material-symbols loading-spinner">progress_activity</span>
        <p>Загрузка...</p>
      </div>

      <!-- Users List -->
      <div v-else class="users-list">
        <div
          v-for="(user, index) in sortedUsers"
          :key="user.user_id"
          class="user-card"
          :class="`rank-${index < 3 ? index + 1 : 'default'}`"
        >
          <div class="user-rank">
            <span v-if="index < 3" class="rank-medal" :class="`medal-${index + 1}`">
              {{ ['🥇', '🥈', '🥉'][index] }}
            </span>
            <span v-else class="rank-number">#{{ index + 1 }}</span>
          </div>
          <div class="user-avatar">
            <img :src="user.avatar_url || defaultAvatar" alt="Аватар" />
          </div>
          <div class="user-info">
            <h3 class="user-name">{{ user.display_name || 'Аноним' }}</h3>
            <div class="user-meta">
              <span v-if="user.city" class="meta-item">
                <span class="material-symbols">location_on</span>
                {{ user.city }}
              </span>
              <span v-if="user.age" class="meta-item">
                <span class="material-symbols">cake</span>
                {{ user.age }} лет
              </span>
            </div>
            <div class="user-stats">
              <div class="stat">
                <span class="material-symbols stat-icon">verified_user</span>
                <span class="stat-value" :class="{ high: user.reliability_score >= 80 }">
                  {{ user.reliability_score.toFixed(1) }}%
                </span>
              </div>
              <div class="stat">
                <span class="material-symbols stat-icon">favorite</span>
                <span class="stat-value" :class="{ high: user.empathy_score >= 80 }">
                  {{ user.empathy_score }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="sortedUsers.length === 0" class="empty-state">
          <span class="material-symbols empty-icon">person_off</span>
          <p>Пользователи не найдены</p>
        </div>
      </div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <button class="nav-item">
        <span class="material-symbols">location_on</span>
        <span class="nav-label">Карты</span>
      </button>
      <button class="nav-item">
        <span class="material-symbols">calendar_month</span>
        <span class="nav-label">Ивенты</span>
      </button>
      <button class="nav-item">
        <span class="material-symbols">smart_toy</span>
        <span class="nav-label">Чат ИИ</span>
      </button>
      <button class="nav-item nav-item-active">
        <span class="material-symbols" :data-filled="true">emoji_events</span>
        <span class="nav-label">Рейтинг</span>
      </button>
      <button class="nav-item" @click="router.push('/profile')">
        <span class="material-symbols">person</span>
        <span class="nav-label">Профиль</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../api/index';
import defaultAvatar from '../assets/default-avatar.svg';

const router = useRouter();
const loading = ref(true);
const activeFilter = ref('reliability');
const users = ref([]);
const userAvatar = ref('');
const userName = ref('');

const loadProfile = async () => {
  try {
    const data = await authApi.getProfile();
    userAvatar.value = data.avatar_url || '';
    userName.value = data.display_name || '';
  } catch (e) {
    console.error('Failed to load profile:', e.message);
  }
};

// Mock API call - заглушка для получения всех пользователей с рейтингами
const fetchUsers = async () => {
  // TODO: Заменить на реальный запрос
  // const data = await ratingApi.getAllUsers();
  
  // Заглушка — моковые данные
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          user_id: '1',
          display_name: 'Алексей Петров',
          avatar_url: '',
          city: 'Москва',
          age: 28,
          reliability_score: 98.5,
          empathy_score: 142,
          badges: ['first_step', 'ironman', 'reliable'],
        },
        {
          user_id: '2',
          display_name: 'Мария Иванова',
          avatar_url: '',
          city: 'Санкт-Петербург',
          age: 24,
          reliability_score: 95.2,
          empathy_score: 138,
          badges: ['first_step', 'regular', 'empathy'],
        },
        {
          user_id: '3',
          display_name: 'Дмитрий Козлов',
          avatar_url: '',
          city: 'Казань',
          age: 31,
          reliability_score: 91.0,
          empathy_score: 125,
          badges: ['first_step', 'regular', 'social'],
        },
        {
          user_id: '4',
          display_name: 'Анна Смирнова',
          avatar_url: '',
          city: 'Екатеринбург',
          age: 26,
          reliability_score: 87.3,
          empathy_score: 118,
          badges: ['first_step', 'empathy'],
        },
        {
          user_id: '5',
          display_name: 'Сергей Волков',
          avatar_url: '',
          city: 'Новосибирск',
          age: 33,
          reliability_score: 84.1,
          empathy_score: 110,
          badges: ['first_step', 'regular'],
        },
        {
          user_id: '6',
          display_name: 'Елена Кузнецова',
          avatar_url: '',
          city: 'Краснодар',
          age: 22,
          reliability_score: 79.8,
          empathy_score: 105,
          badges: ['first_step'],
        },
        {
          user_id: '7',
          display_name: 'Артём Новиков',
          avatar_url: '',
          city: 'Ростов-на-Дону',
          age: 29,
          reliability_score: 76.4,
          empathy_score: 98,
          badges: [],
        },
        {
          user_id: '8',
          display_name: 'Ольга Морозова',
          avatar_url: '',
          city: 'Самара',
          age: 27,
          reliability_score: 72.9,
          empathy_score: 92,
          badges: [],
        },
        {
          user_id: '9',
          display_name: 'Игорь Соколов',
          avatar_url: '',
          city: 'Уфа',
          age: 35,
          reliability_score: 68.5,
          empathy_score: 85,
          badges: [],
        },
        {
          user_id: '10',
          display_name: 'Наталья Попова',
          avatar_url: '',
          city: 'Воронеж',
          age: 23,
          reliability_score: 65.0,
          empathy_score: 78,
          badges: [],
        },
      ]);
    }, 600);
  });
};

const sortedUsers = computed(() => {
  const sorted = [...users.value];
  if (activeFilter.value === 'reliability') {
    return sorted.sort((a, b) => b.reliability_score - a.reliability_score);
  } else {
    return sorted.sort((a, b) => b.empathy_score - a.empathy_score);
  }
});

onMounted(async () => {
  loading.value = true;
  await Promise.all([loadProfile(), fetchUsers().then(data => { users.value = data; })]);
  loading.value = false;
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

/* ===== Filter Bar ===== */
.filter-bar {
  padding: 8px 16px 12px;
  background: #f3f4f5;
  position: sticky;
  top: 56px;
  z-index: 40;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  background: #ffffff;
  border: 2px solid transparent;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 600;
  color: #59413a;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: all 0.2s;
}

.filter-tab .material-symbols {
  font-size: 20px;
}

.filter-tab.active {
  border-color: #c2410c;
  background: #fff0ea;
  color: #c2410c;
}

.filter-tab.active .material-symbols {
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 20;
}

.filter-tab:hover:not(.active) {
  background: #e7e8e9;
}

/* ===== Main Content ===== */
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
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  color: #9ca3af;
}

.loading-spinner {
  font-size: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  gap: 12px;
  background: #ffffff;
  border-radius: 16px;
  padding: 12px;
  transition: transform 0.15s, box-shadow 0.15s;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.user-card.rank-1 {
  background: linear-gradient(135deg, #fff8e1, #ffecb3);
  border: 2px solid #ffc107;
}

.user-card.rank-2 {
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
  border: 2px solid #9e9e9e;
}

.user-card.rank-3 {
  background: linear-gradient(135deg, #fbe9e7, #ffccbc);
  border: 2px solid #bf360c;
}

/* ===== Rank ===== */
.user-rank {
  flex-shrink: 0;
  width: 36px;
  text-align: center;
}

.rank-medal {
  font-size: 28px;
}

.rank-number {
  font-size: 14px;
  font-weight: 700;
  color: #9ca3af;
}

/* ===== Avatar ===== */
.user-avatar {
  position: relative;
  width: 48px;
  height: 48px;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 9999px;
  object-fit: cover;
  border: 2px solid #c2410c;
  background: #e1e3e4;
}

.role-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  background: #9b2f00;
  color: #ffffff;
  font-size: 8px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 9999px;
  border: 1px solid #ffffff;
}

/* ===== User Info ===== */
.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
}

.meta-item .material-symbols {
  font-size: 14px;
}

.user-stats {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-icon {
  font-size: 16px;
  color: #9ca3af;
}

.stat-value {
  font-size: 13px;
  font-weight: 600;
  color: #59413a;
}

.stat-value.high {
  color: #c2410c;
}

/* ===== Empty State ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  color: #9ca3af;
}

.empty-icon {
  font-size: 48px;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

/* ===== Bottom Nav ===== */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-around;
  gap: 4px;
  padding: 10px 8px max(20px, env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.04);
  z-index: 50;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: #59413a;
  padding: 6px 4px;
  border-radius: 9999px;
  cursor: pointer;
  transition: background 0.15s;
  min-width: 0;
  flex: 1;
  max-width: 80px;
}

.nav-item:hover {
  background: #f3f4f5;
}

.nav-label {
  font-size: 10px;
  font-weight: 500;
  margin-top: 2px;
  text-align: center;
  line-height: 1.2;
}

.nav-item-active {
  background: #c2410c !important;
  color: #ffffff !important;
  padding: 6px 8px;
}

.nav-item-active:hover {
  background: #c2410c !important;
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

.dark-theme .brand-title {
  color: #e0e0e0;
}

.dark-theme .icon-btn {
  color: #a0a0b0;
}

.dark-theme .filter-bar {
  background: #0f0f1a;
}

.dark-theme .filter-tab {
  background: #1a1a2e;
  color: #a0a0b0;
}

.dark-theme .filter-tab.active {
  background: #2a1a0a;
  border-color: #c2410c;
  color: #ff8a65;
}

.dark-theme .filter-tab:hover:not(.active) {
  background: #16213e;
}

.dark-theme .user-card {
  background: #1a1a2e;
}

.dark-theme .user-name {
  color: #e0e0e0;
}

.dark-theme .rank-number {
  color: #a0a0b0;
}

.dark-theme .nav-item:hover {
  background: #16213e;
}

.dark-theme .bottom-nav {
  background: rgba(26, 26, 46, 0.9);
}

.dark-theme .nav-item {
  color: #a0a0b0;
}

.dark-theme .stat-value {
  color: #a0a0b0;
}

.dark-theme .stat-value.high {
  color: #ff8a65;
}
</style>
