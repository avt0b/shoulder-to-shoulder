<template>
  <div class="profile-page">
    <!-- Top Navigation Bar -->
    <header class="top-nav">
      <div class="top-nav-left">
        <div class="avatar-small">
          <img :src="profile.avatar_url || defaultAvatar" alt="Аватар" />
        </div>
        <h1 class="brand-title">{{ profile.display_name || 'Имя Фамилия' }}</h1>
      </div>
      <div class="top-nav-right">
        <button class="icon-btn" aria-label="Настройки" @click="showSettings = true">
          <span class="material-symbols">settings</span>
        </button>
      </div>
    </header>

    <main class="main-content">
      <!-- Bento Grid -->
      <div class="bento-grid">
        <!-- Profile Hero Card -->
        <div class="card profile-hero">
          <div class="avatar-large" @click="!profile.avatar_url && triggerFileInput()">
            <img :src="profile.avatar_url || defaultAvatar" alt="Аватар" />
            <div v-if="!profile.avatar_url" class="avatar-overlay">
              <span class="material-symbols">add_a_photo</span>
            </div>
            <div class="role-badge" v-if="profile.role === 'moderator' || profile.role === 'superuser'">
              PRO
            </div>
          </div>
          <div class="profile-info">
            <h2 class="display-name">{{ profile.display_name || 'Имя Фамилия' }}</h2>
            <div class="profile-meta">
              <span class="meta-item" :class="{ clickable: !profile.age }" @click="!profile.age && editProfile('age')">
                <span class="material-symbols meta-icon">cake</span>
                {{ profile.age ? profile.age + ' лет' : 'Добавить' }}
              </span>
              <span class="meta-item" :class="{ clickable: !profile.city }" @click="!profile.city && editProfile('city')">
                <span class="material-symbols meta-icon">location_on</span>
                {{ profile.city || 'Добавить' }}
              </span>
            </div>
            <span v-if="!profile.bio" class="meta-item bio-add clickable" @click="editProfile('bio')">
              <span class="material-symbols meta-icon">edit_note</span>
              Добавить
            </span>
            <p v-else class="profile-bio">{{ profile.bio }}</p>
          </div>
        </div>

        <!-- Reliability Card -->
        <div class="card reliability-card">
          <div class="rating-header">
            <span class="material-symbols rating-icon" :data-filled="true">verified_user</span>
            <div class="rating-info">
              <span class="rating-label">Надёжность</span>
              <span class="rating-value">{{ ratings.reliability_score.toFixed(1) }}%</span>
            </div>
          </div>
          <div class="progress-bar">
            <div class="progress-fill reliability-fill" :style="{ width: ratings.reliability_score + '%' }"></div>
          </div>
          <div class="rating-detail">
            <span>Завершено: {{ ratings.completed_events }}</span>
            <span>Всего: {{ ratings.total_events }}</span>
          </div>
        </div>

        <!-- Empathy Card -->
        <div class="card empathy-card">
          <div class="rating-header">
            <span class="material-symbols rating-icon" :data-filled="true">favorite</span>
            <div class="rating-info">
              <span class="rating-label">Эмпатия</span>
              <span class="rating-value">{{ ratings.empathy_score }}</span>
            </div>
          </div>
          <div class="progress-bar">
            <div class="progress-fill empathy-fill" :style="{ width: Math.min(ratings.empathy_score, 100) + '%' }"></div>
          </div>
          <div class="rating-detail rating-detail-center">
            <span>Баллов поддержки</span>
          </div>
        </div>

        <!-- Achievements -->
        <div class="card achievements-card">
          <h3 class="section-title">Достижения</h3>
          <div v-if="badges.length > 0" class="badges-grid">
            <div v-for="badge in badges" :key="badge.id" class="badge-card" :class="`badge-${badge.badge_type}`">
              <div class="badge-icon-wrap">
                <span class="material-symbols badge-icon" :data-filled="true">{{ getBadgeIcon(badge.badge_type) }}</span>
              </div>
              <span class="badge-label">{{ getBadgeLabel(badge.badge_type) }}</span>
            </div>
          </div>
          <div v-else class="badges-empty">
            <span class="material-symbols badges-empty-icon">military_tech</span>
            <p>Пока нет достижений. Начните тренироваться, чтобы получить первые награды!</p>
          </div>
        </div>
      </div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/map" class="nav-item">
        <span class="material-symbols">map</span>
        <span class="nav-label">Map</span>
      </router-link>
      <router-link to="/groups" class="nav-item">
        <span class="material-symbols">group</span>
        <span class="nav-label">Groups</span>
      </router-link>
      <router-link to="/routes" class="nav-item">
        <span class="material-symbols">directions_run</span>
        <span class="nav-label">Routes</span>
      </router-link>
      <router-link to="/profile" class="nav-item nav-item-active">
        <span class="material-symbols" :data-filled="true">person</span>
        <span class="nav-label">Profile</span>
      </router-link>
    </nav>

    <!-- Edit Modal -->
    <div v-if="editModal.show" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <button class="modal-close" @click="closeEditModal">
          <span class="material-symbols">close</span>
        </button>
        <h3 class="modal-title">{{ modalTitle }}</h3>
        <div class="modal-body">
          <!-- Display Name Input -->
          <div v-if="editModal.field === 'display_name'" class="form-field">
            <label class="form-label">Имя</label>
            <input
              v-model="editModal.value"
              type="text"
              placeholder="Введите ваше имя"
              class="form-input"
              maxlength="50"
            />
            <p v-if="editModal.error" class="error-text">{{ editModal.error }}</p>
          </div>
          <!-- Age Input -->
          <div v-if="editModal.field === 'age'" class="form-field">
            <label class="form-label">Возраст</label>
            <input
              v-model.number="editModal.value"
              type="number"
              min="18"
              max="120"
              placeholder="Введите возраст"
              class="form-input"
            />
            <p v-if="editModal.error" class="error-text">{{ editModal.error }}</p>
          </div>
          <!-- City Input -->
          <div v-if="editModal.field === 'city'" class="form-field">
            <label class="form-label">Город</label>
            <select
              v-model="editModal.value"
              class="form-input form-select"
            >
              <option value="" disabled>Выберите город</option>
              <option v-for="city in russianCities" :key="city" :value="city">{{ city }}</option>
            </select>
            <p v-if="editModal.error" class="error-text">{{ editModal.error }}</p>
          </div>
          <!-- Bio Input -->
          <div v-if="editModal.field === 'bio'" class="form-field">
            <label class="form-label">О себе</label>
            <textarea
              v-model="editModal.value"
              class="form-input form-textarea"
              placeholder="Расскажите о себе"
              maxlength="255"
              rows="4"
            ></textarea>
            <p class="char-count">{{ (editModal.value || '').length }}/255</p>
          </div>
        </div>
        <div class="modal-actions">
          <button class="modal-btn modal-btn-cancel" @click="backFromEdit">
            Назад
          </button>
          <button class="modal-btn modal-btn-save" @click="saveEdit" :disabled="saving">
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Hidden file input for avatar -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileSelect"
    />

    <!-- Settings Modal -->
    <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
      <div class="modal settings-modal">
        <button class="modal-close" @click="showSettings = false">
          <span class="material-symbols">close</span>
        </button>
        <h3 class="modal-title">Настройки</h3>
        <div class="settings-list">
          <button class="settings-item" @click="openEditProfile">
            <span class="material-symbols settings-icon">person_edit</span>
            <span class="settings-label">Редактировать профиль</span>
          </button>
          <button class="settings-item" @click="showAbout = true; showSettings = false">
            <span class="material-symbols settings-icon">info</span>
            <span class="settings-label">О программе</span>
          </button>
          <button class="settings-item" @click="showPrivacy = true; showSettings = false">
            <span class="material-symbols settings-icon">policy</span>
            <span class="settings-label">Политика безопасности</span>
          </button>
          <div class="settings-divider"></div>
          <button class="settings-item" @click="toggleTheme">
            <span class="material-symbols settings-icon">{{ isDark ? 'light_mode' : 'dark_mode' }}</span>
            <span class="settings-label">{{ isDark ? 'Светлая тема' : 'Тёмная тема' }}</span>
          </button>
        </div>
        <div class="modal-actions">
          <button class="modal-btn modal-btn-back" @click="showSettings = false">Назад</button>
        </div>
      </div>
    </div>

    <!-- About Modal -->
    <div v-if="showAbout" class="modal-overlay" @click.self="showAbout = false">
      <div class="modal info-modal">
        <button class="modal-close" @click="showAbout = false">
          <span class="material-symbols">close</span>
        </button>
        <h3 class="modal-title">О программе</h3>
        <div class="info-content">
          <p class="app-name"><strong>Плечом к плечу</strong></p>
          <p class="app-version">Версия 1.0.0</p>
          <div class="info-divider"></div>
          <p class="app-desc">Приложение для сообщества уличных тренировок. Объединяй людей, создавай тренировки, зарабатывай репутацию и достижения.</p>
          <div class="info-divider"></div>
          <p class="app-tech">Backend: FastAPI, PostgreSQL, NATS</p>
          <p class="app-tech">Frontend: Vue 3, Vite</p>
        </div>
        <div class="modal-actions">
          <button class="modal-btn modal-btn-back" @click="showAbout = false; showSettings = true">Назад</button>
        </div>
      </div>
    </div>

    <!-- Privacy Policy Modal -->
    <div v-if="showPrivacy" class="modal-overlay" @click.self="showPrivacy = false">
      <div class="modal info-modal">
        <button class="modal-close" @click="showPrivacy = false">
          <span class="material-symbols">close</span>
        </button>
        <h3 class="modal-title">Политика безопасности</h3>
        <div class="info-content privacy-content">
          <p class="info-section-title">Сбор и использование данных</p>
          <p>Мы собираем только необходимую информацию для работы приложения: номер телефона, email и профиль пользователя. Ваши персональные данные не передаются третьим лицам.</p>
          <p class="info-section-title">Безопасность</p>
          <p>Пароли хранятся в хешированном виде. Доступ к данным защищён JWT-токенами с ограниченным сроком действия. Подключение к базе данных осуществляется через защищённый протокол.</p>
          <p class="info-section-title">Права пользователя</p>
          <p>Вы можете запросить удаление вашего аккаунта и всех связанных данных в любое время, обратившись в поддержку.</p>
        </div>
        <div class="modal-actions">
          <button class="modal-btn modal-btn-back" @click="showPrivacy = false; showSettings = true">Назад</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../api/index';
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

const badges = ref([]);

const fileInput = ref(null);
const showSettings = ref(false);
const showAbout = ref(false);
const showPrivacy = ref(false);
const isDark = ref(false);

// Load theme from localStorage
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') isDark.value = true;

// Apply theme
const applyTheme = () => {
  document.documentElement.classList.toggle('dark-theme', isDark.value);
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
};
applyTheme();

const toggleTheme = () => {
  isDark.value = !isDark.value;
  applyTheme();
};

const openEditProfile = () => {
  showSettings.value = false;
  editProfile('display_name', true);
};

const backFromEdit = () => {
  const fromSettings = editModal.value.fromSettings;
  closeEditModal();
  if (fromSettings) {
    showSettings.value = true;
  }
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;

  // Validate file type
  if (!file.type.startsWith('image/')) {
    uploadError.value = 'Выберите изображение';
    return;
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    uploadError.value = 'Файл слишком большой (макс. 5МБ)';
    return;
  }

  try {
    // Convert to base64/data URL for preview
    const reader = new FileReader();
    reader.onload = (e) => {
      profile.value.avatar_url = e.target.result;
    };
    reader.readAsDataURL(file);
  } catch (e) {
    console.error('Failed to upload avatar:', e.message);
    uploadError.value = 'Ошибка загрузки. Попробуйте снова.';
  }

  // Reset input
  event.target.value = '';
};

const editModal = ref({
  show: false,
  field: '',
  value: '',
  error: '',
  fromSettings: false,
});
const saving = ref(false);

const russianCities = [
  'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
  'Нижний Новгород', 'Челябинск', 'Красноярск', 'Самара', 'Уфа',
  'Ростов-на-Дону', 'Омск', 'Краснодар', 'Воронеж', 'Пермь',
  'Волгоград', 'Саратов', 'Тюмень', 'Тольятти', 'Ижевск',
  'Барнаул', 'Иркутск', 'Хабаровск', 'Ярославль', 'Владивосток',
  'Махачкала', 'Томск', 'Оренбург', 'Кемерово', 'Новокузнецк',
  'Рязань', 'Астрахань', 'Набережные Челны', 'Калининград', 'Пенза',
  'Липецк', 'Киров', 'Чебоксары', 'Тула', 'Смоленск',
  'Брянск', 'Владимир', 'Белгород', 'Сургут', 'Курган',
  'Орёл', 'Мурманск', 'Якутск', 'Тверь', 'Сочи',
  'Ставрополь', 'Подольск', 'Сыктывкар', 'Нальчик', 'Петрозаводск',
  'Грозный', 'Курск', 'Улан-Удэ', 'Чита', 'Архангельск',
  'Новороссийск', 'Йошкар-Ола', 'Саранск', 'Калуга', 'Псков',
  'Кострома', 'Вологда', 'Великий Новгород', 'Южно-Сахалинск', 'Благовещенск',
  'Комсомольск-на-Амуре', 'Петропавловск-Камчатский', 'Магадан', 'Анадырь',
];

const modalTitles = {
  display_name: 'Имя',
  age: 'Возраст',
  city: 'Город',
  bio: 'О себе',
};

const modalTitle = computed(() => modalTitles[editModal.value.field] || '');

const editProfile = (field, fromSettings = false) => {
  let currentValue = '';
  if (field === 'age') currentValue = profile.value.age ?? '';
  else if (field === 'city') currentValue = profile.value.city || '';
  else if (field === 'bio') currentValue = profile.value.bio ?? '';
  else if (field === 'display_name') currentValue = profile.value.display_name || '';

  editModal.value = {
    show: true,
    field,
    value: currentValue,
    error: '',
    fromSettings,
  };
};

const closeEditModal = () => {
  editModal.value = { show: false, field: '', value: '', error: '', fromSettings: false };
};

const saveEdit = async () => {
  editModal.value.error = '';
  const { field, value } = editModal.value;

  // Validation
  if (field === 'age') {
    if (!value || value < 18 || value > 120) {
      editModal.value.error = 'Возраст должен быть от 18 до 120';
      return;
    }
  }
  if (field === 'bio' && value && value.trim().length > 255) {
    editModal.value.error = 'Описание не должно превышать 255 символов';
    return;
  }

  saving.value = true;
  try {
    const updateData = {};
    if (field === 'display_name') updateData.display_name = value.trim();
    if (field === 'age') updateData.age = parseInt(value);
    else if (field === 'city') {
      const prefs = { ...profile.value.preferences, city: value };
      updateData.preferences = prefs;
    }
    else if (field === 'bio') updateData.bio = value || '';

    await authApi.updateProfile(updateData);

    // Update local state
    if (field === 'display_name') profile.value.display_name = value.trim() || null;
    if (field === 'age') profile.value.age = parseInt(value);
    else if (field === 'city') {
      profile.value.city = value;
      profile.value.preferences = { ...profile.value.preferences, city: value };
    }
    else if (field === 'bio') profile.value.bio = value || null;

    closeEditModal();
  } catch (e) {
    console.error('Failed to save:', e.message);
    editModal.value.error = 'Ошибка сохранения. Попробуйте снова.';
  } finally {
    saving.value = false;
  }
};

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

const loadProfile = async () => {
  try {
    const data = await authApi.getProfile();
    const payload = decodeToken();
    profile.value = {
      user_id: data.user_id,
      display_name: data.display_name,
      login: data.phone_number,
      age: data.age,
      fitness_level: data.fitness_level || 'beginner',
      bio: data.bio ?? null,
      avatar_url: data.avatar_url || '',
      role: payload?.role || 'user',
      city: data.preferences?.city || '',
      preferences: data.preferences || {},
    };
  } catch (e) {
    console.error('Failed to load profile:', e.message);
  }
};

const loadRating = async () => {
  try {
    const data = await authApi.getRating();
    ratings.value = {
      empathy_score: data.empathy_score,
      reliability_score: data.reliability_score,
      total_events: data.total_events,
      completed_events: data.completed_events,
    };
  } catch (e) {
    console.error('Failed to load rating:', e.message);
  }
};

const loadBadges = async () => {
  if (!profile.value.user_id) return;
  try {
    const data = await authApi.getPublicProfile(profile.value.user_id);
    badges.value = data.badges.map((type, index) => ({
      id: index + 1,
      badge_type: type,
    }));
  } catch (e) {
    console.error('Failed to load badges:', e.message);
  }
};

onMounted(async () => {
  await loadProfile();
  await Promise.all([loadRating(), loadBadges()]);
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

/* ===== Reliability & Empathy Cards ===== */
.reliability-card,
.empathy-card {
  grid-column: 1 / -1;
}

@media (min-width: 480px) {
  .reliability-card,
  .empathy-card {
    grid-column: span 2;
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

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.avatar-overlay:hover {
  background: rgba(0, 0, 0, 0.6);
}

.avatar-overlay .material-symbols {
  color: #ffffff;
  font-size: 28px;
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
  margin: 0 0 12px;
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
  margin-bottom: 12px;
}

@media (min-width: 768px) {
  .profile-meta {
    justify-content: flex-start;
  }
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #59413a;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 8px;
}

.meta-item.clickable {
  cursor: pointer;
  transition: background 0.15s;
}

.meta-item.clickable:hover {
  background: #e7e8e9;
}

.meta-icon {
  font-size: 18px;
  color: #9ca3af;
}

.profile-bio {
  font-size: 14px;
  line-height: 1.6;
  color: #191c1d;
  margin: 0;
  padding: 12px 16px;
  background: #f3f4f5;
  border-radius: 12px;
  word-break: break-word;
  overflow-wrap: anywhere;
  width: 100%;
  box-sizing: border-box;
  max-width: 100%;
}

.bio-add {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #9ca3af;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.15s;
  justify-content: center;
  width: 100%;
}

.bio-add:hover {
  background: #e7e8e9;
}

/* ===== Rating Cards ===== */
.rating-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.rating-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.reliability-card .rating-icon {
  color: #c2410c;
}

.empathy-card .rating-icon {
  color: #0069de;
}

.rating-info {
  display: flex;
  flex-direction: column;
}

.rating-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #9ca3af;
}

.rating-value {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.reliability-card .rating-value {
  color: #c2410c;
}

.empathy-card .rating-value {
  color: #0069de;
}

.progress-bar {
  height: 8px;
  background: #f3f4f5;
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.6s ease;
}

.reliability-fill {
  background: linear-gradient(90deg, #c2410c, #9b2f00);
}

.empathy-fill {
  background: linear-gradient(90deg, #0069de, #0047a1);
}

.rating-detail {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
}

.rating-detail-center {
  justify-content: center;
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
  margin: 0 0 16px;
}

.badges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 16px;
}

.badge-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.badge-card:hover {
  transform: translateY(-2px);
}

.badge-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-icon {
  font-size: 28px;
}

.badge-label {
  font-size: 12px;
  font-weight: 600;
  text-align: center;
}

/* === Leader Badge === */
.badge-leader {
  background: linear-gradient(135deg, #fff3e8, #ffe4cc);
}

.badge-leader .badge-icon-wrap {
  background: linear-gradient(135deg, #ffb59d, #c2410c);
  box-shadow: 0 4px 12px rgba(194, 65, 12, 0.35);
}

.badge-leader .badge-icon {
  color: #ffffff;
}

.badge-leader .badge-label {
  color: #832600;
}

/* === Sprinter Badge === */
.badge-sprinter {
  background: linear-gradient(135deg, #e8f0ff, #cce0ff);
}

.badge-sprinter .badge-icon-wrap {
  background: linear-gradient(135deg, #4d94ff, #0051af);
  box-shadow: 0 4px 12px rgba(0, 81, 175, 0.35);
}

.badge-sprinter .badge-icon {
  color: #ffffff;
}

.badge-sprinter .badge-label {
  color: #001a41;
}

/* === Supporter Badge === */
.badge-supporter {
  background: linear-gradient(135deg, #e8ffe8, #ccf5cc);
}

.badge-supporter .badge-icon-wrap {
  background: linear-gradient(135deg, #4caf50, #1b5e20);
  box-shadow: 0 4px 12px rgba(27, 94, 32, 0.35);
}

.badge-supporter .badge-icon {
  color: #ffffff;
}

.badge-supporter .badge-label {
  color: #0d3b0f;
}

/* === Curator Badge === */
.badge-curator {
  background: linear-gradient(135deg, #f3e8ff, #e4ccff);
}

.badge-curator .badge-icon-wrap {
  background: linear-gradient(135deg, #ab47bc, #6a1b9a);
  box-shadow: 0 4px 12px rgba(106, 27, 154, 0.35);
}

.badge-curator .badge-icon {
  color: #ffffff;
}

.badge-curator .badge-label {
  color: #4a148c;
}

/* === Explorer Badge === */
.badge-explorer {
  background: linear-gradient(135deg, #fff8e1, #ffecb3);
}

.badge-explorer .badge-icon-wrap {
  background: linear-gradient(135deg, #ffa726, #e65100);
  box-shadow: 0 4px 12px rgba(230, 81, 0, 0.35);
}

.badge-explorer .badge-icon {
  color: #ffffff;
}

.badge-explorer .badge-label {
  color: #bf360c;
}

/* === Empty Badges === */
.badges-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 16px;
  text-align: center;
}

.badges-empty-icon {
  font-size: 48px;
  color: #d1d5d8;
}

.badges-empty p {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
  line-height: 1.5;
}

/* ===== Modal ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  background: #ffffff;
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 20px;
  text-align: center;
}

.form-field {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #59413a;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  background: #f3f4f5;
  border: 2px solid transparent;
  border-radius: 12px;
  font-size: 14px;
  color: #191c1d;
  outline: none;
  font-family: 'Inter', sans-serif;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #c2410c;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  word-break: break-word;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.form-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2359413a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.char-count {
  font-size: 11px;
  color: #9ca3af;
  text-align: right;
  margin: 4px 0 0;
}

.error-text {
  font-size: 12px;
  color: #ba1a1a;
  margin: 4px 0 0;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.modal-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: transform 0.15s, opacity 0.15s;
  min-height: 44px;
}

.modal-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.modal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-btn-back {
  background: #e7e8e9;
  color: #59413a;
}

.modal-btn-back:hover:not(:disabled) {
  opacity: 0.85;
}

/* ===== Modal Close Button ===== */
.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  padding: 4px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
}

.modal-close:hover {
  background: #f3f4f5;
  color: #191c1d;
}

.modal-close .material-symbols {
  font-size: 24px;
}

.modal {
  position: relative;
  background: #ffffff;
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-btn-save {
  background: linear-gradient(135deg, #c2410c, #9b2f00);
  color: #ffffff;
}

.modal-btn-save:hover:not(:disabled) {
  opacity: 0.9;
}

/* ===== Settings ===== */
.settings-modal {
  padding: 24px;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.settings-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: none;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.15s;
  text-align: left;
  width: 100%;
}

.settings-item:hover {
  background: #f3f4f5;
}

.settings-icon {
  font-size: 24px;
  color: #59413a;
}

.settings-label {
  font-size: 15px;
  font-weight: 500;
  color: #191c1d;
}

.settings-divider {
  height: 1px;
  background: #e7e8e9;
  margin: 8px 0;
}

/* ===== Info Modals ===== */
.info-modal {
  max-width: 440px;
}

.info-content {
  text-align: center;
}

.app-name {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 4px;
  color: #191c1d;
}

.app-version {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}

.info-divider {
  height: 1px;
  background: #e7e8e9;
  margin: 16px 0;
}

.app-desc {
  font-size: 14px;
  line-height: 1.6;
  color: #59413a;
  margin: 0 0 12px;
}

.app-tech {
  font-size: 13px;
  color: #9ca3af;
  margin: 4px 0;
}

.privacy-content {
  text-align: left;
}

.info-section-title {
  font-size: 15px;
  font-weight: 700;
  color: #191c1d;
  margin: 16px 0 8px !important;
}

.privacy-content p {
  font-size: 14px;
  line-height: 1.6;
  color: #59413a;
  margin: 0 0 8px;
}

/* ===== Dark Theme ===== */
.dark-theme {
  --bg-primary: #1a1a2e;
  --bg-secondary: #16213e;
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0b0;
}

.dark-theme .profile-page {
  background: #0f0f1a;
  color: #e0e0e0;
}

.dark-theme .top-nav {
  background: #0f0f1a;
}

.dark-theme .card {
  background: #1a1a2e;
}

.dark-theme .bottom-nav {
  background: rgba(26, 26, 46, 0.9);
}

.dark-theme .display-name {
  color: #e0e0e0;
}

.dark-theme .profile-meta .meta-item {
  color: #a0a0b0;
}

.dark-theme .profile-bio {
  background: #16213e;
  color: #e0e0e0;
}

.dark-theme .modal {
  background: #1a1a2e;
}

.dark-theme .modal-title {
  color: #e0e0e0;
}

.dark-theme .form-input {
  background: #16213e;
  color: #e0e0e0;
}

.dark-theme .form-label {
  color: #a0a0b0;
}

.dark-theme .settings-item:hover {
  background: #16213e;
}

.dark-theme .settings-label {
  color: #e0e0e0;
}

.dark-theme .settings-icon {
  color: #a0a0b0;
}

.dark-theme .settings-divider {
  background: #2a2a3e;
}

.dark-theme .info-divider {
  background: #2a2a3e;
}

.dark-theme .brand-title {
  color: #e0e0e0;
}

.dark-theme .icon-btn {
  color: #a0a0b0;
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
  text-decoration: none;
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
