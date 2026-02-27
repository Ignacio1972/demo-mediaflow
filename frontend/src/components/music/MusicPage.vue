<template>
  <div>
    <!-- Hidden Audio Element -->
    <audio
      ref="audioRef"
      :src="STREAM_URL"
      preload="none"
      @play="onPlay"
      @pause="onPause"
      @playing="onPlaying"
      @error="handleAudioError"
      @stalled="handleStalled"
      @waiting="handleWaiting"
      @timeupdate="onTimeUpdate"
    />

    <!-- Main Content -->
    <div class="max-w-lg md:max-w-xl mx-auto">
      <!-- Now Playing Card -->
      <div class="card bg-base-200 shadow-xl">
        <div class="card-body p-4 md:p-6">
          <!-- Album Art + Info -->
          <div class="flex flex-col sm:flex-row gap-4 items-center sm:items-start">
            <!-- Album Art -->
            <div class="w-32 h-32 md:w-40 md:h-40 rounded-xl flex-shrink-0 overflow-hidden bg-gradient-to-br from-primary/30 to-secondary/30">
              <img
                v-if="nowPlaying.art"
                :src="nowPlaying.art"
                :alt="nowPlaying.title"
                class="w-full h-full object-cover"
                @error="nowPlaying.art = ''"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <MusicalNoteIcon class="w-16 h-16 text-primary/50" />
              </div>
            </div>

            <!-- Track Info -->
            <div class="flex-1 text-center sm:text-left">
              <!-- Connection Status Badge -->
              <div
                class="badge badge-sm mb-2"
                :class="statusBadgeClass"
              >
                <span
                  v-if="connectionStatus === 'reconnecting'"
                  class="loading loading-dots loading-xs mr-1"
                ></span>
                {{ statusLabel }}
              </div>
              <h2 class="text-xl md:text-2xl font-bold text-base-content">
                {{ nowPlaying.title || 'Online' }}
              </h2>
              <p class="text-base-content/70 text-lg">{{ nowPlaying.artist || 'Mediaflow Radio' }}</p>
              <p v-if="nowPlaying.genre" class="text-base-content/50 text-sm mt-1">{{ nowPlaying.genre }}</p>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="mt-6">
            <div class="flex justify-between text-xs text-base-content/60 mb-2">
              <span>{{ formatTime(nowPlaying.elapsed) }}</span>
              <span>{{ formatTime(nowPlaying.duration) }}</span>
            </div>
            <div class="w-full bg-base-300 rounded-full h-2">
              <div
                class="bg-primary h-full rounded-full transition-all duration-1000"
                :style="{ width: progressPercent + '%' }"
              ></div>
            </div>
          </div>

          <!-- Controls -->
          <div class="flex items-center justify-center gap-4 mt-6">
            <!-- Play/Pause Button -->
            <button
              @click="togglePlay"
              class="btn btn-circle btn-lg btn-primary"
              :disabled="isLoading"
            >
              <span v-if="isLoading" class="loading loading-spinner"></span>
              <PauseIcon v-else-if="isPlaying" class="w-6 h-6" />
              <PlayIcon v-else class="w-6 h-6" />
            </button>
            <!-- Skip/Forward Button -->
            <button
              @click="skipSong"
              class="btn btn-circle btn-lg btn-outline"
              :disabled="isSkipping"
              title="Saltar canción"
            >
              <span v-if="isSkipping" class="loading loading-spinner"></span>
              <ForwardIcon v-else class="w-6 h-6" />
            </button>
          </div>

          <!-- Volume Control -->
          <div class="flex items-center justify-center gap-3 mt-6">
            <button @click="toggleMute" class="btn btn-ghost btn-sm btn-square">
              <SpeakerXMarkIcon v-if="isMuted || volume === 0" class="w-5 h-5 text-base-content/60" />
              <SpeakerWaveIcon v-else class="w-5 h-5 text-base-content/60" />
            </button>
            <input
              type="range"
              min="0"
              max="100"
              v-model="volume"
              @input="updateVolume"
              class="range range-primary range-sm w-48 md:w-64"
            />
            <span class="text-sm text-base-content/60 w-8">{{ volume }}%</span>
          </div>

          <!-- Rating -->
          <div class="flex items-center justify-center gap-6 mt-6 pt-4 border-t border-base-300">
            <span class="text-sm text-base-content/60">Calificar:</span>
            <button
              @click="rate('up')"
              class="btn btn-circle btn-outline btn-success hover:btn-success"
              :class="{ 'btn-success': currentRating === 'up' }"
            >
              <HandThumbUpIcon class="w-5 h-5" />
            </button>
            <button
              @click="rate('down')"
              class="btn btn-circle btn-outline btn-error hover:btn-error"
              :class="{ 'btn-error': currentRating === 'down' }"
            >
              <HandThumbDownIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Playlist Selector -->
      <div class="mt-6">
        <h3 class="text-lg font-semibold text-base-content mb-3">Playlists</h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            v-for="playlist in playlists"
            :key="playlist.id"
            @click="selectPlaylist(playlist.id)"
            class="btn btn-lg justify-start"
            :class="selectedPlaylist === playlist.id ? 'btn-primary' : 'btn-outline'"
          >
            <QueueListIcon class="w-5 h-5" />
            {{ playlist.name }}
          </button>
        </div>
      </div>

      <!-- Upcoming Tracks -->
      <div class="mt-6">
        <h3 class="text-lg font-semibold text-base-content mb-3">Próximas canciones</h3>
        <div class="card bg-base-200">
          <div class="divide-y divide-base-300">
            <div
              v-for="(track, index) in currentTracks"
              :key="index"
              class="flex items-center gap-3 p-3 hover:bg-base-300/50 transition-colors"
            >
              <!-- Index: Number, Letter, or Icon based on playlist -->
              <span v-if="selectedPlaylist === 'a'" class="text-base-content/40 text-sm w-6">{{ index + 1 }}</span>
              <span v-else-if="selectedPlaylist === 'b'" class="text-base-content/40 text-sm w-6 font-medium">{{ String.fromCharCode(65 + index) }}</span>
              <component
                v-else
                :is="trackIcons[index]"
                class="w-5 h-5 text-base-content/60 flex-shrink-0"
              />
              <div class="w-10 h-10 bg-base-300 rounded flex items-center justify-center flex-shrink-0">
                <MusicalNoteIcon class="w-5 h-5 text-base-content/30" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-base-content truncate">{{ track.title }}</p>
                <p class="text-sm text-base-content/60 truncate">{{ track.artist }}</p>
              </div>
              <span class="text-sm text-base-content/40">{{ track.duration }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, markRaw, onMounted, onUnmounted, type Component } from 'vue'
import {
  MusicalNoteIcon,
  PlayIcon,
  PauseIcon,
  ForwardIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  QueueListIcon,
  StarIcon,
  HeartIcon,
  BoltIcon,
  FireIcon
} from '@heroicons/vue/24/outline'
import apiClient from '@/api/client'

// Constants
const STREAM_URL = 'https://radio.mediaflow.cl/listen/mediaflow/radio.mp3'
const API_URL = 'https://radio.mediaflow.cl/api/nowplaying'

// Reconnection config
const RECONNECT_MAX_RETRIES = 10
const RECONNECT_BASE_DELAY = 1500
const RECONNECT_MAX_DELAY = 15000
const STALLED_THRESHOLD = 5000

// Audio element ref
const audioRef = ref<HTMLAudioElement | null>(null)

// Player state
const isPlaying = ref(false)
const isLoading = ref(false)
const isSkipping = ref(false)
const volume = ref(70)
const isMuted = ref(false)
const currentRating = ref<'up' | 'down' | null>(null)

// Connection state
type ConnectionStatus = 'idle' | 'live' | 'reconnecting' | 'disconnected'
const connectionStatus = ref<ConnectionStatus>('idle')
const reconnectAttempts = ref(0)
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let stalledTimer: ReturnType<typeof setTimeout> | null = null
let wasPlayingBeforeError = false

// Status badge
const statusLabel = computed(() => {
  switch (connectionStatus.value) {
    case 'live': return 'EN VIVO'
    case 'reconnecting': return `RECONECTANDO (${reconnectAttempts.value}/${RECONNECT_MAX_RETRIES})`
    case 'disconnected': return 'DESCONECTADO'
    default: return 'PAUSADO'
  }
})

const statusBadgeClass = computed(() => {
  switch (connectionStatus.value) {
    case 'live': return 'badge-success'
    case 'reconnecting': return 'badge-warning'
    case 'disconnected': return 'badge-error'
    default: return 'badge-ghost'
  }
})

// Now Playing data
const nowPlaying = ref({
  title: '',
  artist: '',
  album: '',
  art: '',
  genre: '',
  duration: 0,
  elapsed: 0
})

// Progress
const progressPercent = computed(() => {
  if (!nowPlaying.value.duration) return 0
  return Math.min((nowPlaying.value.elapsed / nowPlaying.value.duration) * 100, 100)
})

// Format time helper
const formatTime = (seconds: number): string => {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// --- Reconnection Logic ---

const clearReconnectTimer = () => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
}

const clearStalledTimer = () => {
  if (stalledTimer) {
    clearTimeout(stalledTimer)
    stalledTimer = null
  }
}

const resetStalledTimer = () => {
  clearStalledTimer()
  if (isPlaying.value) {
    stalledTimer = setTimeout(() => {
      console.warn('[MusicPlayer] Stream stalled (no timeupdate for 5s)')
      triggerReconnect()
    }, STALLED_THRESHOLD)
  }
}

const triggerReconnect = () => {
  if (connectionStatus.value === 'reconnecting') return
  if (connectionStatus.value === 'disconnected') return

  wasPlayingBeforeError = true
  connectionStatus.value = 'reconnecting'
  reconnect()
}

const reconnect = async () => {
  if (reconnectAttempts.value >= RECONNECT_MAX_RETRIES) {
    console.error('[MusicPlayer] Max reconnect attempts reached')
    connectionStatus.value = 'disconnected'
    isPlaying.value = false
    isLoading.value = false
    return
  }

  const audio = audioRef.value
  if (!audio) return

  reconnectAttempts.value++
  console.log(`[MusicPlayer] Reconnect attempt ${reconnectAttempts.value}/${RECONNECT_MAX_RETRIES}`)

  try {
    audio.pause()
    // Cache bust to force a new connection
    audio.src = `${STREAM_URL}?t=${Date.now()}`
    audio.load()
    await audio.play()
    // If play() resolves, the 'playing' event handler will reset state
  } catch {
    // Schedule next retry with exponential backoff
    const delay = Math.min(
      RECONNECT_BASE_DELAY * Math.pow(1.5, reconnectAttempts.value - 1),
      RECONNECT_MAX_DELAY
    )
    console.log(`[MusicPlayer] Retry in ${Math.round(delay)}ms`)
    clearReconnectTimer()
    reconnectTimer = setTimeout(reconnect, delay)
  }
}

// --- Audio Event Handlers ---

const onPlay = () => {
  isPlaying.value = true
}

const onPause = () => {
  isPlaying.value = false
  clearStalledTimer()
  if (connectionStatus.value === 'live') {
    connectionStatus.value = 'idle'
  }
}

const onPlaying = () => {
  // Stream is actively playing — connection is good
  isPlaying.value = true
  isLoading.value = false
  connectionStatus.value = 'live'
  reconnectAttempts.value = 0
  wasPlayingBeforeError = false
  clearReconnectTimer()
  resetStalledTimer()
}

const onTimeUpdate = () => {
  // Stream is receiving data — reset stalled timer
  resetStalledTimer()
}

const handleAudioError = () => {
  console.error('[MusicPlayer] Audio error')
  isLoading.value = false

  if (isPlaying.value || wasPlayingBeforeError) {
    triggerReconnect()
  }
}

const handleStalled = () => {
  console.warn('[MusicPlayer] Stream stalled event')
  if (isPlaying.value || wasPlayingBeforeError) {
    triggerReconnect()
  }
}

const handleWaiting = () => {
  // Buffer empty — give it a few seconds before considering it a real problem
  // The stalled timer will handle it if data doesn't resume
  resetStalledTimer()
}

// --- Player Controls ---

const togglePlay = async () => {
  if (!audioRef.value) return

  if (isPlaying.value) {
    audioRef.value.pause()
    wasPlayingBeforeError = false
  } else {
    // If disconnected, reset and try fresh
    if (connectionStatus.value === 'disconnected') {
      reconnectAttempts.value = 0
      audioRef.value.src = `${STREAM_URL}?t=${Date.now()}`
      audioRef.value.load()
    }

    isLoading.value = true
    try {
      await audioRef.value.play()
    } catch (error) {
      console.error('Error playing audio:', error)
      isLoading.value = false
    }
  }
}

const skipSong = async () => {
  isSkipping.value = true
  try {
    await apiClient.post('/api/v1/radio/skip')
    setTimeout(fetchNowPlaying, 1000)
  } catch (error) {
    console.error('Error skipping song:', error)
  } finally {
    isSkipping.value = false
  }
}

// Volume control
const updateVolume = () => {
  if (audioRef.value) {
    audioRef.value.volume = volume.value / 100
    isMuted.value = volume.value === 0
  }
}

const toggleMute = () => {
  if (audioRef.value) {
    if (isMuted.value) {
      audioRef.value.volume = volume.value / 100
      isMuted.value = false
    } else {
      audioRef.value.volume = 0
      isMuted.value = true
    }
  }
}

// Rating
const rate = (rating: 'up' | 'down') => {
  currentRating.value = currentRating.value === rating ? null : rating
}

// Fetch Now Playing info
const fetchNowPlaying = async () => {
  try {
    const response = await fetch(API_URL)
    const data = await response.json()

    const station = Array.isArray(data) ? data[0] : data

    if (station?.now_playing?.song) {
      const song = station.now_playing.song
      const artUrl = song.art ? song.art.replace('http://', 'https://') : ''
      nowPlaying.value = {
        title: song.title || 'Sin título',
        artist: song.artist || 'Artista desconocido',
        album: song.album || '',
        art: artUrl,
        genre: song.genre || '',
        duration: station.now_playing.duration || 0,
        elapsed: station.now_playing.elapsed || 0
      }
    }
  } catch (error) {
    console.error('Error fetching now playing:', error)
  }
}

// Polling intervals
let pollInterval: ReturnType<typeof setInterval> | null = null
let elapsedInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  if (audioRef.value) {
    audioRef.value.volume = volume.value / 100
  }

  fetchNowPlaying()
  pollInterval = setInterval(fetchNowPlaying, 10000)
  elapsedInterval = setInterval(() => {
    if (nowPlaying.value.elapsed < nowPlaying.value.duration) {
      nowPlaying.value.elapsed++
    }
  }, 1000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  if (elapsedInterval) clearInterval(elapsedInterval)
  clearReconnectTimer()
  clearStalledTimer()
  if (audioRef.value) {
    audioRef.value.pause()
  }
})

// Playlists (placeholder data)
const playlists = [
  { id: 'a', name: 'Lunes a Viernes' },
  { id: 'b', name: 'Sábado' },
  { id: 'c', name: 'Domingo' }
]

const selectedPlaylist = ref('a')

const selectPlaylist = (id: string) => {
  selectedPlaylist.value = id
}

// Icons for Playlist C
const trackIcons: Component[] = [
  markRaw(StarIcon),
  markRaw(HeartIcon),
  markRaw(BoltIcon),
  markRaw(FireIcon)
]

// Mock track data per playlist
const tracksA = [
  { title: 'Rock Clásico Mix', artist: 'Varios Artistas', duration: '3:24' },
  { title: 'Pop Hits 2024', artist: 'Top Charts', duration: '4:12' },
  { title: 'Baladas Románticas', artist: 'Colección', duration: '2:58' },
  { title: 'Éxitos del Momento', artist: 'Radio Mix', duration: '3:45' }
]

const tracksB = [
  { title: 'Jazz Lounge', artist: 'Smooth Sounds', duration: '5:10' },
  { title: 'Bossa Nova Nights', artist: 'Brazilian Vibes', duration: '4:32' },
  { title: 'Classical Piano', artist: 'Orchestra', duration: '6:15' },
  { title: 'Chill Electronic', artist: 'Ambient Mix', duration: '4:48' }
]

const tracksC = [
  { title: 'Acoustic Sessions', artist: 'Unplugged', duration: '3:55' },
  { title: 'Indie Folk', artist: 'New Artists', duration: '4:20' },
  { title: 'Alternative Rock', artist: 'Underground', duration: '3:38' },
  { title: 'Lo-Fi Beats', artist: 'Study Music', duration: '5:02' }
]

const currentTracks = computed(() => {
  switch (selectedPlaylist.value) {
    case 'b': return tracksB
    case 'c': return tracksC
    default: return tracksA
  }
})
</script>
