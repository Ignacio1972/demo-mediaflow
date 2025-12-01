import { ref, onUnmounted } from 'vue'
import type { AudioMessage } from '@/types/audio'

export function useAudioPlayer() {
  const currentMessage = ref<AudioMessage | null>(null)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)
  const audioElement = ref<HTMLAudioElement | null>(null)

  function createAudioElement() {
    if (!audioElement.value) {
      audioElement.value = new Audio()

      audioElement.value.addEventListener('play', () => {
        isPlaying.value = true
      })

      audioElement.value.addEventListener('pause', () => {
        isPlaying.value = false
      })

      audioElement.value.addEventListener('ended', () => {
        isPlaying.value = false
        currentTime.value = 0
      })

      audioElement.value.addEventListener('timeupdate', () => {
        currentTime.value = audioElement.value?.currentTime || 0
      })

      audioElement.value.addEventListener('loadedmetadata', () => {
        duration.value = audioElement.value?.duration || 0
      })

      audioElement.value.addEventListener('error', (e) => {
        console.error('[useAudioPlayer] Audio error:', e)
        isPlaying.value = false
      })
    }
    return audioElement.value
  }

  function playMessage(message: AudioMessage) {
    const audio = createAudioElement()

    // If same message, toggle play/pause
    if (currentMessage.value?.id === message.id) {
      if (isPlaying.value) {
        audio.pause()
      } else {
        audio.play()
      }
      return
    }

    // Stop current and play new
    stopPlayback()

    currentMessage.value = message
    // Use audio_url from API response (same as Dashboard RecentMessages)
    audio.src = message.audio_url || `/storage/audio/${message.filename}`
    audio.play().catch(err => {
      console.error('[useAudioPlayer] Play error:', err)
      isPlaying.value = false
    })
  }

  function stopPlayback() {
    if (audioElement.value) {
      audioElement.value.pause()
      audioElement.value.currentTime = 0
    }
    isPlaying.value = false
    currentTime.value = 0
    currentMessage.value = null
  }

  function seek(time: number) {
    if (audioElement.value) {
      audioElement.value.currentTime = time
    }
  }

  function setVolume(volume: number) {
    if (audioElement.value) {
      audioElement.value.volume = Math.max(0, Math.min(1, volume))
    }
  }

  function isMessagePlaying(messageId: number): boolean {
    return currentMessage.value?.id === messageId && isPlaying.value
  }

  function isMessageLoaded(messageId: number): boolean {
    return currentMessage.value?.id === messageId
  }

  // Cleanup on unmount
  onUnmounted(() => {
    stopPlayback()
    if (audioElement.value) {
      audioElement.value.src = ''
      audioElement.value = null
    }
  })

  return {
    currentMessage,
    isPlaying,
    currentTime,
    duration,
    playMessage,
    stopPlayback,
    seek,
    setVolume,
    isMessagePlaying,
    isMessageLoaded
  }
}
