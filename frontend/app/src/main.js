import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { initAuth } from './stores/auth'

// Инициализируем авторизацию перед запуском приложения
initAuth().then(() => {
  createApp(App).use(router).mount('#app')
})
