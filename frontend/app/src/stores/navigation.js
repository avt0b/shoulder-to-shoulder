import { reactive, computed } from 'vue'

const STORAGE_KEY = 'shoulder_navigation'

// Реактивный стейт навигации — общий для MapLight и MainPage
export const navigationStore = reactive({
  isNavigating: false,
  activeRoute: 'fast',
  routeCoords: [],           // [[lat, lng], ...]
  userPosition: null,        // { lat, lng }
  navRemaining: { distance: '0 м', duration: '0 мин' },
  routeColor: '#ea580c'
})

// Восстановление из localStorage при старте
function loadFromStorage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const data = JSON.parse(stored)
      navigationStore.isNavigating = data.isNavigating || false
      navigationStore.activeRoute = data.activeRoute || 'fast'
      navigationStore.routeCoords = data.routeCoords || []
      navigationStore.userPosition = data.userPosition || null
      navigationStore.navRemaining = data.navRemaining || { distance: '0 м', duration: '0 мин' }
      navigationStore.routeColor = data.activeRoute === 'fast' ? '#ea580c' : '#16a34a'
    }
  } catch (e) {
    console.warn('Navigation storage load error:', e)
  }
}

function saveToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      isNavigating: navigationStore.isNavigating,
      activeRoute: navigationStore.activeRoute,
      routeCoords: navigationStore.routeCoords,
      userPosition: navigationStore.userPosition,
      navRemaining: navigationStore.navRemaining
    }))
  } catch (e) {
    console.warn('Navigation storage save error:', e)
  }
}

// Вызываем при загрузке модуля
loadFromStorage()

export function setNavigation(active, data = {}) {
  navigationStore.isNavigating = active
  if (active) {
    navigationStore.activeRoute = data.activeRoute || 'fast'
    // Копируем массив чтобы Vue отследил изменения
    navigationStore.routeCoords = data.routeCoords ? [...data.routeCoords] : []
    navigationStore.userPosition = data.userPosition ? { ...data.userPosition } : null
    navigationStore.navRemaining = data.navRemaining || { distance: '0 м', duration: '0 мин' }
    navigationStore.routeColor = data.activeRoute === 'fast' ? '#ea580c' : '#16a34a'
  } else {
    navigationStore.activeRoute = 'fast'
    navigationStore.routeCoords = []
    navigationStore.userPosition = null
    navigationStore.navRemaining = { distance: '0 м', duration: '0 мин' }
    navigationStore.routeColor = '#ea580c'
  }
  saveToStorage()
}

export function updateNavPosition(pos) {
  navigationStore.userPosition = pos ? { ...pos } : null
  saveToStorage()
}

export function updateNavRemaining(remaining) {
  navigationStore.navRemaining = remaining ? { ...remaining } : { distance: '0 м', duration: '0 мин' }
  saveToStorage()
}
