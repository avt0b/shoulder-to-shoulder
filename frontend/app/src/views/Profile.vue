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
              <span class="meta-item" :class="{ clickable: !profile.fitness_level }" @click="!profile.fitness_level && editProfile('fitness_level')">
                <span class="material-symbols meta-icon">fitness_center</span>
                {{ profile.fitness_level ? getFitnessLevelLabel(profile.fitness_level) : 'Добавить' }}
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
      <router-link to="/" class="nav-item">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/'">map</span>
        <span>Карта</span>
      </router-link>
      <router-link to="/events" class="nav-item">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/events'">event</span>
        <span>Ивенты</span>
      </router-link>
      <router-link to="/map" class="nav-item">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/map'">directions_run</span>
        <span>Маршруты</span>
      </router-link>
      <router-link to="/profile" class="nav-item nav-item-active">
        <span class="material-symbols-outlined" data-filled="true">person</span>
        <span>Профиль</span>
      </router-link>
      <router-link to="/rating" class="nav-item">
        <span class="material-symbols-outlined" :data-filled="$route.path === '/rating'">emoji_events</span>
        <span>Рейтинг</span>
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
          <!-- Fitness Level Select -->
          <div v-if="editModal.field === 'fitness_level'" class="form-field">
            <label class="form-label">Уровень подготовки</label>
            <select
              v-model="editModal.value"
              class="form-input form-select"
            >
              <option value="" disabled>Выберите уровень</option>
              <option value="beginner">Начинающий</option>
              <option value="intermediate">Средний</option>
              <option value="advanced">Продвинутый</option>
            </select>
            <p v-if="editModal.error" class="error-text">{{ editModal.error }}</p>
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

    <!-- Full Profile Edit Modal -->
    <div v-if="showEditProfile" class="modal-overlay" @click.self="closeEditProfileModal">
      <div class="modal edit-profile-modal">
        <button class="modal-close" @click="closeEditProfileModal">
          <span class="material-symbols">close</span>
        </button>
        <h3 class="modal-title">Редактировать профиль</h3>
        <div class="modal-body modal-body-scrollable">
          <!-- Avatar Upload -->
          <div class="form-field avatar-upload-field">
            <label class="form-label">Фото профиля</label>
            <div class="avatar-preview-wrap">
              <div class="avatar-preview">
                <img :src="editModal.avatar_url || defaultAvatar" alt="Аватар" />
              </div>
              <button type="button" class="avatar-change-btn" @click="triggerEditAvatarInput">
                <span class="material-symbols">photo_camera</span>
                <span>Изменить фото</span>
              </button>
            </div>
            <input
              ref="editAvatarFileInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleEditAvatarSelect"
            />
            <p v-if="editModal.error_avatar" class="error-text">{{ editModal.error_avatar }}</p>
          </div>
          <!-- Display Name Input -->
          <div class="form-field">
            <label class="form-label">Имя</label>
            <input
              v-model="editModal.display_name"
              type="text"
              placeholder="Введите ваше имя"
              class="form-input"
              maxlength="50"
            />
            <p v-if="editModal.error_name" class="error-text">{{ editModal.error_name }}</p>
          </div>
          <!-- Age Input -->
          <div class="form-field">
            <label class="form-label">Возраст</label>
            <input
              v-model.number="editModal.age"
              type="number"
              min="18"
              max="120"
              placeholder="Введите возраст"
              class="form-input"
            />
            <p v-if="editModal.error_age" class="error-text">{{ editModal.error_age }}</p>
          </div>
          <!-- City Input -->
          <div class="form-field">
            <label class="form-label">Город</label>
            <select
              v-model="editModal.city"
              class="form-input form-select"
            >
              <option value="" disabled>Выберите город</option>
              <option v-for="city in russianCities" :key="city" :value="city">{{ city }}</option>
            </select>
            <p v-if="editModal.error_city" class="error-text">{{ editModal.error_city }}</p>
          </div>
          <!-- Fitness Level Select -->
          <div class="form-field">
            <label class="form-label">Уровень подготовки</label>
            <select
              v-model="editModal.fitness_level"
              class="form-input form-select"
            >
              <option value="" disabled>Выберите уровень</option>
              <option value="beginner">Начинающий</option>
              <option value="intermediate">Средний</option>
              <option value="advanced">Продвинутый</option>
            </select>
            <p v-if="editModal.error_fitness" class="error-text">{{ editModal.error_fitness }}</p>
          </div>
          <!-- Bio Input -->
          <div class="form-field">
            <label class="form-label">О себе</label>
            <textarea
              v-model="editModal.bio"
              class="form-input form-textarea"
              placeholder="Расскажите о себе"
              maxlength="255"
              rows="4"
            ></textarea>
            <p class="char-count">{{ (editModal.bio || '').length }}/255</p>
          </div>
        </div>
        <div class="modal-actions">
          <button class="modal-btn modal-btn-cancel" @click="closeEditProfileModal">
            Назад
          </button>
          <button class="modal-btn modal-btn-save" @click="saveEditProfile" :disabled="saving">
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
          <div class="settings-divider"></div>
          <button class="settings-item settings-item-logout" @click="handleLogout">
            <span class="material-symbols settings-icon">logout</span>
            <span class="settings-label">Выйти из профиля</span>
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
import { useRouter } from 'vue-router'
import { authApi } from '../api/index'
import defaultAvatar from '../assets/default-avatar.svg'

const router = useRouter();

const profile = ref({
  display_name: '',
  login: '',
  email: null,
  age: null,
  fitness_level: '',
  bio: '',
  avatar_url: '',
  role: 'user',
  city: '',
  preferences: {},
  theme: 'light',
  joined_events_count: 0,
  attended_events_count: 0,
});

const ratings = ref({
  empathy_score: 0,
  reliability_score: 100,
  total_events: 0,
  completed_events: 0,
});

const badges = ref([]);

const fileInput = ref(null);
const editAvatarFileInput = ref(null);
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

const toggleTheme = async () => {
  isDark.value = !isDark.value;
  const newTheme = isDark.value ? 'dark' : 'light';
  applyTheme();
  try {
    await authApi.updateTheme(newTheme);
  } catch (e) {
    console.error('Failed to update theme:', e.message);
  }
};

const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('app_visited');
  router.push('/login');
};

const showEditProfile = ref(false);

const openEditProfile = () => {
  showSettings.value = false;
  showEditProfile.value = true;
  editModal.value = {
    show: false,
    field: '',
    value: '',
    error: '',
    fromSettings: true,
    display_name: profile.value.display_name || '',
    age: profile.value.age ?? null,
    city: profile.value.city || '',
    fitness_level: profile.value.fitness_level || '',
    bio: profile.value.bio || '',
    avatar_url: profile.value.avatar_url || '',
    avatar_file: null,
    error_avatar: '',
    error_name: '',
    error_age: '',
    error_city: '',
    error_fitness: '',
  };
};

const openEditSingleField = (field) => {
  let currentValue = '';
  if (field === 'age') currentValue = profile.value.age ?? '';
  else if (field === 'city') currentValue = profile.value.city || '';
  else if (field === 'bio') currentValue = profile.value.bio ?? '';
  else if (field === 'display_name') currentValue = profile.value.display_name || '';
  else if (field === 'fitness_level') currentValue = profile.value.fitness_level || '';

  editModal.value = {
    show: true,
    field,
    value: currentValue,
    error: '',
    fromSettings: false,
    display_name: '',
    age: null,
    city: '',
    fitness_level: '',
    bio: '',
    avatar_url: '',
    avatar_file: null,
    error_avatar: '',
    error_name: '',
    error_age: '',
    error_city: '',
    error_fitness: '',
  };
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
    // Convert to base64/data URL
    const reader = new FileReader();
    reader.onload = async (e) => {
      const dataUrl = e.target.result;
      profile.value.avatar_url = dataUrl;

      // Upload to server
      try {
        await authApi.updateProfile({ avatar_url: dataUrl });
      } catch (e) {
        console.error('Failed to save avatar:', e.message);
        uploadError.value = 'Ошибка сохранения. Попробуйте снова.';
        // Revert on error
        profile.value.avatar_url = '';
      }
    };
    reader.readAsDataURL(file);
  } catch (e) {
    console.error('Failed to process avatar:', e.message);
    uploadError.value = 'Ошибка обработки. Попробуйте снова.';
  }

  // Reset input
  event.target.value = '';
};

const triggerEditAvatarInput = () => {
  editAvatarFileInput.value?.click();
};

const handleEditAvatarSelect = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;

  // Validate file type
  if (!file.type.startsWith('image/')) {
    editModal.value.error_avatar = 'Выберите изображение';
    return;
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    editModal.value.error_avatar = 'Файл слишком большой (макс. 5МБ)';
    return;
  }

  editModal.value.error_avatar = '';
  editModal.value.avatar_file = file;

  // Convert to base64/data URL for preview
  const reader = new FileReader();
  reader.onload = (e) => {
    editModal.value.avatar_url = e.target.result;
  };
  reader.readAsDataURL(file);

  // Reset input
  event.target.value = '';
};

const editModal = ref({
  show: false,
  field: '',
  value: '',
  error: '',
  fromSettings: false,
  // Full profile edit fields
  display_name: '',
  age: null,
  city: '',
  fitness_level: '',
  bio: '',
  avatar_url: '',
  avatar_file: null,
  error_avatar: '',
  // Validation errors
  error_name: '',
  error_age: '',
  error_city: '',
  error_fitness: '',
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
  fitness_level: 'Уровень подготовки',
};

const modalTitle = computed(() => modalTitles[editModal.value.field] || '');

const editProfile = (field) => {
  openEditSingleField(field);
};

const saveEditProfile = async () => {
  // Clear previous errors
  editModal.value.error_name = '';
  editModal.value.error_age = '';
  editModal.value.error_city = '';
  editModal.value.error_fitness = '';

  // Validate all fields are filled
  const nameVal = editModal.value.display_name?.trim();
  const ageVal = editModal.value.age;
  const cityVal = editModal.value.city;
  const fitnessVal = editModal.value.fitness_level;
  const bioVal = editModal.value.bio?.trim();

  let hasError = false;

  if (!nameVal) {
    editModal.value.error_name = 'Заполните поле "Имя"';
    hasError = true;
  }
  if (!ageVal || ageVal < 18 || ageVal > 120) {
    editModal.value.error_age = 'Заполните корректный возраст (18-120)';
    hasError = true;
  }
  if (!cityVal) {
    editModal.value.error_city = 'Выберите город';
    hasError = true;
  }
  if (!fitnessVal) {
    editModal.value.error_fitness = 'Выберите уровень подготовки';
    hasError = true;
  }

  if (hasError) return;

  // Save all fields from the full edit modal
  saving.value = true;
  try {
    const updateData = {};
    updateData.display_name = nameVal;
    updateData.age = parseInt(ageVal);

    const prefs = { ...profile.value.preferences, city: cityVal };
    updateData.preferences = prefs;

    updateData.fitness_level = fitnessVal;
    updateData.bio = bioVal || 'Пусто';

    // Convert avatar file to base64 if changed
    if (editModal.value.avatar_file) {
      const reader = new FileReader();
      const avatarBase64 = await new Promise((resolve, reject) => {
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(editModal.value.avatar_file);
      });
      updateData.avatar_url = avatarBase64;
    }

    await authApi.updateProfile(updateData);

    // Update local state
    profile.value.display_name = nameVal;
    profile.value.age = parseInt(ageVal);
    profile.value.city = cityVal;
    profile.value.preferences = { ...profile.value.preferences, city: cityVal };
    profile.value.fitness_level = fitnessVal;
    profile.value.bio = bioVal || 'Пусто';
    if (updateData.avatar_url) {
      profile.value.avatar_url = updateData.avatar_url;
    }

    showEditProfile.value = false;
  } catch (e) {
    console.error('Failed to save:', e.message);
  } finally {
    saving.value = false;
  }
};

const closeEditModal = () => {
  editModal.value = { show: false, field: '', value: '', error: '', fromSettings: false, display_name: '', age: null, city: '', fitness_level: '', bio: '', avatar_url: '', avatar_file: null, error_avatar: '', error_name: '', error_age: '', error_city: '', error_fitness: '' };
};

const closeEditProfileModal = () => {
  showEditProfile.value = false;
  editModal.value = { show: false, field: '', value: '', error: '', fromSettings: false, display_name: '', age: null, city: '', fitness_level: '', bio: '', avatar_url: '', avatar_file: null, error_avatar: '', error_name: '', error_age: '', error_city: '', error_fitness: '' };
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
    else if (field === 'fitness_level') updateData.fitness_level = value;

    await authApi.updateProfile(updateData);

    // Update local state
    if (field === 'display_name') profile.value.display_name = value.trim() || null;
    if (field === 'age') profile.value.age = parseInt(value);
    else if (field === 'city') {
      profile.value.city = value;
      profile.value.preferences = { ...profile.value.preferences, city: value };
    }
    else if (field === 'bio') profile.value.bio = value || null;
    else if (field === 'fitness_level') profile.value.fitness_level = value;

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

const fitnessLevelLabels = {
  beginner: 'Начинающий',
  intermediate: 'Средний',
  advanced: 'Продвинутый',
};

const getFitnessLevelLabel = (level) => fitnessLevelLabels[level] || 'Начинающий';

const fitnessLevelIcons = {
  beginner: 'fitness_center',
  intermediate: 'trending_up',
  advanced: 'directions_run',
};

const getFitnessLevelIcon = (level) => fitnessLevelIcons[level] || 'fitness_center';

const badgeIcons = {
  first_step: 'directions_walk',
  regular: 'emoji_events',
  ironman: 'self_improvement',
  reliable: 'verified_user',
  empathy: 'favorite',
  social: 'group',
};

const badgeLabels = {
  first_step: 'Первый шаг',
  regular: 'Постоянный',
  ironman: 'Железный человек',
  reliable: 'Надёжный',
  empathy: 'Эмпатия',
  social: 'Социальный',
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
      email: data.email || null,
      age: data.age,
      fitness_level: data.fitness_level || '',
      bio: data.bio ?? null,
      avatar_url: data.avatar_url || '',
      role: payload?.role || 'user',
      city: data.city || data.preferences?.city || '',
      preferences: data.preferences || {},
      theme: data.theme || 'light',
      joined_events_count: data.joined_events_count || 0,
      attended_events_count: data.attended_events_count || 0,
    };
    // Badges are included in the profile response
    badges.value = (data.badges || []).map((type, index) => ({
      id: index + 1,
      badge_type: type,
    }));
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

onMounted(async () => {
  await loadProfile();
  await loadRating();
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
  border: 4px solid #ea580c;
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
  background: #ea580c;
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
  color: #ea580c;
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
  color: #ea580c;
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
  background: linear-gradient(90deg, #ea580c, #ea580c);
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

/* === First Step Badge === */
.badge-first_step {
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
}

.badge-first_step .badge-icon-wrap {
  background: linear-gradient(135deg, #66bb6a, #2e7d32);
  box-shadow: 0 4px 12px rgba(46, 125, 50, 0.35);
}

.badge-first_step .badge-icon {
  color: #ffffff;
}

.badge-first_step .badge-label {
  color: #1b5e20;
}

/* === Regular Badge === */
.badge-regular {
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
}

.badge-regular .badge-icon-wrap {
  background: linear-gradient(135deg, #ffa726, #e65100);
  box-shadow: 0 4px 12px rgba(230, 81, 0, 0.35);
}

.badge-regular .badge-icon {
  color: #ffffff;
}

.badge-regular .badge-label {
  color: #bf360c;
}

/* === Ironman Badge === */
.badge-ironman {
  background: linear-gradient(135deg, #fce4ec, #f8bbd0);
}

.badge-ironman .badge-icon-wrap {
  background: linear-gradient(135deg, #ec407a, #ad1457);
  box-shadow: 0 4px 12px rgba(173, 20, 87, 0.35);
}

.badge-ironman .badge-icon {
  color: #ffffff;
}

.badge-ironman .badge-label {
  color: #880e4f;
}

/* === Reliable Badge === */
.badge-reliable {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
}

.badge-reliable .badge-icon-wrap {
  background: linear-gradient(135deg, #42a5f5, #1565c0);
  box-shadow: 0 4px 12px rgba(21, 101, 192, 0.35);
}

.badge-reliable .badge-icon {
  color: #ffffff;
}

.badge-reliable .badge-label {
  color: #0d47a1;
}

/* === Empathy Badge === */
.badge-empathy {
  background: linear-gradient(135deg, #fce4ec, #f8bbd0);
}

.badge-empathy .badge-icon-wrap {
  background: linear-gradient(135deg, #ef5350, #c62828);
  box-shadow: 0 4px 12px rgba(198, 40, 40, 0.35);
}

.badge-empathy .badge-icon {
  color: #ffffff;
}

.badge-empathy .badge-label {
  color: #b71c1c;
}

/* === Social Badge === */
.badge-social {
  background: linear-gradient(135deg, #ede7f6, #d1c4e9);
}

.badge-social .badge-icon-wrap {
  background: linear-gradient(135deg, #7e57c2, #4527a0);
  box-shadow: 0 4px 12px rgba(69, 39, 160, 0.35);
}

.badge-social .badge-icon {
  color: #ffffff;
}

.badge-social .badge-label {
  color: #311b92;
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
  border-color: #ea580c;
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
  background: linear-gradient(135deg, #ea580c, #ea580c);
  color: #ffffff;
}

.modal-btn-save:hover:not(:disabled) {
  opacity: 0.9;
}

/* ===== Avatar Upload ===== */
.avatar-upload-field {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.avatar-preview-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.avatar-preview {
  width: 96px;
  height: 96px;
  border-radius: 9999px;
  overflow: hidden;
  border: 3px solid #ea580c;
  background: #f3f4f5;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-change-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  color: #ea580c;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  padding: 6px 12px;
  border-radius: 9999px;
  transition: background 0.15s;
}

.avatar-change-btn:hover {
  background: #fff7ed;
}

.avatar-change-btn .material-symbols {
  font-size: 20px;
}

/* ===== Edit Profile Modal (scrollable) ===== */
.edit-profile-modal {
  max-width: 440px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.edit-profile-modal .modal-title {
  flex-shrink: 0;
  margin-bottom: 16px;
}

.modal-body-scrollable {
  overflow-y: auto;
  flex: 1;
  padding-right: 4px;
  -webkit-overflow-scrolling: touch;
}

.modal-body-scrollable::-webkit-scrollbar {
  width: 6px;
}

.modal-body-scrollable::-webkit-scrollbar-track {
  background: #f3f4f5;
  border-radius: 9999px;
}

.modal-body-scrollable::-webkit-scrollbar-thumb {
  background: #ea580c;
  border-radius: 9999px;
}

.modal-body-scrollable::-webkit-scrollbar-thumb:hover {
  background: #ea580c;
}

.edit-profile-modal .modal-actions {
  flex-shrink: 0;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e7e8e9;
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

.settings-item-logout:hover {
  background: #ffebee;
}

.settings-item-logout:hover .settings-icon {
  color: #ba1a1a;
}

.settings-item-logout:hover .settings-label {
  color: #ba1a1a;
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

.dark-theme .settings-item-logout:hover {
  background: #3e1616;
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
  color: #ea580c;
}
</style>
