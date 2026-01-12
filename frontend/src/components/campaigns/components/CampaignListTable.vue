<template>
  <div class="overflow-x-auto">
    <table class="table table-zebra w-full">
      <thead>
        <tr>
          <th class="w-16"></th>
          <th>Nombre</th>
          <th class="w-32 text-center">Audios</th>
          <th class="w-40 hidden md:table-cell">Creada</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="campaign in campaigns"
          :key="campaign.id"
          class="hover cursor-pointer transition-colors"
          @click="emit('click', campaign)"
        >
          <!-- Icon -->
          <td>
            <div class="flex items-center justify-center w-10 h-10 bg-base-200 rounded-xl">
              <DynamicIcon
                :name="campaign.icon"
                fallback="Folder"
                class="w-5 h-5"
              />
            </div>
          </td>

          <!-- Name -->
          <td>
            <span class="font-medium">{{ campaign.name }}</span>
          </td>

          <!-- Audio Count -->
          <td class="text-center">
            <span class="badge badge-ghost">
              {{ campaign.audio_count }}
            </span>
          </td>

          <!-- Created Date -->
          <td class="text-sm text-base-content/70 hidden md:table-cell">
            {{ formatDate(campaign.created_at) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { Campaign } from '@/types/campaign'
import DynamicIcon from '@/components/shared/ui/DynamicIcon.vue'

defineProps<{
  campaigns: Campaign[]
}>()

const emit = defineEmits<{
  'click': [campaign: Campaign]
}>()

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}
</script>
