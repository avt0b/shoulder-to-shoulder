// Жёстко задаём URL бэкенда, т.к. Vite на Windows кэширует env из родительских директорий
const API_BASE_URL = 'http://localhost:8000/api/v1'
const MEDIA_BASE_URL = 'http://localhost:8006/api/v1'

export const config = {
  apiBaseURL: API_BASE_URL,
  mediaBaseURL: MEDIA_BASE_URL,
  osrmBaseURL: import.meta.env.VITE_OSRM_BASE_URL || 'https://router.project-osrm.org',
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  isDebug: import.meta.env.VITE_DEBUG === 'true'
}

// Helper: полный URL эндпоинта
export const api = (path) => `${config.apiBaseURL}${path}`
export const mediaApi = (path) => `${config.mediaBaseURL}${path}`
