<template>
  <div class="voice-editor">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="card-title text-xl">
            <span class="text-2xl">{{ genderIcon }}</span>
            {{ localVoice.name }}
          </h2>
          <div class="flex gap-2">
            <button
              v-if="!localVoice.is_default"
              class="btn btn-ghost btn-sm"
              @click="$emit('set-default', localVoice.id)"
              :disabled="isSaving"
            >
              Establecer como Default
            </button>
            <button
              class="btn btn-ghost btn-sm text-error"
              @click="$emit('delete', localVoice.id)"
              :disabled="isSaving || localVoice.is_default"
              :title="localVoice.is_default ? 'No puedes eliminar la voz por defecto' : ''"
            >
              Eliminar
            </button>
          </div>
        </div>

        <!-- Form Sections -->
        <div class="space-y-6">
          <!-- Basic Info -->
          <div class="collapse collapse-open bg-base-200 rounded-box">
            <div class="collapse-title font-semibold">
              Información Básica
            </div>
            <div class="collapse-content">
              <div class="grid md:grid-cols-2 gap-4">
                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Nombre</span>
                  </label>
                  <input
                    v-model="localVoice.name"
                    type="text"
                    class="input input-bordered"
                    placeholder="Nombre de la voz"
                  />
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">ElevenLabs ID</span>
                  </label>
                  <input
                    v-model="localVoice.elevenlabs_id"
                    type="text"
                    class="input input-bordered font-mono text-sm"
                    placeholder="ID de ElevenLabs"
                  />
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Género</span>
                  </label>
                  <select v-model="localVoice.gender" class="select select-bordered">
                    <option value="">Sin especificar</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Estado</span>
                  </label>
                  <label class="label cursor-pointer justify-start gap-3">
                    <input
                      type="checkbox"
                      v-model="localVoice.active"
                      class="toggle toggle-primary"
                    />
                    <span class="label-text">{{ localVoice.active ? 'Activa' : 'Inactiva' }}</span>
                  </label>
                </div>
              </div>

              <div class="form-control mt-4">
                <label class="label">
                  <span class="label-text">Descripción</span>
                </label>
                <textarea
                  v-model="localVoice.description"
                  class="textarea textarea-bordered h-20"
                  placeholder="Descripción opcional de la voz..."
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Voice Settings -->
          <div class="collapse collapse-open bg-base-200 rounded-box">
            <div class="collapse-title font-semibold">
              Voice Settings (ElevenLabs)
            </div>
            <div class="collapse-content">
              <div class="space-y-6">
                <!-- Style -->
                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Style (Expresividad)</span>
                    <span class="label-text-alt font-mono">{{ localVoice.style }}%</span>
                  </label>
                  <input
                    v-model.number="localVoice.style"
                    type="range"
                    min="0"
                    max="100"
                    step="1"
                    class="range range-primary"
                  />
                  <div class="flex justify-between text-xs text-base-content/50 mt-1">
                    <span>Neutro</span>
                    <span>Expresivo</span>
                  </div>
                </div>

                <!-- Stability -->
                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Stability (Consistencia)</span>
                    <span class="label-text-alt font-mono">{{ localVoice.stability }}%</span>
                  </label>
                  <input
                    v-model.number="localVoice.stability"
                    type="range"
                    min="0"
                    max="100"
                    step="1"
                    class="range range-secondary"
                  />
                  <div class="flex justify-between text-xs text-base-content/50 mt-1">
                    <span>Variable</span>
                    <span>Consistente</span>
                  </div>
                </div>

                <!-- Similarity Boost -->
                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Similarity Boost</span>
                    <span class="label-text-alt font-mono">{{ localVoice.similarity_boost }}%</span>
                  </label>
                  <input
                    v-model.number="localVoice.similarity_boost"
                    type="range"
                    min="0"
                    max="100"
                    step="1"
                    class="range range-accent"
                  />
                  <div class="flex justify-between text-xs text-base-content/50 mt-1">
                    <span>Baja similitud</span>
                    <span>Alta similitud</span>
                  </div>
                </div>

                <!-- Speaker Boost -->
                <div class="form-control">
                  <label class="label cursor-pointer justify-start gap-3">
                    <input
                      type="checkbox"
                      v-model="localVoice.use_speaker_boost"
                      class="checkbox checkbox-primary"
                    />
                    <span class="label-text">Use Speaker Boost</span>
                  </label>
                  <p class="text-xs text-base-content/50 ml-9">
                    Mejora la claridad de la voz (recomendado)
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Volume Adjustment -->
          <div class="collapse collapse-open bg-base-200 rounded-box">
            <div class="collapse-title font-semibold">
              Ajuste de Volumen
            </div>
            <div class="collapse-content">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Volume Adjustment</span>
                  <span class="label-text-alt font-mono" :class="volumeClass">
                    {{ volumeDisplay }}
                  </span>
                </label>
                <input
                  v-model.number="localVoice.volume_adjustment"
                  type="range"
                  min="-20"
                  max="20"
                  step="0.5"
                  class="range"
                  :class="volumeRangeClass"
                />
                <div class="flex justify-between text-xs text-base-content/50 mt-1">
                  <span>-20 dB</span>
                  <span class="text-base-content/70">0 dB</span>
                  <span>+20 dB</span>
                </div>
                <p class="text-xs text-base-content/50 mt-2">
                  Ajusta el volumen de salida para compensar voces más altas o bajas
                </p>
              </div>
            </div>
          </div>

          <!-- Jingle Settings -->
          <div class="collapse collapse-arrow bg-base-200 rounded-box">
            <input type="checkbox" />
            <div class="collapse-title font-semibold">
              Jingle Settings (Opcional)
            </div>
            <div class="collapse-content">
              <div class="grid md:grid-cols-2 gap-4">
                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Music Volume</span>
                    <span class="label-text-alt font-mono">{{ jingleSettings.music_volume }}x</span>
                  </label>
                  <input
                    v-model.number="jingleSettings.music_volume"
                    type="range"
                    min="0"
                    max="3"
                    step="0.05"
                    class="range range-sm"
                  />
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Voice Volume</span>
                    <span class="label-text-alt font-mono">{{ jingleSettings.voice_volume }}x</span>
                  </label>
                  <input
                    v-model.number="jingleSettings.voice_volume"
                    type="range"
                    min="0"
                    max="5"
                    step="0.1"
                    class="range range-sm"
                  />
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Duck Level</span>
                    <span class="label-text-alt font-mono">{{ Math.round(jingleSettings.duck_level * 100) }}%</span>
                  </label>
                  <input
                    v-model.number="jingleSettings.duck_level"
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    class="range range-sm"
                  />
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Intro Silence</span>
                    <span class="label-text-alt font-mono">{{ jingleSettings.intro_silence }}s</span>
                  </label>
                  <input
                    v-model.number="jingleSettings.intro_silence"
                    type="range"
                    min="0"
                    max="15"
                    step="0.5"
                    class="range range-sm"
                  />
                </div>

                <div class="form-control md:col-span-2">
                  <label class="label">
                    <span class="label-text">Outro Silence</span>
                    <span class="label-text-alt font-mono">{{ jingleSettings.outro_silence }}s</span>
                  </label>
                  <input
                    v-model.number="jingleSettings.outro_silence"
                    type="range"
                    min="0"
                    max="20"
                    step="0.5"
                    class="range range-sm"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Test Voice -->
          <div class="collapse collapse-open bg-base-200 rounded-box">
            <div class="collapse-title font-semibold">
              Probar Voz
            </div>
            <div class="collapse-content">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Texto de prueba</span>
                </label>
                <textarea
                  v-model="testText"
                  class="textarea textarea-bordered h-20"
                  placeholder="Escribe el texto que quieres probar..."
                ></textarea>
              </div>

              <div class="flex items-center gap-4 mt-4">
                <button
                  class="btn btn-primary"
                  @click="handleTest"
                  :disabled="isTesting || !testText.trim()"
                >
                  <span v-if="isTesting" class="loading loading-spinner loading-sm"></span>
                  <span v-else>🔊</span>
                  {{ isTesting ? 'Generando...' : 'Probar Voz' }}
                </button>

                <!-- Audio Player -->
                <audio
                  v-if="testAudioUrl"
                  ref="audioPlayer"
                  :src="testAudioUrl"
                  controls
                  class="flex-1 h-10"
                ></audio>
              </div>

              <p class="text-xs text-base-content/50 mt-2">
                Esto generará audio real usando ElevenLabs con los settings actuales
              </p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="card-actions justify-end mt-6 pt-4 border-t border-base-300">
          <button
            class="btn btn-ghost"
            @click="handleCancel"
            :disabled="isSaving"
          >
            Cancelar
          </button>
          <button
            class="btn btn-primary"
            @click="handleSave"
            :disabled="isSaving || !hasChanges"
          >
            <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
            {{ isSaving ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue'
import type { VoiceSettings } from '../composables/useVoiceManager'

const props = defineProps<{
  voice: VoiceSettings
  isSaving: boolean
  isTesting: boolean
}>()

const emit = defineEmits<{
  save: [voice: Partial<VoiceSettings>]
  cancel: []
  delete: [voiceId: string]
  'set-default': [voiceId: string]
  test: [text: string]
}>()

// Local copy for editing
const localVoice = ref<VoiceSettings>({ ...props.voice })

// Jingle settings (separate reactive for easier handling)
const jingleSettings = reactive({
  music_volume: props.voice.jingle_settings?.music_volume ?? 1.0,
  voice_volume: props.voice.jingle_settings?.voice_volume ?? 1.0,
  duck_level: props.voice.jingle_settings?.duck_level ?? 0.2,
  intro_silence: props.voice.jingle_settings?.intro_silence ?? 3,
  outro_silence: props.voice.jingle_settings?.outro_silence ?? 5,
})

// Test state
const testText = ref('Hola, esta es una prueba de voz con los settings actuales.')
const testAudioUrl = ref<string | null>(null)
const audioPlayer = ref<HTMLAudioElement | null>(null)

// Watch for voice changes (when selecting different voice)
watch(() => props.voice, (newVoice) => {
  localVoice.value = { ...newVoice }
  jingleSettings.music_volume = newVoice.jingle_settings?.music_volume ?? 1.0
  jingleSettings.voice_volume = newVoice.jingle_settings?.voice_volume ?? 1.0
  jingleSettings.duck_level = newVoice.jingle_settings?.duck_level ?? 0.2
  jingleSettings.intro_silence = newVoice.jingle_settings?.intro_silence ?? 3
  jingleSettings.outro_silence = newVoice.jingle_settings?.outro_silence ?? 5
  testAudioUrl.value = null
}, { deep: true })

// Computed
const genderIcon = computed(() => {
  switch (localVoice.value.gender) {
    case 'M': return '👨'
    case 'F': return '👩'
    default: return '🎙️'
  }
})

const volumeDisplay = computed(() => {
  const vol = localVoice.value.volume_adjustment || 0
  if (vol === 0) return '0 dB'
  return vol > 0 ? `+${vol} dB` : `${vol} dB`
})

const volumeClass = computed(() => {
  const vol = localVoice.value.volume_adjustment || 0
  if (vol > 0) return 'text-success'
  if (vol < 0) return 'text-error'
  return ''
})

const volumeRangeClass = computed(() => {
  const vol = localVoice.value.volume_adjustment || 0
  if (vol > 0) return 'range-success'
  if (vol < 0) return 'range-error'
  return 'range-primary'
})

const hasChanges = computed(() => {
  // Compare local with original
  const original = props.voice
  const local = localVoice.value

  return (
    local.name !== original.name ||
    local.elevenlabs_id !== original.elevenlabs_id ||
    local.gender !== original.gender ||
    local.description !== original.description ||
    local.active !== original.active ||
    local.style !== original.style ||
    local.stability !== original.stability ||
    local.similarity_boost !== original.similarity_boost ||
    local.use_speaker_boost !== original.use_speaker_boost ||
    local.volume_adjustment !== original.volume_adjustment ||
    JSON.stringify(jingleSettings) !== JSON.stringify(original.jingle_settings || {})
  )
})

// Handlers
const handleSave = () => {
  const updates: Partial<VoiceSettings> = {
    name: localVoice.value.name,
    elevenlabs_id: localVoice.value.elevenlabs_id,
    gender: localVoice.value.gender,
    description: localVoice.value.description,
    active: localVoice.value.active,
    style: localVoice.value.style,
    stability: localVoice.value.stability,
    similarity_boost: localVoice.value.similarity_boost,
    use_speaker_boost: localVoice.value.use_speaker_boost,
    volume_adjustment: localVoice.value.volume_adjustment,
    jingle_settings: { ...jingleSettings },
  }

  emit('save', updates)
}

const handleCancel = () => {
  // Reset to original
  localVoice.value = { ...props.voice }
  emit('cancel')
}

const handleTest = () => {
  emit('test', testText.value)
}

// Expose method to set test audio URL
defineExpose({
  setTestAudioUrl: (url: string) => {
    testAudioUrl.value = url
    // Auto-play when URL is set
    setTimeout(() => {
      audioPlayer.value?.play()
    }, 100)
  }
})
</script>
