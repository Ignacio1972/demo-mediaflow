<template>
  <div class="min-h-screen bg-base-100">
    <SettingsNav />
    <div class="p-6">
      <div class="container mx-auto max-w-7xl">
        <MusicManager />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import MusicManager from './music/MusicManager.vue'
import SettingsNav from './SettingsNav.vue'
</script>
