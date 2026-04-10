export const config = {
  apiBaseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002/api/v1',
  osrmBaseURL: import.meta.env.VITE_OSRM_BASE_URL || 'https://router.project-osrm.org',
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  isDebug: import.meta.env.VITE_DEBUG === 'true'
}

// Helper: полный URL эндпоинта
export const api = (path) => `${config.apiBaseURL}${path}`
