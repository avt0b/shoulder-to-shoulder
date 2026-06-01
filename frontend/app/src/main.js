import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { initAuth, clearAuthSession } from './stores/auth'
import { config } from './config'

const savedTheme = localStorage.getItem('theme')
document.documentElement.classList.toggle('dark-theme', savedTheme === 'dark')

function installUnauthorizedInterceptor() {
  const nativeFetch = window.fetch.bind(window)

  window.fetch = async (input, init = {}) => {
    const url = typeof input === 'string' ? input : input?.url || ''
    const isAuthRequest = url.includes('/auth/login') || url.includes('/auth/register')
    const isApiRequest = url.startsWith(config.gatewayApiURL) || url.startsWith('/api/v1/')
    const token = localStorage.getItem('token')
    const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined))

    if (token && isApiRequest && !isAuthRequest && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`)
    }

    const response = await nativeFetch(input, { ...init, headers })

    if (response.status === 401 && !isAuthRequest) {
      clearAuthSession()
      if (router.currentRoute.value.path !== '/login') {
        router.replace('/login')
      }
    }

    return response
  }
}

installUnauthorizedInterceptor()

// Инициализируем авторизацию перед запуском приложения
initAuth().then(() => {
  createApp(App).use(router).mount('#app')
})
