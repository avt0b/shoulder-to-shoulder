import { createRouter, createWebHistory } from 'vue-router';
import WelcomeScreen from '../views/WelcomeScreen.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import ForgotPassword from '../views/ForgotPassword.vue';
import Profile from '../views/Profile.vue';
import NavPlaceholder from '../views/NavPlaceholder.vue';

const routes = [
  { path: '/', name: 'Welcome', component: WelcomeScreen },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword },
  { path: '/profile', name: 'Profile', component: Profile },
  {
    path: '/map',
    name: 'Map',
    component: NavPlaceholder,
    props: {
      icon: 'map',
      title: 'Map',
      subtitle: 'Map screen is connected. The full map experience can be mounted here next.',
    },
  },
  {
    path: '/groups',
    name: 'Groups',
    component: NavPlaceholder,
    props: {
      icon: 'group',
      title: 'Groups',
      subtitle: 'Groups navigation is now active. Group content can be wired into this route.',
    },
  },
  {
    path: '/routes',
    name: 'Routes',
    component: NavPlaceholder,
    props: {
      icon: 'directions_run',
      title: 'Routes',
      subtitle: 'Routes navigation is now active. Route planning can be mounted here next.',
    },
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
