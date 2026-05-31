import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { initAuth, clearAuthSession } from './stores/auth'

function installUnauthorizedInterceptor() {
  const nativeFetch = window.fetch.bind(window)

  window.fetch = async (input, init) => {
    const response = await nativeFetch(input, init)
    const url = typeof input === 'string' ? input : input?.url || ''
    const isAuthRequest = url.includes('/auth/login') || url.includes('/auth/register')

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
