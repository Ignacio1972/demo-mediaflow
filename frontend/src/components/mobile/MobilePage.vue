<template>
  <div class="mobile-page min-h-screen bg-base-100">
    <!-- Mobile Playroom Interface -->
    <MobilePlayroom />
  </div>
</template>

<script setup lang="ts">
import MobilePlayroom from '@/components/settings/playroom/mobile/MobilePlayroom.vue'
</script>

<style scoped>
.mobile-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
