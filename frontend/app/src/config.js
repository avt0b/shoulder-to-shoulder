// Жёстко задаём URL бэкенда, т.к. Vite на Windows кэширует env из родительских директорий
const API_BASE_URL = '/api/users'  // Через Vite proxy -> localhost:8000
const MEDIA_BASE_URL = '/api/media'  // Через Vite proxy -> localhost:8006
const EVENTS_BASE_URL = '/api/events'  // Через Vite proxy -> localhost:8002
const PLACES_BASE_URL = '/api/places'  // Через Vite proxy -> localhost:8004

export const config = {
  userApiURL: '/api/users',  // Через Vite proxy
  placesApiURL: '/api/places',  // Через Vite proxy
  eventsApiURL: '/api/events',  // Через Vite proxy
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
