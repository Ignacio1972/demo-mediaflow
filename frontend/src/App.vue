<template>
  <PasswordGate />
  <div class="min-h-screen bg-base-100">
    <NavigationHeader />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import NavigationHeader from '@/components/common/NavigationHeader.vue'
import PasswordGate from '@/components/PasswordGate.vue'

onMounted(() => {
  console.log('🚀 MediaFlowDemo v2.1 Frontend Started')
})
</script>

<style scoped>
/* App-specific styles */
</style>
