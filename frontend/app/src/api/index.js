import { config, mediaApi } from '../config'

const API_BASE_URL = config.userApiURL
const IS_DEBUG = config.isDebug

// Переключи на true для использования mock-данных
const USE_MOCK = false

// ===== Logger =====
const LOG_PREFIX = '🌐 [API]'
const LOG_COLORS = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  magenta: '\x1b[35m',
  blue: '\x1b[34m',
  bgBlue: '\x1b[44m',
  bgGreen: '\x1b[42m',
  bgRed: '\x1b[41m',
  bgYellow: '\x1b[43m',
}

function logRequest(method, url, body, token) {
  if (!IS_DEBUG) return
  const timestamp = new Date().toLocaleTimeString('ru-RU')
  console.group(`${LOG_PREFIX} ${LOG_COLORS.bold}ЗАПРОС${LOG_COLORS.reset} ${LOG_COLORS.dim}${timestamp}${LOG_COLORS.reset}`)
  console.log(`${LOG_COLORS.cyan}Метод:${LOG_COLORS.reset}  ${LOG_COLORS.bold}${method}${LOG_COLORS.reset}`)
  console.log(`${LOG_COLORS.cyan}URL:${LOG_COLORS.reset}    ${LOG_COLORS.blue}${url}${LOG_COLORS.reset}`)
  if (token) {
    console.log(`${LOG_COLORS.cyan}Token:${LOG_COLORS.reset}  ${LOG_COLORS.dim}Bearer ${token.substring(0, 20)}...${LOG_COLORS.reset}`)
  }
  if (body) {
    // Маскируем чувствительные данные
    const safeBody = { ...body }
    if (safeBody.password) safeBody.password = '****'
    if (safeBody.new_password) safeBody.new_password = '****'
    if (safeBody.confirmPassword) safeBody.confirmPassword = '****'
    console.log(`${LOG_COLORS.cyan}Body:${LOG_COLORS.reset}   `, safeBody)
  }
  console.groupEnd()
}

function logResponse(status, statusText, data, duration) {
  if (!IS_DEBUG) return
  const timestamp = new Date().toLocaleTimeString('ru-RU')
  const isSuccess = status >= 200 && status < 300
  const statusColor = isSuccess ? LOG_COLORS.green : LOG_COLORS.red
  const statusBg = isSuccess ? LOG_COLORS.bgGreen : LOG_COLORS.bgRed
  const icon = isSuccess ? '✅' : '❌'

  console.group(`${LOG_PREFIX} ${icon} ${LOG_COLORS.bold}ОТВЕТ${LOG_COLORS.reset} ${LOG_COLORS.dim}${timestamp}${LOG_COLORS.reset} ${LOG_COLORS.dim}(${duration}ms)${LOG_COLORS.reset}`)
  console.log(`${LOG_COLORS.cyan}Статус:${LOG_COLORS.reset} ${statusBg}${statusColor} ${status} ${statusText} ${LOG_COLORS.reset}`)
  if (data !== null && data !== undefined) {
    console.log(`${LOG_COLORS.cyan}Data:${LOG_COLORS.reset}   `, data)
  }
  console.groupEnd()
}

function logError(method, url, error, duration) {
  if (!IS_DEBUG) return
  const timestamp = new Date().toLocaleTimeString('ru-RU')
  console.group(`${LOG_PREFIX} ${LOG_COLORS.bgRed}${LOG_COLORS.red} ОШИБКА ${LOG_COLORS.reset} ${LOG_COLORS.dim}${timestamp}${LOG_COLORS.reset} ${LOG_COLORS.dim}(${duration}ms)${LOG_COLORS.reset}`)
  console.log(`${LOG_COLORS.cyan}Метод:${LOG_COLORS.reset} ${LOG_COLORS.bold}${method}${LOG_COLORS.reset}`)
  console.log(`${LOG_COLORS.cyan}URL:${LOG_COLORS.reset}   ${LOG_COLORS.blue}${url}${LOG_COLORS.reset}`)
  console.log(`${LOG_COLORS.red}Ошибка:${LOG_COLORS.reset}  ${LOG_COLORS.red}${error.message || error}${LOG_COLORS.reset}`)
  console.groupEnd()
}

function logMockCall(name, isRequest) {
  if (!IS_DEBUG) return
  const icon = isRequest ? '📤' : '📥'
  const type = isRequest ? 'ЗАПРОС' : 'ОТВЕТ'
  console.log(`${LOG_PREFIX} ${icon} ${LOG_COLORS.magenta}[MOCK]${LOG_COLORS.reset} ${type}: ${LOG_COLORS.yellow}${name}${LOG_COLORS.reset}`)
}

// ===== Token Decoder =====
function decodeTokenPayload(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload
  } catch {
    return null
  }
}

// Конвертирует MinIO URL в Vite proxy URL (браузер не может напрямую к MinIO)
export function toProxyUrl(url) {
  if (!url) return url
  return url
    .replace('http://minio:9000/', '/minio-static/')
    .replace('http://localhost:9000/', '/minio-static/')
}

// ===== Phone Normalizer =====
function normalizePhone(phone) {
  if (!phone) return ''
  const cleaned = phone.replace(/[\s\-\(\)]/g, '')
  if (cleaned.startsWith('+')) return cleaned
  if (cleaned.startsWith('8') && cleaned.length === 11) return '+7' + cleaned.slice(1)
  if (cleaned.startsWith('7') && cleaned.length === 11) return '+' + cleaned
  if (cleaned.length === 10) return '+7' + cleaned
  return '+' + cleaned
}

// ===== Mock helpers =====
const delay = (ms = 500) => new Promise(r => setTimeout(r, ms))

function mockLogin(data) {
  logMockCall('login', true)
  return delay().then(() => {
    if (data.phone_number === 'fail' || data.password === 'fail') {
      logMockCall('login', false)
      console.log(`${LOG_PREFIX} ${LOG_COLORS.bgRed}${LOG_COLORS.red} MOCK ERROR ${LOG_COLORS.reset} ${LOG_COLORS.red}Неверный логин или пароль${LOG_COLORS.reset}`)
      throw new Error('Неверный логин или пароль')
    }
    const result = {
      access_token: 'mock-jwt-token-' + Date.now(),
      refresh_token: 'mock-refresh-token',
      user: { login: data.phone_number, display_name: data.phone_number },
    }
    logMockCall('login', false)
    console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
    return result
  })
}

function mockRegister(data) {
  logMockCall('register', true)
  return delay(800).then(() => {
    if (data.password !== data.confirmPassword) {
      logMockCall('register', false)
      console.log(`${LOG_PREFIX} ${LOG_COLORS.bgRed}${LOG_COLORS.red} MOCK ERROR ${LOG_COLORS.reset} ${LOG_COLORS.red}Пароли не совпадают${LOG_COLORS.reset}`)
      throw new Error('Пароли не совпадают')
    }
    const result = { access_token: 'mock-jwt-token-' + Date.now(), user: { display_name: data.display_name } }
    logMockCall('register', false)
    console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
    return result
  })
}

function mockSendResetCode(data) {
  logMockCall('sendResetCode', true)
  return delay().then(() => {
    if (!data.contact) {
      logMockCall('sendResetCode', false)
      console.log(`${LOG_PREFIX} ${LOG_COLORS.bgRed}${LOG_COLORS.red} MOCK ERROR ${LOG_COLORS.reset} ${LOG_COLORS.red}Введите номер телефона или Email${LOG_COLORS.reset}`)
      throw new Error('Введите номер телефона или Email')
    }
    const result = { message: 'Код отправлен', code: '123456' }
    logMockCall('sendResetCode', false)
    console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
    return result
  })
}

function mockResetPassword(data) {
  logMockCall('resetPassword', true)
  return delay(800).then(() => {
    if (data.code !== '123456') {
      logMockCall('resetPassword', false)
      console.log(`${LOG_PREFIX} ${LOG_COLORS.bgRed}${LOG_COLORS.red} MOCK ERROR ${LOG_COLORS.reset} ${LOG_COLORS.red}Неверный код${LOG_COLORS.reset}`)
      throw new Error('Неверный код')
    }
    if (data.new_password !== data.confirmPassword) {
      logMockCall('resetPassword', false)
      console.log(`${LOG_PREFIX} ${LOG_COLORS.bgRed}${LOG_COLORS.red} MOCK ERROR ${LOG_COLORS.reset} ${LOG_COLORS.red}Пароли не совпадают${LOG_COLORS.reset}`)
      throw new Error('Пароли не совпадают')
    }
    const result = { message: 'Пароль изменён' }
    logMockCall('resetPassword', false)
    console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
    return result
  })
}

function mockGetProfile() {
  logMockCall('getProfile', true)
  return delay().then(() => {
    const result = {
      display_name: 'Тестовый Пользователь',
      login: '+79001234567',
      email: 'test@example.com',
      age: 25,
      fitness_level: 'intermediate',
      bio: 'Люблю бег и воркаут!',
      avatar_url: '',
      role: 'user',
      city: 'Орёл',
      preferences: {},
      theme: 'light',
      joined_events_count: 12,
      attended_events_count: 8,
    }
    logMockCall('getProfile', false)
    console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
    return result
  })
}

function mockGetRating() {
  logMockCall('getRating', true)
  return delay().then(() => {
    const result = { empathy_score: 42, reliability_score: 87.5, total_events: 12, completed_events: 10 }
    logMockCall('getRating', false)
    console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
    return result
  })
}

function mockGetBadges() {
  logMockCall('getBadges', true)
  return delay().then(() => {
    const result = [{ id: 1, badge_type: 'first_step' }, { id: 2, badge_type: 'regular' }]
    logMockCall('getBadges', false)
    console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
    return result
  })
}

// ===== Real API =====
async function request(path, options = {}) {
  const method = options.method || 'GET'
  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`
  const token = localStorage.getItem('token')

  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const body = options.body ? JSON.stringify(options.body) : undefined
  const startTime = Date.now()

  // Логируем запрос
  logRequest(method, url, options.body, token)

  try {
    const response = await fetch(url, { ...options, headers, body })
    const duration = Date.now() - startTime

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      logResponse(response.status, response.statusText, data, duration)
      const detail = data.detail || data.message
      const errorMessage = extractErrorMessage(detail) || `Ошибка сервера: ${response.status}`
      throw new Error(errorMessage)
    }

    if (response.status === 204) {
      logResponse(204, 'No Content', null, duration)
      return null
    }

    const data = await response.json()
    logResponse(response.status, response.statusText, data, duration)
    return data
  } catch (error) {
    const duration = Date.now() - startTime
    logError(method, url, error, duration)
    throw error
  }
}

function extractErrorMessage(detail) {
  if (!detail) return null
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map(item => extractErrorMessage(item)).filter(Boolean).join('. ')
  }
  if (typeof detail === 'object') {
    return Object.entries(detail)
      .map(([key, value]) => {
        const msg = extractErrorMessage(value)
        return msg ? `${key}: ${msg}` : null
      })
      .filter(Boolean)
      .join('. ')
  }
  return String(detail)
}

// ===== Export =====
export const authApi = USE_MOCK
  ? {
      register(data) {
        const body = {
          phone_number: normalizePhone(data.phone_number),
          password: data.password,
          display_name: data.display_name,
          ...(data.email ? { email: data.email } : {}),
        }
        logMockCall('register', true)
        console.log(`${LOG_PREFIX} ${LOG_COLORS.cyan}Payload:${LOG_COLORS.reset}`, body)
        return mockRegister(data)
      },
      login(data) {
        const body = {
          phone_number: normalizePhone(data.phone_number),
          password: data.password,
        }
        logMockCall('login', true)
        console.log(`${LOG_PREFIX} ${LOG_COLORS.cyan}Payload:${LOG_COLORS.reset}`, { ...body, password: '****' })
        return mockLogin(data)
      },
      getProfile() {
        return mockGetProfile()
      },
      updateProfile(data) {
        logMockCall('updateProfile', true)
        console.log(`${LOG_PREFIX} ${LOG_COLORS.cyan}Payload:${LOG_COLORS.reset}`, data)
        return delay(500).then(() => {
          logMockCall('updateProfile', false)
          const result = { message: 'Профиль обновлён' }
          console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
          return result
        })
      },
      updateContact(data) {
        logMockCall('updateContact', true)
        console.log(`${LOG_PREFIX} ${LOG_COLORS.cyan}Payload:${LOG_COLORS.reset}`, data)
        return delay(500).then(() => {
          logMockCall('updateContact', false)
          const result = { message: 'Контакт обновлён' }
          console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
          return result
        })
      },
      getRating() {
        return mockGetRating()
      },
      getBadges() {
        return mockGetBadges()
      },
      getPublicProfile(userId) {
        logMockCall('getPublicProfile', true)
        console.log(`${LOG_PREFIX} ${LOG_COLORS.cyan}userId:${LOG_COLORS.reset}`, userId)
        return mockGetProfile()
      },
      updateTheme(theme) {
        logMockCall('updateTheme', true)
        console.log(`${LOG_PREFIX} ${LOG_COLORS.cyan}theme:${LOG_COLORS.reset}`, theme)
        return delay(300).then(() => {
          logMockCall('updateTheme', false)
          const result = { message: 'Тема обновлена' }
          console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
          return result
        })
      },
      getAllUsers() {
        logMockCall('getAllUsers', true)
        return delay(300).then(() => {
          const result = {
            users: [
              { user_id: '1', display_name: 'Алексей', city: 'Орёл', age: 28, avatar_url: '', empathy_score: 42, reliability_score: 95.5, badges: [] },
              { user_id: '2', display_name: 'Мария', city: 'Орёл', age: 24, avatar_url: '', empathy_score: 67, reliability_score: 88.0, badges: [] },
              { user_id: '3', display_name: 'Дмитрий', city: 'Орёл', age: 31, avatar_url: '', empathy_score: 33, reliability_score: 72.3, badges: [] },
            ],
            total: 3,
            limit: 20,
            offset: 0,
          }
          logMockCall('getAllUsers', false)
          console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
          return result
        })
      },
      getUploadUrl({ purpose, content_type, file_size }) {
        logMockCall('getUploadUrl', true)
        return delay(300).then(() => {
          const fileKey = `${purpose}/mock/${Date.now()}.${content_type.split('/')[1]}`
          const result = {
            file_key: fileKey,
            upload_url: 'http://localhost:9000/dev-media',
            fields: { key: fileKey, 'Content-Type': content_type },
            public_url: `http://localhost:9000/dev-media/${fileKey}`,
          }
          logMockCall('getUploadUrl', false)
          console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, result)
          return result
        })
      },
      uploadToS3({ file }) {
        logMockCall('uploadToS3', true)
        return delay(500).then(() => {
          logMockCall('uploadToS3', false)
          console.log(`${LOG_PREFIX} ${LOG_COLORS.bgGreen}${LOG_COLORS.green} MOCK OK ${LOG_COLORS.reset}`, { name: file?.name })
          return { ok: true }
        })
      },
    }
  : {
      register(data) {
        const body = {
          phone_number: normalizePhone(data.phone_number),
          password: data.password,
          display_name: data.display_name,
          ...(data.email ? { email: data.email } : {}),
        }
        return request('/auth/register', { method: 'POST', body })
      },
      login(data) {
        const body = {
          phone_number: normalizePhone(data.phone_number),
          password: data.password,
        }
        return request('/auth/login', { method: 'POST', body })
      },
      getProfile() {
        return request('/users/me')
      },
      updateProfile(data) {
        return request('/users/me', { method: 'PUT', body: data })
      },
      updateContact(data) {
        return request('/users/me/contact', { method: 'PUT', body: data })
      },
      getRating() {
        return request('/users/me/rating')
      },
      getBadges() {
        return request('/users/me/badges')
      },
      getPublicProfile(userId) {
        return request(`/users/${userId}`)
      },
      updateTheme(theme) {
        return request('/users/me/theme', { method: 'POST', body: { theme } })
      },
      getAllUsers() {
        return request('/users')
      },

      // Получение presigned URL для загрузки файла в S3
      async getUploadUrl({ purpose, content_type, file_size }) {
        const token = localStorage.getItem('token')
        const userId = token ? decodeTokenPayload(token)?.sub : null
        if (!userId) throw new Error('Не авторизован')

        const url = mediaApi('/media/upload-url')
        const body = { purpose, content_type, file_size, owner_id: userId }
        logRequest('POST', url, { ...body }, token)

        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.detail || 'Ошибка получения URL загрузки')
        return data
      },

      // Прямая загрузка файла в S3 через presigned POST
      async uploadToS3({ upload_url, fields, file }) {
        // Проксируем через Vite dev server — браузер не может напрямую к MinIO
        // из-за системного HTTP-прокси. Vite работает как обратный прокси.
        const devServerUrl = upload_url
          .replace('http://minio:9000', 'http://localhost:5173/minio-upload')
          .replace('http://localhost:9000', 'http://localhost:5173/minio-upload')

        const formData = new FormData()
        Object.entries(fields).forEach(([key, value]) => {
          formData.append(key, value)
        })
        formData.append('file', file)

        const response = await fetch(devServerUrl, { method: 'POST', body: formData })
        if (!response.ok) throw new Error('Ошибка загрузки файла в хранилище')
        return response
      },
    }
