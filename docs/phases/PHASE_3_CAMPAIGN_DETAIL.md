# Fase 3: Campaign Detail - Layout y Paneles

**Estado**: COMPLETADA (2025-12-21)
**Dependencias**: Fase 2 (CampaignList funcional)
**Enfoque**: Layout estructural + paneles colapsables

---

## Objetivo

Crear la estructura base de CampaignDetail con:
- Header con navegacion y nombre de campaña
- Layout 3:2 (columna izquierda + columna derecha)
- Panel colapsable de Entrenamiento IA
- Panel colapsable de Mensajes Recientes
- State machine basica para el workflow

**Esta fase NO implementa**: Generacion de sugerencias ni TTS (Fase 4)

---

## Diseño Visual de Referencia

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Campañas                         🎵 Navidad                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─── COLUMNA IZQUIERDA (flex-[3]) ─────────┐ ┌─ COLUMNA DERECHA (flex-[2])┐
│  │                                          │ │                            │
│  │  [Card: Crear Nuevo Anuncio]             │ │  ▼ 🧠 ENTRENAMIENTO IA     │
│  │  ┌────────────────────────────────────┐  │ │  ┌────────────────────┐    │
│  │  │ [textarea]                         │  │ │  │ [textarea]         │    │
│  │  │                                    │  │ │  └────────────────────┘    │
│  │  │                [Pedir Sugerencia]  │  │ │  [Guardar]                 │
│  │  └────────────────────────────────────┘  │ ├────────────────────────────┤
│  │                                          │ │  ▶ 📋 MENSAJES RECIENTES   │
│  │  [Card: Placeholder sugerencias]         │ │    (colapsado)             │
│  │                                          │ │                            │
│  └──────────────────────────────────────────┘ └────────────────────────────┘
│                                                                             │
│  ┌─ 📚 AUDIOS DE ESTA CAMPAÑA (0) ─────────────────────────────────────────┐│
│  │                              [Fase 5]                                   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Archivos Creados

| Archivo | Lineas | Descripcion |
|---------|--------|-------------|
| `composables/useCampaignWorkflow.ts` | 98 | State machine del workflow |
| `components/AITrainingPanel.vue` | 79 | Panel entrenamiento IA |
| `components/RecentMessagesPanel.vue` | 135 | Panel mensajes recientes |
| `CampaignDetail.vue` | 173 | Layout principal (reemplazo) |
| **Total** | **485** | |

---

## Implementacion Real

### useCampaignWorkflow.ts

```typescript
import { ref, computed } from 'vue'

export type WorkflowStep = 'input' | 'suggestions' | 'generate' | 'preview'

export function useCampaignWorkflow() {
  const currentStep = ref<WorkflowStep>('input')
  const inputText = ref('')
  const suggestions = ref<string[]>([])
  const selectedSuggestion = ref('')
  const editedText = ref('')
  const generatedAudioUrl = ref('')
  const generatedAudioId = ref<number | null>(null)
  const isGeneratingSuggestions = ref(false)
  const isGeneratingAudio = ref(false)

  // Acciones stub para Fase 4
  async function requestSuggestions(_campaignId: string) { /* TODO */ }
  async function generateAudio(_voiceId: string, _musicFile: string | null) { /* TODO */ }
  // ...

  return { /* ... */ }
}

// IMPORTANTE: Export del tipo para provide/inject con TypeScript
export type CampaignWorkflow = ReturnType<typeof useCampaignWorkflow>
```

### CollapsiblePanel

**El componente ya existe** en `shared/ui/CollapsiblePanel.vue`.

Props disponibles:
- `title: string` - Titulo del panel
- `icon?: string` - Icono (se concatena al titulo)
- `preview?: string` - Texto preview cuando esta colapsado
- `defaultExpanded?: boolean` - Estado inicial

```vue
<!-- Uso correcto -->
<CollapsiblePanel
  title="Entrenamiento IA"
  icon="🧠"
  :preview="previewText"
  :default-expanded="true"
>
  <slot />
</CollapsiblePanel>
```

### RecentMessagesPanel - Correcciones Importantes

**Error en documentacion original**: El codigo mostraba `response.data.audios`.

**Codigo correcto**:
```typescript
import type { CampaignAudio, CampaignAudiosResponse } from '@/types/campaign'
import { apiClient } from '@/api/client'

// apiClient YA devuelve data, NO usar .data
const response = await apiClient.get<CampaignAudiosResponse>(
  `/api/v1/campaigns/${props.campaignId}/audios`,
  { params: { limit: 5 } }
)
messages.value = response.audios  // ✅ Correcto (NO response.data.audios)
```

**Tipo correcto**: `CampaignAudio` (de `@/types/campaign`), NO `AudioMessage`.

**Cleanup requerido**:
```typescript
onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
})
```

### CampaignDetail - Provide/Inject Tipado

```typescript
import type { CampaignWorkflow } from './composables/useCampaignWorkflow'
import type { CampaignAudio } from '@/types/campaign'

const workflow = useCampaignWorkflow()
provide<CampaignWorkflow>('workflow', workflow)

function handleSelectRecentMessage(message: CampaignAudio) {
  workflow.editedText.value = message.original_text
  workflow.goToStep('generate')
}
```

---

## Estructura de Archivos Resultante

```
frontend/src/components/campaigns/
├── CampaignList.vue                      # Fase 2 (no tocar)
├── CampaignDetail.vue                    # 173 lineas
├── components/
│   ├── CampaignCard.vue                  # Fase 2 (no tocar)
│   ├── AITrainingPanel.vue               # 79 lineas
│   └── RecentMessagesPanel.vue           # 135 lineas
├── modals/
│   └── NewCampaignModal.vue              # Fase 2 (no tocar)
├── composables/
│   └── useCampaignWorkflow.ts            # 98 lineas
└── stores/
    └── campaignStore.ts                  # Fase 2 (no tocar)
```

---

## Verificacion Completada

### Funcional
- [x] Click en campaña navega a /campaigns/:id
- [x] Header muestra "← Campañas" + icono + nombre
- [x] Layout flex-[3] / flex-[2] visible
- [x] AITrainingPanel se expande/colapsa
- [x] AITrainingPanel guarda instrucciones
- [x] RecentMessagesPanel se expande/colapsa
- [x] RecentMessagesPanel carga audios (endpoint funciona)
- [x] Click en mensaje reciente cambia workflow step
- [x] Workflow state machine funciona

### No-Regresion
- [x] CampaignList sigue funcionando
- [x] Dashboard sigue funcionando
- [x] npm run build pasa
- [x] TypeScript sin errores

---

## Consejos para el Desarrollador de Fase 4

### 1. El workflow ya tiene la estructura base

El composable `useCampaignWorkflow.ts` ya tiene:
- Estados: `currentStep`, `inputText`, `editedText`, etc.
- Loading: `isGeneratingSuggestions`, `isGeneratingAudio`
- Computed: `canRequestSuggestions`, `canGenerateAudio`, `isOnStep`
- Acciones stub: `requestSuggestions()`, `generateAudio()`

Solo necesitas **implementar el cuerpo** de las funciones stub.

### 2. La Fase 4 sugiere cambiar la firma del composable

La documentacion de Fase 4 cambia:
```typescript
// Fase 3 (actual)
export function useCampaignWorkflow()

// Fase 4 (propuesto)
export function useCampaignWorkflow(campaignId: string)
```

Esto romperia CampaignDetail.vue que ya esta implementado. Considera:
- Opcion A: Pasar `campaignId` como parametro a `requestSuggestions()`
- Opcion B: Modificar CampaignDetail para pasar campaignId al composable

### 3. Shared components listos para usar

Ya existen en `components/shared/audio/`:
- `VoiceSelectorBase.vue`
- `MusicSelectorBase.vue`
- `AudioPlayerBase.vue`

Verifica sus props antes de usarlos:
```bash
cat frontend/src/components/shared/audio/VoiceSelectorBase.vue
```

### 4. apiClient devuelve data directamente

**CRITICO**: Recuerda que `apiClient.get/post/patch` devuelve `response.data` automaticamente.

```typescript
// ❌ INCORRECTO
const response = await apiClient.post('/ai/generate', data)
suggestions.value = response.data.suggestions

// ✅ CORRECTO
const response = await apiClient.post('/ai/generate', data)
suggestions.value = response.suggestions
```

Ver `frontend/src/api/client.ts:71-74` para confirmar.

### 5. El endpoint de AI ya existe

`/api/v1/ai/generate` acepta:
```typescript
interface AIGenerateRequest {
  context: string
  category?: string      // campaign_id aqui
  tone?: string
  duration?: number
  keywords?: string[]
  temperature?: number
  mode?: 'normal' | 'automatic'
  word_limit?: [number, number]
}
```

Ver `backend/app/api/v1/endpoints/ai.py` y `frontend/src/types/audio.ts`.

### 6. El store de audio ya existe

```typescript
import { useAudioStore } from '@/stores/audio'

const audioStore = useAudioStore()
await audioStore.loadVoices()
await audioStore.loadMusicTracks()
const result = await audioStore.generateAudio({ text, voice_id, ... })
```

### 7. Orden sugerido para Fase 4

1. Actualizar `useCampaignWorkflow.ts` con implementacion real
2. Crear `steps/StepInput.vue`
3. Crear `steps/StepSuggestions.vue`
4. Crear `steps/StepGenerate.vue`
5. Crear `steps/StepPreview.vue`
6. Actualizar `CampaignDetail.vue` para usar componentes dinamicos

### 8. Prueba despues de cada componente

```bash
npm run build
```

Y navega a `/campaigns/musica` para verificar visualmente.

---

**Siguiente fase**: `PHASE_4_WORKFLOW.md` - Implementacion completa de steps y generacion
