<template>
  <nav class="bg-base-200 border-b border-base-300 shadow-sm">
    <div class="container mx-auto px-4">
      <div class="flex items-center gap-2 overflow-x-auto py-3">
        <!-- AI Settings -->
        <router-link
          to="/settings/ai"
          class="settings-nav-link"
          :class="{ 'active': isActive('/settings/ai') }"
        >
          <CpuChipIcon class="h-5 w-5" />
          <span class="hidden sm:inline">AI</span>
        </router-link>

        <!-- Voices -->
        <router-link
          to="/settings/voices"
          class="settings-nav-link"
          :class="{ 'active': isActive('/settings/voices') }"
        >
          <MicrophoneIcon class="h-5 w-5" />
          <span class="hidden sm:inline">Voices</span>
        </router-link>

        <!-- Audio -->
        <router-link
          to="/settings/audio"
          class="settings-nav-link"
          :class="{ 'active': isActive('/settings/audio') }"
        >
          <MusicalNoteIcon class="h-5 w-5" />
          <span class="hidden sm:inline">Audio</span>
        </router-link>

        <!-- Categories -->
        <router-link
          to="/settings/categories"
          class="settings-nav-link"
          :class="{ 'active': isActive('/settings/categories') }"
        >
          <FolderIcon class="h-5 w-5" />
          <span class="hidden sm:inline">Categories</span>
        </router-link>

        <!-- Automatic -->
        <router-link
          to="/settings/automatic"
          class="settings-nav-link"
          :class="{ 'active': isActive('/settings/automatic') }"
        >
          <BoltIcon class="h-5 w-5" />
          <span class="hidden sm:inline">Automatic</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  CpuChipIcon,
  MicrophoneIcon,
  MusicalNoteIcon,
  FolderIcon,
  BoltIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()

const isActive = (path: string): boolean => {
  return route.path === path
}
</script>

<style scoped>
.settings-nav-link {
  @apply flex items-center gap-2 px-4 py-2 rounded-lg;
  @apply text-base-content/70 font-medium text-sm;
  @apply transition-all duration-200;
  @apply hover:text-primary hover:bg-base-300;
  @apply whitespace-nowrap;
}

.settings-nav-link.active {
  @apply text-primary bg-base-300;
  @apply shadow-sm;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .settings-nav-link {
    @apply px-3 py-2;
  }
}
</style>
