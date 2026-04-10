import { reactive } from 'vue'
import { authApi, toProxyUrl } from '../api'

const STORAGE_KEY = 'shoulder_auth'
const LOG_PREFIX = '🔐 [Auth]'

// Реактивный стейт авторизации
export const authStore = reactive({
  isAuthenticated: false,
  user: null,
  token: null,
  loading: false,
  error: null,
})

// Восстановление из localStorage при старте
function loadFromStorage() {
  try {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem(STORAGE_KEY)
    if (token && userData) {
      authStore.token = token
      authStore.user = JSON.parse(userData)
      authStore.isAuthenticated = true
      console.log(`${LOG_PREFIX} ✅ Сессия восстановлена из storage:`, authStore.user.display_name || authStore.user.login)
      return true
    }
    console.log(`${LOG_PREFIX} ⚪ Нет сохранённой сессии`)
  } catch (e) {
    console.warn(`${LOG_PREFIX} Ошибка загрузки storage:`, e)
  }
  return false
}

function saveToStorage() {
  try {
    if (authStore.token) {
      localStorage.setItem('token', authStore.token)
    }
    if (authStore.user) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(authStore.user))
    }
  } catch (e) {
    console.warn(`${LOG_PREFIX} Ошибка сохранения в storage:`, e)
  }
}

function clearStorage() {
  localStorage.removeItem('token')
  localStorage.removeItem(STORAGE_KEY)
  localStorage.removeItem('app_visited')
  console.log(`${LOG_PREFIX} 🗑️ Сессия очищена`)
}

// Вызываем при загрузке модуля
loadFromStorage()

export async function login(credentials) {
  console.log(`${LOG_PREFIX} 📤 Вход для:`, credentials.phone_number)
  authStore.loading = true
  authStore.error = null
  try {
    const data = await authApi.login(credentials)
    authStore.token = data.access_token
    authStore.isAuthenticated = true
    saveToStorage()
    console.log(`${LOG_PREFIX} ✅ Вход успешен, загружаем профиль...`)

    // Бэкенд возвращает только токены — загружаем профиль отдельно
    const profile = await loadProfile()
    if (!profile) {
      // Если не удалось загрузить профиль, используем минимум из токена
      authStore.user = { login: credentials.phone_number }
      saveToStorage()
    }
    return data
  } catch (e) {
    authStore.error = e.message
    console.log(`${LOG_PREFIX} ❌ Ошибка входа:`, e.message)
    throw e
  } finally {
    authStore.loading = false
  }
}

export async function register(data) {
  console.log(`${LOG_PREFIX} 📤 Регистрация для:`, data.phone_number, 'имя:', data.display_name)
  authStore.loading = true
  authStore.error = null
  try {
    const { confirmPassword, ...apiData } = data
    const result = await authApi.register(apiData)
    if (result.access_token) {
      authStore.token = result.access_token
      authStore.isAuthenticated = true
      saveToStorage()
      console.log(`${LOG_PREFIX} ✅ Регистрация успешна, загружаем профиль...`)

      // Бэкенд возвращает только токены — загружаем профиль отдельно
      const profile = await loadProfile()
      if (!profile) {
        // Фоллбэк: используем данные из формы
        authStore.user = { display_name: data.display_name, login: data.phone_number }
        saveToStorage()
      }
    }
    return result
  } catch (e) {
    authStore.error = e.message
    console.log(`${LOG_PREFIX} ❌ Ошибка регистрации:`, e.message)
    throw e
  } finally {
    authStore.loading = false
  }
}

export async function loadProfile() {
  console.log(`${LOG_PREFIX} 📥 Загрузка профиля...`)
  try {
    const profile = await authApi.getProfile()
    const processedProfile = {
      ...profile,
      avatar_url: toProxyUrl(profile.avatar_url),
    }
    authStore.user = { ...authStore.user, ...processedProfile }
    saveToStorage()
    console.log(`${LOG_PREFIX} ✅ Профиль загружен:`, processedProfile.display_name || authStore.user.display_name)
    return processedProfile
  } catch (e) {
    console.warn(`${LOG_PREFIX} ⚠️ Не удалось загрузить профиль:`, e.message)
    return null
  }
}

export async function fetchRating() {
  if (!authStore.isAuthenticated) return { empathy_score: 0, reliability_score: 100, total_events: 0, completed_events: 0 }
  try {
    console.log(`${LOG_PREFIX} 📥 Загрузка рейтинга...`)
    const rating = await authApi.getRating()
    console.log(`${LOG_PREFIX} ✅ Рейтинг загручен:`, `надёжность: ${rating.reliability_score}%, эмпатия: ${rating.empathy_score}`)
    return rating
  } catch (e) {
    console.warn(`${LOG_PREFIX} ⚠️ Не удалось загрузить рейтинг:`, e.message)
    return { empathy_score: 0, reliability_score: 100, total_events: 0, completed_events: 0 }
  }
}

export async function fetchBadges() {
  if (!authStore.isAuthenticated) return []
  try {
    console.log(`${LOG_PREFIX} 📥 Загрузка достижений...`)
    const badges = await authApi.getBadges()
    console.log(`${LOG_PREFIX} ✅ Достижения загружены:`, badges.length, 'шт.')
    return badges
  } catch (e) {
    console.warn(`${LOG_PREFIX} ⚠️ Не удалось загрузить достижения:`, e.message)
    return []
  }
}

export function logout() {
  const userName = authStore.user?.display_name || authStore.user?.login || 'Неизвестный'
  console.log(`${LOG_PREFIX} 🚪 Выход пользователя:`, userName)
  authStore.isAuthenticated = false
  authStore.user = null
  authStore.token = null
  authStore.error = null
  clearStorage()
}

export function isLoggedIn() {
  return authStore.isAuthenticated && !!authStore.token
}

// Инициализация при старте
export async function initAuth() {
  console.log(`${LOG_PREFIX} 🚀 Инициализация авторизации...`)
  if (authStore.isAuthenticated) {
    console.log(`${LOG_PREFIX} 🔄 Пользователь авторизован, обновляем профиль...`)
    await loadProfile()
  } else {
    console.log(`${LOG_PREFIX} 🔓 Пользователь не авторизован`)
  }
  return authStore.isAuthenticated
}
