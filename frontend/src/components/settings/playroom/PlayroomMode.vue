<template>
  <div class="playroom-container min-h-screen bg-base-100">
    <!-- Navigation Bar -->
    <SettingsNav />

    <!-- Mobile Playroom Interface -->
    <MobilePlayroom />
  </div>
</template>

<script setup lang="ts">
import SettingsNav from '../SettingsNav.vue'
import MobilePlayroom from './mobile/MobilePlayroom.vue'
</script>

<style scoped>
.playroom-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
