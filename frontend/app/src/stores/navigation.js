import { reactive, computed } from 'vue'

// Реактивный стейт навигации — общий для MapLight и MainPage
export const navigationStore = reactive({
  isNavigating: false,
  activeRoute: 'fast',
  routeCoords: [],           // [[lat, lng], ...]
  userPosition: null,        // { lat, lng }
  navRemaining: { distance: '0 м', duration: '0 мин' },
  routeColor: '#ea580c'
})

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
}

export function updateNavPosition(pos) {
  navigationStore.userPosition = pos ? { ...pos } : null
}

export function updateNavRemaining(remaining) {
  navigationStore.navRemaining = remaining ? { ...remaining } : { distance: '0 м', duration: '0 мин' }
}
