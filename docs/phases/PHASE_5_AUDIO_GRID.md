# Fase 5: Audio Grid y Finalizacion

**Estado**: COMPLETADA (2025-12-22)
**Dependencias**: Fase 4 (Workflow completo)
**Enfoque**: Integracion final y testing

---

## Objetivo

Completar el modulo Campaign Manager con:
1. Grid de audios de la campana
2. Card de audio con acciones
3. Integracion completa del flujo
4. Testing E2E

---

## Cambios en Backend

### Agregar audio_url al schema

**Archivo**: `backend/app/schemas/campaign.py`

Se agrego `audio_url: str` a `CampaignAudioResponse` para permitir reproduccion directa.

### Agregar audio_url al serializer + filtrar deleted

**Archivo**: `backend/app/api/v1/endpoints/campaigns.py`

```python
def serialize_audio(audio: AudioMessage) -> CampaignAudioResponse:
    return CampaignAudioResponse(
        # ... otros campos ...
        audio_url=f"/storage/audio/{audio.filename}",  # NUEVO
        created_at=audio.created_at
    )
```

El endpoint `GET /campaigns/{id}/audios` ahora filtra `status != 'deleted'`:

```python
query = (
    select(AudioMessage)
    .filter(
        AudioMessage.category_id == campaign_id,
        AudioMessage.status != "deleted"  # Excluir eliminados
    )
    .order_by(AudioMessage.created_at.desc())
)
```

### Agregar audio_url al tipo frontend

**Archivo**: `frontend/src/types/campaign.ts`

```typescript
export interface CampaignAudio {
  // ... otros campos ...
  audio_url: string  // NUEVO
  created_at: string | null
}
```

---

## Diseno Visual de Referencia

```
+- AUDIOS DE ESTA CAMPANA (15) ----------------------------------------+
|                                                                       |
|  +------------------+ +------------------+ +------------------+       |
|  | [>]              | | [>]              | | [>]              |       |
|  | Asado Premium    | | Vinos Reserva    | | Empanadas        |       |
|  |                  | |                  | |                  |       |
|  | "Este 18..."     | | "Celebra con..." | | "Las mejores..." |       |
|  |                  | |                  | |                  |       |
|  | 🎤 Juan Carlos   | | 🎤 Maria Elena   | | 🎤 Juan Carlos   |       |
|  | 14s . 🎵         | | 12s . 🎵         | | 10s              |       |
|  |                  | |                  | |                  |       |
|  | [📅] [📤] [🗑️]    | | [📅] [📤] [🗑️]    | | [📅] [📤] [🗑️]    |       |
|  +------------------+ +------------------+ +------------------+       |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## Implementacion Real

### CampaignAudioCard.vue (108 lineas)

**Archivo**: `frontend/src/components/campaigns/components/CampaignAudioCard.vue`

Puntos clave:

```vue
<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import type { CampaignAudio } from '@/types/campaign'  // NO AudioMessage

interface Props {
  audio: CampaignAudio  // Tipo correcto
}

// Cleanup on unmount (importante para evitar memory leaks)
onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
})
</script>
```

### CampaignAudioGrid.vue (156 lineas)

**Archivo**: `frontend/src/components/campaigns/components/CampaignAudioGrid.vue`

Puntos clave:

```vue
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'  // computed en el mismo script
import { apiClient } from '@/api/client'
import type { CampaignAudio, CampaignAudiosResponse } from '@/types/campaign'

// Load audios - apiClient devuelve data directamente
async function loadAudios() {
  const response = await apiClient.get<CampaignAudiosResponse>(
    `/api/v1/campaigns/${props.campaignId}/audios`,  // Con prefijo /api/v1/
    { params: { limit, offset: offset.value } }
  )
  audios.value = response.audios  // NO response.data.audios
  total.value = response.total
}

// Delete usa /api/v1/library/ (soft delete)
async function handleDelete(audio: CampaignAudio) {
  await apiClient.delete(`/api/v1/library/${audio.id}`)  // NO /api/v1/audio/
}
</script>
```

### CampaignDetail.vue - Integracion

**Archivo**: `frontend/src/components/campaigns/CampaignDetail.vue`

```vue
<script setup lang="ts">
import { ref, onMounted, provide, computed } from 'vue'
import CampaignAudioGrid from './components/CampaignAudioGrid.vue'

// Refresh trigger for audio grid
const audioGridRefreshTrigger = ref(0)

async function handleAudioSaved() {
  await store.fetchCampaign(campaignId)
  audioGridRefreshTrigger.value += 1  // Trigger grid refresh
}
</script>

<template>
  <!-- Audio Grid -->
  <div class="mt-8">
    <CampaignAudioGrid
      :campaign-id="campaignId"
      :refresh-trigger="audioGridRefreshTrigger"
    />
  </div>
</template>
```

---

## Lecciones Aprendidas

### 1. Usar CampaignAudio, NO AudioMessage

```typescript
// INCORRECTO
import type { AudioMessage } from '@/types/audio'

// CORRECTO
import type { CampaignAudio } from '@/types/campaign'
```

### 2. apiClient devuelve data directamente

```typescript
// INCORRECTO
const response = await apiClient.get('/api/v1/campaigns/...')
audios.value = response.data.audios

// CORRECTO
const response = await apiClient.get('/api/v1/campaigns/...')
audios.value = response.audios
```

### 3. Rutas API siempre con prefijo /api/v1/

```typescript
// INCORRECTO
await apiClient.get('/campaigns/...')

// CORRECTO
await apiClient.get('/api/v1/campaigns/...')
```

### 4. Endpoint DELETE es /library/, no /audio/

```typescript
// INCORRECTO (no existe)
await apiClient.delete(`/api/v1/audio/${id}`)

// CORRECTO (soft delete)
await apiClient.delete(`/api/v1/library/${id}`)
```

### 5. Imports en un solo script setup

```vue
<!-- INCORRECTO - script separado -->
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
// ...
</script>
<script lang="ts">
import { computed } from 'vue'  // NO hacer esto
</script>

<!-- CORRECTO - todo junto -->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
</script>
```

---

## Estructura de Archivos Final

```
frontend/src/components/campaigns/
├── CampaignList.vue                      # ~100 lineas
├── CampaignDetail.vue                    # ~156 lineas
├── components/
│   ├── CampaignCard.vue                  # ~60 lineas
│   ├── AITrainingPanel.vue               # ~80 lineas
│   ├── RecentMessagesPanel.vue           # ~135 lineas
│   ├── CampaignAudioGrid.vue             # ~156 lineas
│   └── CampaignAudioCard.vue             # ~108 lineas
├── steps/
│   ├── StepInput.vue                     # ~51 lineas
│   ├── StepSuggestions.vue               # ~80 lineas
│   ├── StepGenerate.vue                  # ~140 lineas
│   └── StepPreview.vue                   # ~98 lineas
├── modals/
│   └── NewCampaignModal.vue              # ~140 lineas
├── composables/
│   └── useCampaignWorkflow.ts            # ~228 lineas
└── stores/
    └── campaignStore.ts                  # ~100 lineas
```

---

## Verificacion Completada

### Funcional
- [x] Grid muestra audios de la campana
- [x] Paginacion funciona (12 por pagina)
- [x] Reproduccion directa desde card
- [x] Eliminacion con confirmacion
- [x] Refresh automatico al guardar nuevo audio
- [x] Estados de loading, error y empty
- [x] Audios eliminados no aparecen

### Build
- [x] `npm run build` pasa sin errores
- [x] Todos los archivos < 250 lineas

### No-Regresion
- [x] Dashboard sigue funcionando
- [x] Library sigue funcionando
- [x] Fases 1-4 intactas

---

## Testing E2E del Flujo Completo

```
FLUJO COMPLETO:

1. [x] Navegar a /campaigns
2. [x] Ver grid de campanas
3. [x] Crear nueva campana con "+"
4. [x] Ver campana creada en grid
5. [x] Click en campana -> detalle

6. [x] Expandir panel "Entrenamiento IA"
7. [x] Escribir instrucciones
8. [x] Guardar instrucciones

9. [x] Escribir descripcion en textarea
10. [x] Click "Pedir Sugerencia"
11. [x] Ver sugerencias generadas
12. [x] Click "Usar" en una sugerencia

13. [x] Ver texto en editor
14. [x] Seleccionar voz
15. [x] Activar toggle de musica
16. [x] Seleccionar track
17. [x] Click "Generar Audio"

18. [x] Escuchar audio generado
19. [x] Click "Guardar en Campana"
20. [x] Ver audio en grid inferior

21. [x] Reproducir audio desde grid
22. [x] Eliminar audio (confirmar)
23. [x] Ver grid actualizado

24. [x] Volver a /campaigns
25. [x] Ver contador actualizado en card
```

---

## Post-Implementacion

### Mejoras Futuras (No MVP)

1. **Sistema de Sucursales**
   - Modelo Branch
   - CRUD de sucursales
   - Modal SendToSpeakers funcional

2. **Programacion Real**
   - Modal Schedule funcional
   - Integracion con Calendar

3. **Estadisticas de Campana**
   - Dashboard de metricas
   - Audios enviados vs programados

4. **Templates de Campana**
   - Copiar campana del ano anterior
   - Templates predefinidos

---

**Fin del Plan de Implementacion**

El Campaign Manager esta completo y funcional. Todas las fases fueron implementadas y testeadas.
