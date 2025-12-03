<template>
  <div class="min-h-screen bg-base-100">
    <SettingsNav />
    <div class="p-8">
      <div class="container mx-auto">
        <h1 class="text-3xl font-bold text-primary mb-6">
          🎙️ Automatic Mode - Speech-to-Text
        </h1>
        <div class="alert alert-warning">
          <span>⚠️ Requiere HTTPS para acceso al micrófono</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SettingsNav from './SettingsNav.vue'
</script>
