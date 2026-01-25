<template>
  <div class="audio-player-view h-full flex flex-col bg-base-100 overflow-y-auto">
    <!-- Header with profile info -->
    <div class="bg-base-200 px-4 py-3 flex items-center gap-3">
      <div
        class="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold overflow-hidden"
        :style="{ backgroundColor: profile?.color || '#8B5CF6' }"
      >
        <img
          v-if="profile?.photoPath"
          :src="profile.photoPath"
          :alt="profile.name"
          class="w-full h-full object-cover"
        />
        <span v-else>{{ profile?.initials || '?' }}</span>
      </div>
      <div>
        <p class="font-semibold text-base-content">{{ profile?.name || 'Locutor' }}</p>
        <p class="text-xs text-base-content/60">{{ profile?.type || '' }}</p>
      </div>
    </div>

    <!-- Audio Player Card -->
    <div class="p-4">
      <div class="card bg-base-200 shadow-lg">
        <div class="card-body p-4">
          <!-- Progress bar -->
          <div class="w-full mb-2">
            <input
              type="range"
              :min="0"
              :max="duration || 100"
              :value="currentTime"
              @input="onSeek"
              class="range range-primary range-sm w-full"
            />
          </div>

          <!-- Time display -->
          <div class="flex justify-between text-xs text-base-content/60 mb-4">
            <span>{{ formatTime(currentTime) }}</span>
            <span>{{ formatTime(duration) }}</span>
          </div>

          <!-- Controls -->
          <div class="flex items-center justify-center gap-4">
            <!-- Rewind 10s -->
            <button
              @click="$emit('seek', Math.max(0, currentTime - 10))"
              class="btn btn-ghost btn-circle"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
              </svg>
            </button>

            <!-- Play/Pause -->
            <button
              @click="$emit('togglePlay')"
              class="btn btn-primary btn-circle btn-lg"
            >
              <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
              </svg>
            </button>

            <!-- Forward 10s -->
            <button
              @click="$emit('seek', Math.min(duration, currentTime + 10))"
              class="btn btn-ghost btn-circle"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs for Edit Options -->
    <div ref="tabsRef" class="px-4 mb-4">
      <div class="tabs tabs-boxed bg-base-200 h-12">
        <button
          class="tab flex-1 h-full text-xs leading-tight px-1"
          :class="{ 'tab-active': activeTab === 'preview' }"
          @click="$emit('update:activeTab', 'preview')"
        >
          Regenerar audio
        </button>
        <button
          class="tab flex-1 h-full text-xs leading-tight px-1"
          :class="{ 'tab-active': activeTab === 'text' }"
          @click="$emit('update:activeTab', 'text')"
        >
          Editar texto
        </button>
        <button
          class="tab flex-1 h-full text-xs leading-tight px-1"
          :class="{ 'tab-active': activeTab === 'voice' }"
          @click="$emit('update:activeTab', 'voice')"
        >
          Cambiar voz
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 px-4 pb-4">
      <!-- Regenerar Audio Tab (default) -->
      <div v-if="activeTab === 'preview'" class="flex flex-col">
        <button
          @click="$emit('regenerateNew')"
          class="btn btn-secondary btn-lg w-full gap-2 mt-4"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Regenerar con IA
        </button>

        <button
          @click="$emit('showConfirm')"
          class="btn btn-primary btn-lg w-full gap-2 mt-4"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
          </svg>
          Enviar a Parlantes
        </button>

        <button
          @click="$emit('reset')"
          class="btn btn-outline border-base-300 text-info hover:bg-info hover:text-info-content w-full mt-4"
        >
          Nuevo mensaje
        </button>
      </div>

      <!-- Text Editor Tab -->
      <div v-else-if="activeTab === 'text'" ref="textTabRef" class="flex flex-col gap-3">
        <textarea
          ref="textareaRef"
          :value="editedText"
          @input="$emit('update:editedText', ($event.target as HTMLTextAreaElement).value)"
          class="textarea textarea-bordered w-full min-h-[180px] text-xl"
          placeholder="Edita el texto aquí..."
        ></textarea>

        <button
          @click="$emit('regenerateText')"
          :disabled="!editedText?.trim()"
          class="btn btn-secondary btn-lg w-full gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
          Generar audio
        </button>

        <button
          @click="$emit('showConfirm')"
          class="btn btn-primary w-full gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
          </svg>
          Enviar a Parlantes
        </button>
      </div>

      <!-- Voice Selector Tab -->
      <div v-else-if="activeTab === 'voice'" ref="voiceTabRef" class="flex flex-col gap-3">
        <div class="text-sm font-medium text-base-content/70 mb-2">
          Toca una voz para generar:
        </div>

        <div class="space-y-2 max-h-[280px] overflow-y-auto">
          <button
            v-for="voice in voices"
            :key="voice.id"
            @click="onVoiceSelect(voice.id)"
            class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors w-full text-left"
            :class="selectedVoiceId === voice.id ? 'bg-primary/10 border border-primary' : 'bg-base-200 hover:bg-base-300'"
          >
            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center"
              :class="selectedVoiceId === voice.id ? 'border-primary bg-primary' : 'border-base-content/30'"
            >
              <div v-if="selectedVoiceId === voice.id" class="w-2 h-2 rounded-full bg-primary-content"></div>
            </div>
            <div>
              <p class="font-medium text-base-content">{{ voice.name }}</p>
              <p class="text-xs text-base-content/60">{{ getVoiceType(voice) }}</p>
            </div>
          </button>
        </div>

        <button
          @click="$emit('showConfirm')"
          class="btn btn-primary w-full gap-2 mt-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
          </svg>
          Enviar a Parlantes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { VoiceProfile } from '../../composables/useMobilePlayroom'
import type { Voice } from '@/types/audio'

// Props
interface Props {
  profile: VoiceProfile | null
  improvedText: string
  editedText: string
  isPlaying: boolean
  currentTime: number
  duration: number
  activeTab: 'preview' | 'text' | 'voice'
  voices: Voice[]
  selectedVoiceId: string | null
}

const props = defineProps<Props>()

// Refs for scroll
const tabsRef = ref<HTMLElement | null>(null)
const textTabRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const voiceTabRef = ref<HTMLElement | null>(null)

// Scroll tabs into view (scroll up)
const scrollToTabs = () => {
  if (tabsRef.value) {
    tabsRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// Watch for tab changes to scroll
watch(() => props.activeTab, async (newTab) => {
  await nextTick()

  if (newTab === 'text') {
    scrollToTabs()
    // Focus the textarea after scroll
    setTimeout(() => {
      textareaRef.value?.focus()
    }, 300)
  } else if (newTab === 'voice') {
    scrollToTabs()
  }
})

// Handle voice selection - emit to regenerate immediately
const onVoiceSelect = (voiceId: string) => {
  emit('regenerateVoice', voiceId)
}

// Helpers
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const getVoiceType = (voice: Voice): string => {
  const name = voice.name.toLowerCase()
  if (name.includes('mario')) return 'Anuncios'
  if (name.includes('juan carlos')) return 'Ofertas y Promociones'
  if (name.includes('jose') || name.includes('miguel')) return 'Jingles'
  if (name.includes('francisca')) return 'Celebraciones'
  return 'Locutor'
}

const emit = defineEmits<{
  (e: 'togglePlay'): void
  (e: 'seek', time: number): void
  (e: 'showConfirm'): void
  (e: 'reset'): void
  (e: 'regenerateText'): void
  (e: 'regenerateNew'): void
  (e: 'regenerateVoice', voiceId: string): void
  (e: 'update:activeTab', tab: 'preview' | 'text' | 'voice'): void
  (e: 'update:editedText', text: string): void
}>()

const onSeek = (event: Event) => {
  const target = event.target as HTMLInputElement
  const time = parseFloat(target.value)
  emit('seek', time)
}
</script>

<style scoped>
.audio-player-view {
  -webkit-overflow-scrolling: touch;
}

/* Custom range slider */
.range {
  --range-shdw: oklch(var(--p));
}
</style>
