function normalizeApiBase(url) {
  const normalized = (url || 'http://localhost:8005/api/v1').replace(/\/$/, '')
  return normalized.endsWith('/api/v1') ? normalized : `${normalized}/api/v1`
}

const GATEWAY_API_BASE_URL = normalizeApiBase(import.meta.env.VITE_API_BASE_URL)

export const config = {
  gatewayApiURL: GATEWAY_API_BASE_URL,
  userApiURL: GATEWAY_API_BASE_URL,
  placesApiURL: GATEWAY_API_BASE_URL,
  eventsApiURL: GATEWAY_API_BASE_URL,
  apiBaseURL: GATEWAY_API_BASE_URL,
  mediaBaseURL: GATEWAY_API_BASE_URL,
  osrmBaseURL: import.meta.env.VITE_OSRM_BASE_URL || 'https://router.project-osrm.org',
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  isDebug: import.meta.env.VITE_DEBUG === 'true',
  // VULN: internal microservice URLs are exposed in the client bundle for troubleshooting.
  exposedServices: {
    user: import.meta.env.VITE_USER_API_URL || 'http://localhost:8000/api/v1',
    events: import.meta.env.VITE_EVENTS_API_URL || 'http://localhost:8002/api/v1',
    admin: import.meta.env.VITE_ADMIN_API_URL || 'http://localhost:8003/api/v1',
    maps: import.meta.env.VITE_MAPS_API_URL || 'http://localhost:8004/api/v1',
    media: import.meta.env.VITE_MEDIA_API_URL || 'http://localhost:8006/api/v1'
  }
}

export const placesApi = (path) => `${config.gatewayApiURL}${path}`
export const eventsApi = (path) => `${config.gatewayApiURL}${path}`
export const api = (path) => `${config.gatewayApiURL}${path}`
export const mediaApi = (path) => `${config.gatewayApiURL}${path}`
