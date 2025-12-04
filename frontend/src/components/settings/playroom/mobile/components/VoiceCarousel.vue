<template>
  <div class="voice-carousel h-full flex flex-col">
    <!-- Title -->
    <div class="text-center py-4">
      <h1 class="text-2xl font-bold text-base-content">
        ¿Qué quieres anunciar?
      </h1>
      <p class="text-sm text-base-content/60 mt-1">
        Desliza para elegir un locutor
      </p>
    </div>

    <!-- Swiper Carousel -->
    <div class="flex-1 relative">
      <Swiper
        :modules="modules"
        :slides-per-view="1"
        :space-between="0"
        :centered-slides="true"
        :pagination="{ clickable: true }"
        :initial-slide="selectedIndex"
        class="h-full"
        @slideChange="onSlideChange"
        @swiper="onSwiper"
      >
        <SwiperSlide
          v-for="(profile, index) in profiles"
          :key="profile.id"
          v-slot="{ isActive }"
        >
          <div
            class="slide-content h-full flex flex-col items-center justify-center p-6 cursor-pointer"
            :class="{ 'opacity-50 scale-95': !isActive }"
            @click="onProfileTap(index)"
          >
            <!-- Profile Avatar -->
            <div
              class="avatar-container relative mb-6"
              :style="{ '--profile-color': profile.color }"
            >
              <!-- Photo or Placeholder -->
              <div
                class="w-48 h-48 sm:w-56 sm:h-56 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 overflow-hidden"
                :class="{ 'ring-4 ring-white ring-offset-4 ring-offset-base-100 scale-105': isActive }"
              >
                <img
                  v-if="profile.photoPath"
                  :src="profile.photoPath"
                  :alt="profile.name"
                  class="w-full h-full object-cover"
                />
                <div
                  v-else
                  class="w-full h-full flex items-center justify-center text-white text-6xl sm:text-7xl font-bold"
                  :style="{ backgroundColor: profile.color }"
                >
                  {{ profile.initials }}
                </div>
              </div>

              <!-- Music indicator badge (clickable) -->
              <button
                @click.stop="onMusicBadgeClick(index)"
                class="absolute -bottom-2 -right-2 rounded-full p-2 shadow-lg transition-all duration-200 hover:scale-110 active:scale-95"
                :class="profile.hasMusic && profile.defaultMusicFile ? 'bg-secondary text-secondary-content' : 'bg-base-300 text-base-content/60'"
                :title="profile.hasMusic && profile.defaultMusicFile ? 'Con música' : 'Sin música'"
              >
                <svg v-if="profile.hasMusic && profile.defaultMusicFile" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                </svg>
              </button>
            </div>

            <!-- Profile Info -->
            <div class="text-center">
              <h2 class="text-3xl font-bold text-base-content">
                {{ profile.name }}
              </h2>
              <p class="text-lg text-base-content/70 mt-1">
                {{ profile.type }}
              </p>
            </div>
          </div>
        </SwiperSlide>
      </Swiper>
    </div>

    <!-- CTA Button -->
    <div class="p-6 pb-8">
      <button
        @click="onStartRecording"
        class="btn btn-primary btn-lg w-full gap-3 text-lg animate-pulse"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
        TAP PARA GRABAR
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Pagination } from 'swiper/modules'
import type { Swiper as SwiperType } from 'swiper'
import type { VoiceProfile } from '../../composables/useMobilePlayroom'

// Import Swiper styles
import 'swiper/css'
import 'swiper/css/pagination'

// Props
interface Props {
  profiles: VoiceProfile[]
  selectedIndex: number
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'select', index: number): void
  (e: 'startRecording'): void
  (e: 'openMusicSelector', index: number): void
}>()

// Swiper modules
const modules = [Pagination]

// Swiper instance
const swiperInstance = ref<SwiperType | null>(null)

const onSwiper = (swiper: SwiperType) => {
  swiperInstance.value = swiper
}

const onSlideChange = () => {
  if (swiperInstance.value) {
    emit('select', swiperInstance.value.activeIndex)
  }
}

const onProfileTap = (index: number) => {
  // If tapping the current slide, start recording
  if (index === props.selectedIndex) {
    emit('startRecording')
  } else {
    // Otherwise, slide to that profile
    swiperInstance.value?.slideTo(index)
  }
}

const onStartRecording = () => {
  emit('startRecording')
}

const onMusicBadgeClick = (index: number) => {
  // First select this profile if not already selected
  if (index !== props.selectedIndex) {
    swiperInstance.value?.slideTo(index)
  }
  // Emit event to open music selector modal
  emit('openMusicSelector', index)
}
</script>

<style scoped>
.voice-carousel {
  background: linear-gradient(180deg, var(--fallback-b1,oklch(var(--b1))) 0%, var(--fallback-b2,oklch(var(--b2))) 100%);
}

.avatar-container {
  transition: transform 0.3s ease;
}

.slide-content {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

/* Custom Swiper pagination */
:deep(.swiper-pagination) {
  bottom: 0 !important;
  position: relative;
  margin-top: 1rem;
}

:deep(.swiper-pagination-bullet) {
  width: 12px;
  height: 12px;
  background: oklch(var(--bc) / 0.3);
  opacity: 1;
}

:deep(.swiper-pagination-bullet-active) {
  background: oklch(var(--p));
  transform: scale(1.2);
}

/* Button animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
