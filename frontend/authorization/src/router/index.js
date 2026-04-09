import { createRouter, createWebHistory } from 'vue-router';
import WelcomeScreen from '../views/WelcomeScreen.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import ForgotPassword from '../views/ForgotPassword.vue';
import Profile from '../views/Profile.vue';

const routes = [
  { path: '/', name: 'Welcome', component: WelcomeScreen },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword },
  { path: '/profile', name: 'Profile', component: Profile },
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
