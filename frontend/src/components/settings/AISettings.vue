<template>
  <div>
    <SettingsNav />
    <div class="max-w-7xl mx-auto mt-6">
      <h1 class="text-2xl font-bold text-base-content mb-6 flex items-center gap-3">
        <CpuChipIcon class="h-6 w-6 text-primary" />
        AI Settings - Multi-Cliente
      </h1>
      <div class="alert alert-info">
        <span>Componente en desarrollo - Semana 5 del roadmap</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CpuChipIcon } from '@heroicons/vue/24/outline'
import SettingsNav from './SettingsNav.vue'
</script>
