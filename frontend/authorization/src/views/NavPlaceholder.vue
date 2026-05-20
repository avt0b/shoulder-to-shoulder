<template>
  <div class="placeholder-page">
    <main class="placeholder-content">
      <span class="material-symbols placeholder-icon">{{ icon }}</span>
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
    </main>

    <nav class="bottom-nav">
      <router-link to="/map" class="nav-item" :class="{ 'nav-item-active': $route.path === '/map' }">
        <span class="material-symbols" :data-filled="$route.path === '/map'">map</span>
        <span class="nav-label">Map</span>
      </router-link>
      <router-link to="/groups" class="nav-item" :class="{ 'nav-item-active': $route.path === '/groups' }">
        <span class="material-symbols" :data-filled="$route.path === '/groups'">group</span>
        <span class="nav-label">Groups</span>
      </router-link>
      <router-link to="/routes" class="nav-item" :class="{ 'nav-item-active': $route.path === '/routes' }">
        <span class="material-symbols" :data-filled="$route.path === '/routes'">directions_run</span>
        <span class="nav-label">Routes</span>
      </router-link>
      <router-link to="/profile" class="nav-item" :class="{ 'nav-item-active': $route.path === '/profile' }">
        <span class="material-symbols" :data-filled="$route.path === '/profile'">person</span>
        <span class="nav-label">Profile</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    required: true,
  },
});
</script>

<style scoped>
.placeholder-page {
  min-height: 100vh;
  background: #f8f4f1;
  color: #191c1d;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  padding-bottom: 96px;
}

.placeholder-content {
  min-height: calc(100vh - 96px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 32px 24px;
  text-align: center;
}

.placeholder-icon {
  font-size: 52px;
  color: #c2410c;
}

.placeholder-content h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.15;
}

.placeholder-content p {
  max-width: 320px;
  margin: 0;
  color: #59413a;
  font-size: 15px;
  line-height: 1.45;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 12px 24px max(24px, env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.04);
  z-index: 50;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: #59413a;
  padding: 8px;
  border-radius: 9999px;
  cursor: pointer;
  transition: background 0.15s;
  min-width: 56px;
  text-decoration: none;
}

.nav-item:hover {
  background: #f3f4f5;
}

.nav-label {
  font-size: 11px;
  font-weight: 500;
  margin-top: 2px;
}

.nav-item-active {
  background: #c2410c !important;
  color: #ffffff !important;
  padding: 6px 20px;
}

.nav-item-active:hover {
  background: #c2410c !important;
}

.material-symbols {
  font-family: 'Material Symbols Outlined';
  display: inline-block;
  line-height: 1;
  text-transform: none;
  letter-spacing: normal;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  font-variation-settings: 'FILL' 0, 'wght' 500, 'GRAD' 0, 'opsz' 24;
}

.material-symbols[data-filled='true'] {
  font-variation-settings: 'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24;
}

@media (max-width: 420px) {
  .bottom-nav {
    gap: 8px;
    padding-left: 10px;
    padding-right: 10px;
  }

  .nav-item {
    min-width: 52px;
  }

  .nav-item-active {
    padding-left: 14px;
    padding-right: 14px;
  }
}
</style>
