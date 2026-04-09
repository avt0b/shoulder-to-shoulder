<template>
  <div class="profile-page">
    <!-- Top Navigation Bar -->
    <header class="top-nav">
      <div class="top-nav-left">
        <div class="avatar-small">
          <img :src="profile.avatar_url || defaultAvatar" alt="Аватар" />
        </div>
        <h1 class="brand-title">{{ profile.login }}</h1>
      </div>
      <div class="top-nav-right">
        <button class="icon-btn" aria-label="Настройки">
          <span class="material-symbols">settings</span>
        </button>
      </div>
    </header>

    <main class="main-content">
      <!-- Bento Grid -->
      <div class="bento-grid">
        <!-- Profile Hero Card -->
        <div class="card profile-hero">
          <div class="avatar-large">
            <img :src="profile.avatar_url || defaultAvatar" alt="Аватар" />
            <div class="role-badge" v-if="profile.role === 'moderator' || profile.role === 'superuser'">
              PRO
            </div>
          </div>
          <div class="profile-info">
            <h2 class="display-name">{{ profile.display_name }}</h2>
            <p class="profile-subtitle">{{ profile.bio || 'Участник сообщества' }} • {{ profile.city || 'Россия' }}</p>
            <div class="chips">
              <div class="chip chip-reliability">
                <span class="material-symbols chip-icon" :data-filled="true">verified_user</span>
                <span>Надёжность {{ ratings.reliability_score }}%</span>
              </div>
              <div class="chip chip-empathy">
                <span class="material-symbols chip-icon" :data-filled="true">favorite</span>
                <span>Эмпатия {{ ratings.empathy_score }}</span>
              </div>
            </div>
          </div>
          <button class="btn-edit" @click="editProfile">Редактировать</button>
        </div>

        <!-- Stat: Тренировок -->
        <div class="card workouts-card">
          <span class="material-symbols stat-icon" :data-filled="true">exercise</span>
          <div class="stat-value">{{ stats.workouts }}</div>
          <div class="stat-label">{{ workoutsLabel(stats.workouts) }}</div>
        </div>

        <!-- Stat: Созданных тренировок -->
        <div class="card meetups-card">
          <span class="material-symbols stat-icon" :data-filled="true">group</span>
          <div class="stat-value">{{ stats.meetups }}</div>
          <div class="stat-label">{{ createdLabel(stats.meetups) }}</div>
        </div>

        <!-- Achievements -->
        <div class="card achievements-card">
          <h3 class="section-title">Достижения</h3>
          <div class="badges-list">
            <div v-for="badge in badges" :key="badge.id" class="badge-row">
              <div class="badge-icon" :class="`badge-${badge.badge_type}`">
                <span class="material-symbols" :data-filled="true">{{ getBadgeIcon(badge.badge_type) }}</span>
              </div>
              <span class="badge-name">{{ getBadgeLabel(badge.badge_type) }}</span>
            </div>
            <div v-if="badges.length < 3" class="badge-row locked">
              <div class="badge-icon badge-locked">
                <span class="material-symbols">lock</span>
              </div>
              <span class="badge-name">Опора</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <button class="nav-item">
        <span class="material-symbols">map</span>
        <span class="nav-label">Map</span>
      </button>
      <button class="nav-item">
        <span class="material-symbols">group</span>
        <span class="nav-label">Groups</span>
      </button>
      <button class="nav-item">
        <span class="material-symbols">directions_run</span>
        <span class="nav-label">Routes</span>
      </button>
      <button class="nav-item nav-item-active">
        <span class="material-symbols" :data-filled="true">person</span>
        <span class="nav-label">Profile</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import defaultAvatar from '../assets/default-avatar.svg';

const router = useRouter();

const profile = ref({
  display_name: '',
  login: '',
  age: null,
  fitness_level: 'beginner',
  bio: '',
  avatar_url: '',
  role: 'user',
  city: '',
});

const ratings = ref({
  empathy_score: 0,
  reliability_score: 100,
  total_events: 0,
  completed_events: 0,
});

const stats = ref({
  workouts: 0,
  meetups: 0,
});

const badges = ref([]);

const pluralize = (n, one, few, many) => {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod100 >= 11 && mod100 <= 19) return many;
  if (mod10 === 1) return one;
  if (mod10 >= 2 && mod10 <= 4) return few;
  return many;
};

const workoutsLabel = (n) => pluralize(n, 'Тренировка', 'Тренировки', 'Тренировок');
const createdLabel = (n) => pluralize(n, 'Созданная тренировка', 'Созданные тренировки', 'Созданных тренировок');

const badgeIcons = {
  leader: 'military_tech',
  sprinter: 'bolt',
  supporter: 'handshake',
  curator: 'shield_person',
  explorer: 'explore',
};

const badgeLabels = {
  leader: 'Лидер',
  sprinter: 'Спринтер',
  supporter: 'Опора',
  curator: 'Куратор',
  explorer: 'Исследователь',
};

const getBadgeIcon = (type) => badgeIcons[type] || 'star';
const getBadgeLabel = (type) => badgeLabels[type] || type;

const editProfile = () => {
  // TODO: navigate to edit profile
};

onMounted(async () => {
  // TODO: replace with real API calls
  // For now, load mock data
  profile.value = {
    display_name: 'Александр Волков',
    login: 'alexrunner',
    age: 28,
    fitness_level: 'advanced',
    bio: 'Бегун-энтузиаст и проводник',
    avatar_url: '',
    role: 'user',
    city: 'Москва',
  };

  ratings.value = {
    empathy_score: 12,
    reliability_score: 94,
    total_events: 142,
    completed_events: 138,
  };

  stats.value = {
    workouts: 142,
    meetups: 24,
  };

  badges.value = [
    { id: 1, badge_type: 'leader', awarded_at: '2025-01-15' },
    { id: 2, badge_type: 'sprinter', awarded_at: '2025-03-20' },
  ];
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.profile-page {
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

/* ===== Main ===== */
.main-content {
  max-width: 768px;
  margin: 0 auto;
  padding: 0 16px 32px;
}

/* ===== Bento Grid ===== */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

/* ===== Card Base ===== */
.card {
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
}

/* ===== Profile Hero ===== */
.profile-hero {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

@media (min-width: 768px) {
  .profile-hero {
    flex-direction: row;
  }
}

.avatar-large {
  position: relative;
  width: 96px;
  height: 96px;
}

@media (min-width: 768px) {
  .avatar-large {
    width: 128px;
    height: 128px;
  }
}

.avatar-large img {
  width: 100%;
  height: 100%;
  border-radius: 9999px;
  object-fit: cover;
  border: 4px solid #c2410c;
  padding: 4px;
  background: #ffffff;
}

.role-badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: #9b2f00;
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 9999px;
  border: 2px solid #ffffff;
}

.profile-info {
  flex: 1;
  text-align: center;
}

@media (min-width: 768px) {
  .profile-info {
    text-align: left;
  }
}

.display-name {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
}

.profile-subtitle {
  font-size: 14px;
  color: #59413a;
  margin: 0 0 16px;
}

.chips {
  display: flex;
  flex-wrap: nowrap;
  gap: 12px;
  justify-content: center;
}

@media (min-width: 768px) {
  .chips {
    justify-content: flex-start;
  }
}

.chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
}

.chip-reliability {
  background: #ffece7;
  color: #832600;
}

.chip-empathy {
  background: #d8e2ff;
  color: #001a41;
}

.chip-icon {
  font-size: 18px;
}

.btn-edit {
  background: #e7e8e9;
  color: #59413a;
  border: none;
  border-radius: 9999px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s;
  font-family: 'Inter', sans-serif;
  min-height: 44px;
}

.btn-edit:active {
  transform: scale(0.98);
}

/* ===== Stats ===== */
.stat-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ===== Workouts & Meetups Cards ===== */
.workouts-card,
.meetups-card {
  grid-column: span 2;
  background: #c2410c;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.meetups-card {
  background: #0069de;
}

.stat-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.workouts-card .stat-label,
.meetups-card .stat-label {
  color: rgba(255, 255, 255, 0.8);
}

/* ===== Achievements ===== */
.achievements-card {
  grid-column: 1 / -1;
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #9ca3af;
  margin: 0 0 12px;
}

.badges-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.badge-row.locked {
  opacity: 0.4;
}

.badge-icon {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.badge-leader {
  background: linear-gradient(135deg, #ffb59d, #c2410c);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(194, 65, 12, 0.3);
}

.badge-sprinter {
  background: linear-gradient(135deg, #d8e2ff, #0051af);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 81, 175, 0.3);
}

.badge-locked {
  background: #e1e3e4;
  border: 2px dashed #d1d5d8;
  color: #9ca3af;
}

.badge-name {
  font-size: 14px;
  font-weight: 600;
  color: #191c1d;
}

/* ===== Bottom Nav ===== */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 12px 24px max(24px, env(safe-area-inset-bottom));
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
  padding: 8px;
  border-radius: 9999px;
  cursor: pointer;
  transition: background 0.15s;
  min-width: 56px;
}

.nav-item:hover {
  background: #f3f4f5;
}

.nav-label {
  font-size: 11px;
  font-weight: 500;
  margin-top: 2px;
}

.nav-item-active {
  background: #c2410c !important;
  color: #ffffff !important;
  padding: 6px 20px;
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

.text-primary {
  color: #9b2f00;
}
</style>
