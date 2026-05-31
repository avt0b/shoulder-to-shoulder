import { config, mediaApi } from '../config'

const API_BASE_URL = config.userApiURL
const IS_DEBUG = config.isDebug

const LOG_PREFIX = '[API]'

function logRequest(method, url, body, token) {
  if (!IS_DEBUG) return
  const safeBody = body ? { ...body } : null
  if (safeBody?.password) safeBody.password = '****'
  if (safeBody?.new_password) safeBody.new_password = '****'
  if (safeBody?.confirmPassword) safeBody.confirmPassword = '****'
  console.log(`${LOG_PREFIX} ${method} ${url}`, {
    token: token ? `Bearer ${token.substring(0, 20)}...` : null,
    body: safeBody
  })
}

function logResponse(status, statusText, data, duration) {
  if (!IS_DEBUG) return
  console.log(`${LOG_PREFIX} ${status} ${statusText} (${duration}ms)`, data)
}

function logError(method, url, error, duration) {
  if (!IS_DEBUG) return
  console.warn(`${LOG_PREFIX} ${method} ${url} failed (${duration}ms)`, error)
}

function decodeTokenPayload(token) {
  try {
    return JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
  } catch {
    return null
  }
}

export function toProxyUrl(url) {
  if (!url || typeof url !== 'string') return url
  if (url.startsWith('http://minio:9000/')) return url.replace('http://minio:9000/', '/minio-static/')
  if (url.startsWith('http://localhost:9000/')) return url.replace('http://localhost:9000/', '/minio-static/')
  if (url.startsWith('http://localhost:8006/api/v1')) {
    return url.replace('http://localhost:8006/api/v1', config.mediaBaseURL)
  }
  return url
}

export function getMediaUrl(category, userId, fileName) {
  if (!category || !userId || !fileName) return ''
  return `${config.mediaBaseURL}/${category}/${userId}/${fileName}`
}

function normalizePhone(phone) {
  if (!phone) return ''
  const cleaned = phone.replace(/[\s\-()]/g, '')
  if (cleaned.startsWith('+')) return cleaned
  if (cleaned.startsWith('8') && cleaned.length === 11) return '+7' + cleaned.slice(1)
  if (cleaned.startsWith('7') && cleaned.length === 11) return '+' + cleaned
  if (cleaned.length === 10) return '+7' + cleaned
  return '+' + cleaned
}

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

  logRequest(method, url, options.body, token)

  try {
    const response = await fetch(url, { ...options, headers, body })
    const duration = Date.now() - startTime

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      logResponse(response.status, response.statusText, data, duration)
      const detail = data.detail || data.message
      throw new Error(extractErrorMessage(detail) || `Ошибка сервера: ${response.status}`)
    }

    if (response.status === 204) {
      logResponse(204, 'No Content', null, duration)
      return null
    }

    const data = await response.json()
    logResponse(response.status, response.statusText, data, duration)
    return data
  } catch (error) {
    logError(method, url, error, Date.now() - startTime)
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

export const authApi = {
  register(data) {
    return request('/auth/register', {
      method: 'POST',
      body: {
        phone_number: normalizePhone(data.phone_number),
        password: data.password,
        display_name: data.display_name,
        ...(data.email ? { email: data.email } : {}),
      }
    })
  },
  login(data) {
    return request('/auth/login', {
      method: 'POST',
      body: {
        phone_number: normalizePhone(data.phone_number),
        password: data.password,
      }
    })
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
  async getUploadUrl({ purpose, content_type, file_size }) {
    const token = localStorage.getItem('token')
    const ownerId = token ? decodeTokenPayload(token)?.sub : null
    if (!ownerId) throw new Error('Не авторизован')

    const body = { purpose, content_type, file_size, owner_id: ownerId }
    return request('/media/upload-url', { method: 'POST', body })
  },
  async uploadToS3({ upload_url, fields, file }) {
    const formData = new FormData()
    Object.entries(fields).forEach(([key, value]) => formData.append(key, value))
    formData.append('file', file)

    const response = await fetch(upload_url, { method: 'POST', body: formData })
    if (!response.ok) throw new Error('Ошибка загрузки файла в хранилище')
    return response
  },
  async uploadMedia({ purpose, file }) {
    const token = localStorage.getItem('token')
    const ownerId = token ? decodeTokenPayload(token)?.sub : null
    if (!ownerId) throw new Error('Не авторизован')

    const formData = new FormData()
    formData.append('purpose', purpose)
    formData.append('owner_id', ownerId)
    formData.append('file', file)

    const response = await fetch(mediaApi('/media/upload'), {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || 'Ошибка загрузки файла')
    return data
  },
}

export const mediaGetApi = {
  async getMedia(category, userId, fileName) {
    const url = `${config.mediaBaseURL}/${category}/${userId}/${fileName}`
    const startTime = Date.now()
    try {
      const response = await fetch(url)
      if (!response.ok) throw new Error(`Ошибка загрузки файла: ${response.status}`)
      const blob = await response.blob()
      logResponse(response.status, response.statusText, `Файл (${blob.size} bytes)`, Date.now() - startTime)
      return blob
    } catch (error) {
      logError('GET', url, error, Date.now() - startTime)
      throw error
    }
  },
  getMediaUrl(category, userId, fileName) {
    return toProxyUrl(`${config.mediaBaseURL}/${category}/${userId}/${fileName}`)
  },
  getDirectUrl(category, userId, fileName) {
    return this.getMediaUrl(category, userId, fileName)
  }
}
