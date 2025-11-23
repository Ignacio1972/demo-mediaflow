<template>
  <div class="min-h-screen bg-base-100">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  console.log('🚀 MediaFlowDemo v2.1 Frontend Started')
})
</script>

<style scoped>
/* App-specific styles */
</style>
