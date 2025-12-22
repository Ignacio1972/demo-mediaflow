<script setup lang="ts">
import type { Campaign } from '@/types/campaign'

interface Props {
  campaign: Campaign
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [campaign: Campaign]
}>()

function handleClick() {
  emit('click', props.campaign)
}
</script>

<template>
  <div
    class="card bg-base-200 cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-lg"
    :style="campaign.color ? { borderTopColor: campaign.color, borderTopWidth: '4px' } : {}"
    @click="handleClick"
  >
    <div class="card-body items-center text-center p-6">
      <!-- Large icon -->
      <div class="text-5xl mb-2">
        {{ campaign.icon || '📁' }}
      </div>

      <!-- Name -->
      <h3 class="card-title text-lg">
        {{ campaign.name }}
      </h3>

      <!-- Audio count -->
      <p class="text-sm opacity-70">
        {{ campaign.audio_count }} {{ campaign.audio_count === 1 ? 'audio' : 'audios' }}
      </p>

      <!-- AI training indicator -->
      <div class="mt-2">
        <span
          v-if="campaign.has_ai_training"
          class="badge badge-success badge-sm gap-1"
        >
          <span class="text-xs">IA</span> ✓
        </span>
        <span
          v-else
          class="badge badge-ghost badge-sm gap-1 opacity-50"
        >
          <span class="text-xs">IA</span> ✗
        </span>
      </div>
    </div>
  </div>
</template>
