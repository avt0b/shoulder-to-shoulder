// Жёстко задаём URL бэкенда, т.к. Vite на Windows кэширует env из родительских директорий
const API_BASE_URL = 'http://localhost:8000/api/v1'
const MEDIA_BASE_URL = 'http://localhost:8006/api/v1'

export const config = {
  userApiURL: import.meta.env.VITE_USER_API_URL || 'http://localhost:8000/api/v1',
  placesApiURL: import.meta.env.VITE_PLACES_API_URL || 'http://localhost:8004/api/v1',
  eventsApiURL: import.meta.env.VITE_EVENTS_API_URL || 'http://localhost:8002/api/v1',
  apiBaseURL: API_BASE_URL,
  mediaBaseURL: MEDIA_BASE_URL,
  osrmBaseURL: import.meta.env.VITE_OSRM_BASE_URL || 'https://router.project-osrm.org',
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  isDebug: import.meta.env.VITE_DEBUG === 'true'
}

// Helper: полный URL эндпоинта для Places сервиса (maps_service :8004)
export const placesApi = (path) => `${config.placesApiURL}${path}`

// Helper: полный URL эндпоинта для Events сервиса (event_service :8002)
export const eventsApi = (path) => `${config.eventsApiURL}${path}`
// Helper: полный URL эндпоинта
export const api = (path) => `${config.apiBaseURL}${path}`
export const mediaApi = (path) => `${config.mediaBaseURL}${path}`
