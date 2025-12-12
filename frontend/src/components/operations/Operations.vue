<template>
  <div class="operations min-h-screen bg-base-100">
    <!-- Navigation -->
    <OperationsNav />

    <!-- Content -->
    <div class="container mx-auto p-6">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import OperationsNav from './OperationsNav.vue'
</script>
