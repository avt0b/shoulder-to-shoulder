import axios from 'axios'
import { config } from '@/config'

// Создаём экземпляр axios с базовым URL
const apiClient = axios.create({
  baseURL: config.apiBaseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Обработчик ошибок
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error.response?.data || error.message)
    throw error
  }
)

export default apiClient

// ===== МЕСТА =====

/**
 * Получить все места на карте
 */
export const getPlaces = () => {
  return apiClient.get('/places')
}

/**
 * Получить одно место по ID
 */
export const getPlace = (id) => {
  return apiClient.get(`/places/${id}`)
}

/**
 * Получить ближайшие места от текущей позиции
 */
export const getNearbyPlaces = (lat, lng, radius = 2000) => {
  return apiClient.get('/places/nearby', {
    params: { lat, lng, radius }
  })
}

// ===== МАРШРУТЫ =====

/**
 * Построить маршрут между двумя точками
 * @param {number} startLat - Широта начальной точки
 * @param {number} startLng - Долгота начальной точки
 * @param {number} endLat - Широта конечной точки
 * @param {number} endLng - Долгота конечной точки
 */
export const getRoute = (startLat, startLng, endLat, endLng) => {
  return apiClient.get('/route', {
    params: {
      start_lat: startLat,
      start_lng: startLng,
      end_lat: endLat,
      end_lng: endLng
    }
  })
}

// ===== МЕРОПРИЯТИЯ =====

/**
 * Получить мои мероприятия
 */
export const getMyMeetups = () => {
  return apiClient.get('/meetups/my')
}

/**
 * Записаться на мероприятие
 */
export const joinMeetup = (meetupId, userId = 1) => {
  return apiClient.post(`/meetups/${meetupId}/join`, {
    user_id: userId
  })
}

/**
 * Отписаться от мероприятия
 */
export const leaveMeetup = (meetupId, userId = 1) => {
  return apiClient.delete(`/meetups/${meetupId}/leave`, {
    params: { user_id: userId }
  })
}
