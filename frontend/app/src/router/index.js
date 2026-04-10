import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '../stores/auth'

// Auth views
import WelcomeScreen from '../views/WelcomeScreen.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// App views
import MainPage from '../components/MainPage.vue'
import MapLight from '../components/MapLight.vue'
import EventsPage from '../components/EventsPage.vue'
import Profile from '../views/Profile.vue'
import Rating from '../views/Rating.vue'

const routes = [
  // Auth routes
  { path: '/welcome', name: 'Welcome', component: WelcomeScreen, meta: { guest: true } },
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },

  // Main app routes (требуют авторизации)
  { path: '/', name: 'Home', component: MainPage, meta: { requiresAuth: true } },
  { path: '/map', name: 'Map', component: MapLight, meta: { requiresAuth: true } },
  { path: '/events', name: 'Events', component: EventsPage, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/rating', name: 'Rating', component: Rating, meta: { requiresAuth: true } },

  // Catch-all — редирект на профиль (если авторизован) или welcome
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Guard: проверяем авторизацию
router.beforeEach((to, from, next) => {
  const authenticated = isLoggedIn()

  // Если маршрут требует авторизацию
  if (to.meta.requiresAuth) {
    if (!authenticated) {
      // Перенаправляем на логин или welcome
      const visited = localStorage.getItem('app_visited')
      next(visited ? '/login' : '/welcome')
    } else {
      next()
    }
  }
  // Если маршрут для гостей (login/register/welcome)
  else if (to.meta.guest) {
    if (authenticated) {
      next('/profile')
    } else {
      next()
    }
  }
  // Catch-all редирект
  else if (to.path === '/' || to.path === '') {
    next(authenticated ? '/profile' : (localStorage.getItem('app_visited') ? '/login' : '/welcome'))
  }
  else {
    next()
  }
})

export default router
