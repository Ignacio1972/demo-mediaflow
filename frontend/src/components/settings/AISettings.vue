<template>
  <div class="min-h-screen bg-base-100">
    <SettingsNav />
    <div class="p-8">
      <div class="container mx-auto">
        <h1 class="text-3xl font-bold text-primary mb-6 flex items-center gap-3">
          <CpuChipIcon class="h-8 w-8" />
          AI Settings - Multi-Cliente
        </h1>
        <div class="alert alert-info">
          <span>Componente en desarrollo - Semana 5 del roadmap</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CpuChipIcon } from '@heroicons/vue/24/outline'
import SettingsNav from './SettingsNav.vue'
</script>
