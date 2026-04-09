/**
 * Координаты центра города Орла (fallback)
 */
const OREL_CENTER = {
  lat: 52.9651,
  lng: 36.0785,
  name: 'Центр Орла'
}

/**
 * Получить текущую позицию GPS
 * Если GPS недоступен - возвращает центр Орла
 * @returns {Promise<{lat: number, lng: number, accuracy?: number, name?: string}>}
 */
export const getCurrentPosition = () => {
  return new Promise((resolve) => {
    // Если браузер поддерживает Geolocation API
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude, accuracy } = position.coords
          console.log(`📍 GPS получена: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`)
          resolve({
            lat: latitude,
            lng: longitude,
            accuracy: accuracy,
            name: 'Текущая позиция'
          })
        },
        (error) => {
          console.warn('⚠️ GPS не доступна, используем центр Орла:', error.message)
          resolve(OREL_CENTER)
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        }
      )
    } else {
      console.warn('⚠️ Geolocation не поддерживается, используем центр Орла')
      resolve(OREL_CENTER)
    }
  })
}

/**
 * Получить центр Орла (fallback координаты)
 */
export const getOrelCenter = () => {
  return { ...OREL_CENTER }
}

/**
 * Некоторые тестовые точки в Орле
 */
export const OREL_PLACES = {
  cityCenter: { lat: 52.9651, lng: 36.0785, name: 'Центр города' },
  parkOfVictory: { lat: 52.9690, lng: 36.0820, name: 'Парк Победы' },
  stadium: { lat: 52.9580, lng: 36.0780, name: 'Стадион Центральный' },
  museum: { lat: 52.9720, lng: 36.0750, name: 'Музей' }
}

/**
 * Вычислить расстояние между двумя точками (Haversine formula)
 */
export const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371000 // Радиус Земли в метрах
  const toRad = (deg) => (deg * Math.PI) / 180

  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) * Math.sin(dLng / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c // Расстояние в метрах
}

/**
 * Форматировать расстояние для отображения
 */
export const formatDistance = (meters) => {
  if (meters < 1000) {
    return `${Math.round(meters)} м`
  }
  return `${(meters / 1000).toFixed(2)} км`
}

/**
 * Форматировать время в секундах
 */
export const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (mins === 0) {
    return `${secs}с`
  }
  return `${mins}м ${secs}с`
}
