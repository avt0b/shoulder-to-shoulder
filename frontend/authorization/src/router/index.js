import { createRouter, createWebHistory } from 'vue-router';
import WelcomeScreen from '../views/WelcomeScreen.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import ForgotPassword from '../views/ForgotPassword.vue';
import Profile from '../views/Profile.vue';
import Map from '../views/Map.vue';

const routes = [
  { path: '/', name: 'Welcome', component: WelcomeScreen },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/map', name: 'Map', component: Map },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
