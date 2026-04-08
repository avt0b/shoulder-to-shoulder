import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Блокировка ориентации экрана
if (screen.orientation && screen.orientation.lock) {
  screen.orientation.lock('portrait').catch(() => {});
}

createApp(App).use(router).mount('#app')
