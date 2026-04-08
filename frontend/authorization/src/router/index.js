import { createRouter, createWebHistory } from 'vue-router';
import WelcomeScreen from '../views/WelcomeScreen.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';

const routes = [
  { path: '/', name: 'Welcome', component: WelcomeScreen },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: { template: '<div style="padding:24px;font-family:Inter,sans-serif;"><h1>Восстановление пароля</h1><p>Страница восстановления</p></div>' },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: { template: '<div style="padding:24px;font-family:Inter,sans-serif;"><h1>Профиль</h1><p>Страница профиля</p></div>' },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const visited = localStorage.getItem('app_visited');
  if (to.path === '/' && visited) {
    next('/login');
  } else {
    next();
  }
});

export default router;
