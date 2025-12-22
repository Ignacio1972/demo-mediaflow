# Fase 4: Workflow - Steps y Generacion

**Estado**: COMPLETADA (2025-12-21)
**Dependencias**: Fase 3 (COMPLETADA - Layout con paneles)
**Complejidad**: ALTA - Integracion con AI y TTS
**Enfoque**: Dividir en componentes pequenos

---

## Resumen de Implementacion

### Archivos Creados/Modificados

| Archivo | Lineas | Descripcion |
|---------|--------|-------------|
| `steps/StepInput.vue` | 51 | Textarea + boton "Pedir Sugerencia" |
| `steps/StepSuggestions.vue` | 80 | Cards de sugerencias IA con conteo |
| `steps/StepGenerate.vue` | 140 | Selector voz + musica + generar |
| `steps/StepPreview.vue` | 98 | Reproductor + guardar en campana |
| `composables/useCampaignWorkflow.ts` | 228 | State machine completa con API |
| `CampaignDetail.vue` | 159 | Componentes dinamicos |
| **Total** | **756** | |

---

## Lecciones Aprendidas (Para Fase 5)

### 1. apiClient devuelve data directamente

```typescript
// ❌ INCORRECTO
const response = await apiClient.post('/api/v1/ai/generate', data)
suggestions.value = response.data.suggestions

// ✅ CORRECTO
const response = await apiClient.post<AIGenerateResponse>('/api/v1/ai/generate', data)
suggestions.value = response.suggestions
```

Ver `frontend/src/api/client.ts:71-74` para confirmar.

### 2. Rutas API SIEMPRE con prefijo /api/v1/

```typescript
// ❌ INCORRECTO
await apiClient.post('/ai/generate', data)
await apiClient.patch('/library/123', data)

// ✅ CORRECTO
await apiClient.post('/api/v1/ai/generate', data)
await apiClient.patch('/api/v1/library/123', data)
```

### 3. Usar CampaignWorkflow type para inject

```typescript
// ❌ INCORRECTO
const workflow = inject('workflow') as any

// ✅ CORRECTO
import type { CampaignWorkflow } from '../composables/useCampaignWorkflow'
const workflow = inject<CampaignWorkflow>('workflow')!
```

### 4. music_file debe ser undefined, no null

```typescript
// ❌ INCORRECTO (TypeScript puede quejarse)
music_file: addMusic.value ? selectedMusicFile.value : null

// ✅ CORRECTO
music_file: addMusic.value && selectedMusicFile.value ? selectedMusicFile.value : undefined
```

### 5. Endpoint de library es /{id}, no /messages/{id}

```typescript
// ❌ INCORRECTO
await apiClient.patch(`/api/v1/library/messages/${audioId}`, data)

// ✅ CORRECTO
await apiClient.patch(`/api/v1/library/${audioId}`, data)
```

### 6. El composable recibe campaignId como parametro

```typescript
// ✅ Se eligio Opcion A: pasar campaignId al composable
export function useCampaignWorkflow(campaignId: string) {
  // ...
}

// En CampaignDetail.vue:
const campaignId = route.params.id as string
const workflow = useCampaignWorkflow(campaignId)
```

---

## Diagrama del Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   STEP 1: INPUT              STEP 2: SUGGESTIONS                            │
│   ─────────────              ───────────────────                            │
│   ┌─────────────────────┐    ┌─────────────────────┐                       │
│   │ Describe que        │    │ "Este 18, tu..."    │                       │
│   │ quieres anunciar... │───▶│                     │──┐                    │
│   │                     │    │              [Usar] │  │                    │
│   └─────────────────────┘    └─────────────────────┘  │                    │
│   [Pedir Sugerencia]         ┌─────────────────────┐  │                    │
│                              │ "Preparate para..." │  │                    │
│                              │              [Usar] │  │                    │
│                              └─────────────────────┘  │                    │
│                                                       │                    │
│   STEP 3: GENERATE           STEP 4: PREVIEW         │                    │
│   ────────────────           ──────────────          │                    │
│   ┌─────────────────────┐    ┌─────────────────────┐ │                    │
│   │ [Texto editable]    │    │ AUDIO GENERADO      │ │                    │
│   │                     │◀───│                     │◀┘                    │
│   │ [voices avatars]    │    │ ▶ ━━━━━━━━ 0:14    │                       │
│   │ [music tracks]      │    │                     │                       │
│   │                     │    │ [Guardar]           │                       │
│   │ [Generar Audio]     │───▶│ [Nuevo anuncio]     │                       │
│   └─────────────────────┘    └─────────────────────┘                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementacion Real

### useCampaignWorkflow.ts (228 lineas)

Puntos clave de la implementacion:

```typescript
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import { useAudioStore } from '@/stores/audio'

export interface Suggestion {
  id: string
  text: string
  char_count: number
  word_count: number
}

export interface GeneratedAudio {
  audio_id: number
  audio_url: string
  filename: string
  duration: number
  voice_name: string
}

export function useCampaignWorkflow(campaignId: string) {
  const audioStore = useAudioStore()

  // ... refs para cada step ...

  // STEP 1 → STEP 2: Request suggestions from AI
  async function requestSuggestions() {
    const response = await apiClient.post<AIGenerateResponse>('/api/v1/ai/generate', {
      context: inputText.value,
      tone: 'profesional',
      campaign_id: campaignId  // Carga ai_instructions de la campana
    })
    suggestions.value = response.suggestions.map(s => ({
      id: s.id,
      text: s.text,
      char_count: s.char_count,
      word_count: s.word_count
    }))
  }

  // STEP 3 → STEP 4: Generate audio with TTS
  async function generateAudio() {
    const response = await audioStore.generateAudio({
      text: editedText.value,
      voice_id: selectedVoiceId.value,
      add_jingles: addMusic.value,
      music_file: addMusic.value && selectedMusicFile.value
        ? selectedMusicFile.value
        : undefined
    })
    // ...
  }

  // Save audio to campaign
  async function saveAudioToCampaign(): Promise<boolean> {
    await apiClient.patch(`/api/v1/library/${generatedAudio.value.audio_id}`, {
      category_id: campaignId,
      is_favorite: true
    })
  }

  return { /* ... */ }
}

export type CampaignWorkflow = ReturnType<typeof useCampaignWorkflow>
```

### StepInput.vue (51 lineas)

```vue
<script setup lang="ts">
import { inject } from 'vue'
import type { CampaignWorkflow } from '../composables/useCampaignWorkflow'

const workflow = inject<CampaignWorkflow>('workflow')!
</script>

<template>
  <div class="card bg-base-200">
    <div class="card-body">
      <h2 class="card-title">Crear Nuevo Anuncio</h2>
      <textarea v-model="workflow.inputText.value" ... />
      <button
        :disabled="!workflow.canRequestSuggestions.value"
        @click="workflow.requestSuggestions"
      >
        Pedir Sugerencia
      </button>
    </div>
  </div>
</template>
```

### StepGenerate.vue (140 lineas)

Usa componentes shared:

```vue
<script setup lang="ts">
import VoiceSelectorBase from '@/components/shared/audio/VoiceSelectorBase.vue'
import MusicSelectorBase from '@/components/shared/audio/MusicSelectorBase.vue'

// NO usar import con llaves para componentes Vue
// ❌ import { VoiceSelectorBase } from '@/components/shared/audio'
</script>
```

### CampaignDetail.vue (159 lineas)

Usa componentes dinamicos:

```vue
<script setup lang="ts">
import StepInput from './steps/StepInput.vue'
import StepSuggestions from './steps/StepSuggestions.vue'
import StepGenerate from './steps/StepGenerate.vue'
import StepPreview from './steps/StepPreview.vue'

const campaignId = route.params.id as string
const workflow = useCampaignWorkflow(campaignId)
provide<CampaignWorkflow>('workflow', workflow)

const currentStepComponent = computed(() => {
  switch (workflow.currentStep.value) {
    case 'input': return StepInput
    case 'suggestions': return StepSuggestions
    case 'generate': return StepGenerate
    case 'preview': return StepPreview
    default: return StepInput
  }
})
</script>

<template>
  <component :is="currentStepComponent" @saved="handleAudioSaved" />
</template>
```

---

## Estructura de Archivos Final

```
frontend/src/components/campaigns/
├── CampaignList.vue
├── CampaignDetail.vue                    # 159 lineas
├── components/
│   ├── CampaignCard.vue
│   ├── AITrainingPanel.vue
│   └── RecentMessagesPanel.vue
├── steps/                                # CREADO EN FASE 4
│   ├── StepInput.vue                     # 51 lineas
│   ├── StepSuggestions.vue               # 80 lineas
│   ├── StepGenerate.vue                  # 140 lineas
│   └── StepPreview.vue                   # 98 lineas
├── modals/
│   └── NewCampaignModal.vue
├── composables/
│   └── useCampaignWorkflow.ts            # 228 lineas
└── stores/
    └── campaignStore.ts
```

---

## Verificacion Completada

### Funcional
- [x] Step 1: Textarea + boton funciona
- [x] Step 2: Muestra sugerencias con conteo
- [x] Step 3: Selector voz + musica + generar
- [x] Step 4: Reproductor + guardar en campana
- [x] Workflow transitions funcionan
- [x] AI usa campaign_id para instrucciones

### Build
- [x] `npm run build` pasa sin errores
- [x] Todos los archivos < 250 lineas

### No-Regresion
- [x] Dashboard sigue funcionando
- [x] Library sigue funcionando

---

**Siguiente fase**: `PHASE_5_AUDIO_GRID.md` - Grid de audios y finalizacion
