# Fase 0: Preparación - Extracción de Componentes Compartidos

**Estado**: ✅ Completado (2025-12-21)
**Prioridad**: CRÍTICA
**Principio**: NO ROMPER DASHBOARD

---

## Objetivo

Extraer componentes base reutilizables a `shared/` **sin modificar el comportamiento** del Dashboard ni ningún otro módulo existente.

---

## Regla de Oro

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ANTES de cada cambio, ejecutar:                               │
│   $ npm run dev                                                 │
│   → Verificar Dashboard funciona                                │
│                                                                 │
│   DESPUÉS de cada cambio, ejecutar:                             │
│   $ npm run dev                                                 │
│   → Verificar Dashboard SIGUE funcionando idéntico              │
│                                                                 │
│   Si algo se rompe → REVERTIR inmediatamente                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tareas

### Tarea 0.1: Crear estructura shared/

```bash
mkdir -p frontend/src/components/shared/audio
mkdir -p frontend/src/components/shared/ui
```

Archivos a crear:
- `shared/audio/index.ts` (exports)
- `shared/ui/index.ts` (exports)

---

### Tarea 0.2: Crear CollapsiblePanel.vue (NUEVO)

Este componente NO existe, se crea desde cero. No hay riesgo de romper nada.

**Ubicación**: `frontend/src/components/shared/ui/CollapsiblePanel.vue`

**Props**:
```typescript
interface Props {
  title: string           // "🧠 Entrenamiento IA"
  icon?: string           // Emoji opcional
  defaultExpanded?: boolean
  preview?: string        // Texto truncado cuando colapsado
}
```

**Slots**:
- `default` - Contenido cuando expandido
- `header-actions` - Botones en el header (opcional)

**Comportamiento**:
- Click en header → toggle expanded
- Transición suave (300ms)
- Indicador ▶/▼ según estado

**Tamaño objetivo**: ~80 líneas

---

### Tarea 0.3: Analizar VoiceSelector actual

**Ubicación actual**: `frontend/src/components/dashboard/VoiceSelector.vue`

**Antes de extraer**:
1. Leer el componente completo
2. Identificar qué es específico de Dashboard
3. Identificar qué es reutilizable

**Patrón de extracción**:
```
VoiceSelector.vue (Dashboard)
       │
       ├── Lógica de avatares        → VoiceSelectorBase.vue (shared)
       ├── Selección por índice      → VoiceSelectorBase.vue (shared)
       ├── Emit de voz seleccionada  → VoiceSelectorBase.vue (shared)
       │
       └── Integración con store     → Se queda en Dashboard
```

**Estrategia SEGURA**:
1. Crear VoiceSelectorBase.vue como COPIA
2. Verificar que la copia funciona independiente
3. OPCIONAL: Refactorizar Dashboard para usar Base (solo si hay tiempo)
4. Si no se refactoriza Dashboard, no pasa nada - Campaigns usa Base

---

### Tarea 0.4: Crear VoiceSelectorBase.vue

**Ubicación**: `frontend/src/components/shared/audio/VoiceSelectorBase.vue`

**Este componente debe ser**:
- Independiente del store (recibe voices como prop)
- Sin dependencias de Dashboard
- Emite eventos para que el padre maneje la selección

**Props**:
```typescript
interface Props {
  voices: Voice[]              // Lista de voces
  selectedVoiceId?: string     // Voz seleccionada
  showAvatars?: boolean        // Mostrar fotos (default: true)
  size?: 'sm' | 'md' | 'lg'    // Tamaño de avatares
}
```

**Emits**:
```typescript
const emit = defineEmits<{
  'select': [voiceId: string]
  'update:selectedVoiceId': [voiceId: string]
}>()
```

**Tamaño objetivo**: ~120 líneas

---

### Tarea 0.5: Crear MusicSelectorBase.vue

**Ubicación**: `frontend/src/components/shared/audio/MusicSelectorBase.vue`

**Referencia**: Extraer de `MessageGenerator.vue` la parte de selección de música

**Props**:
```typescript
interface Props {
  tracks: MusicTrack[]
  selectedTrackFilename?: string
  showToggle?: boolean         // Toggle "Agregar música"
  badgeStyle?: boolean         // Mostrar como badges
}
```

**Emits**:
```typescript
const emit = defineEmits<{
  'select': [filename: string | null]
  'toggle': [enabled: boolean]
}>()
```

**Tamaño objetivo**: ~100 líneas

---

### Tarea 0.6: Crear AudioPlayerBase.vue

**Ubicación**: `frontend/src/components/shared/audio/AudioPlayerBase.vue`

**Referencia**: Simplificar de `AudioPreview.vue`

**Props**:
```typescript
interface Props {
  audioUrl: string
  duration?: number
  title?: string
  subtitle?: string
  showWaveform?: boolean       // Visual opcional
}
```

**Emits**:
```typescript
const emit = defineEmits<{
  'play': []
  'pause': []
  'ended': []
  'timeupdate': [currentTime: number]
}>()
```

**Slots**:
- `actions` - Botones adicionales (Guardar, Enviar, etc.)

**Tamaño objetivo**: ~100 líneas

---

### Tarea 0.7: Crear exports

**Archivo**: `frontend/src/components/shared/audio/index.ts`
```typescript
export { default as VoiceSelectorBase } from './VoiceSelectorBase.vue'
export { default as MusicSelectorBase } from './MusicSelectorBase.vue'
export { default as AudioPlayerBase } from './AudioPlayerBase.vue'
```

**Archivo**: `frontend/src/components/shared/ui/index.ts`
```typescript
export { default as CollapsiblePanel } from './CollapsiblePanel.vue'
```

**Archivo**: `frontend/src/components/shared/index.ts`
```typescript
export * from './audio'
export * from './ui'
```

---

## Verificación Final

### Checklist de NO-REGRESIÓN

```
□ npm run dev → Sin errores
□ Abrir Dashboard → Carga correctamente
□ Seleccionar voz → Funciona
□ Seleccionar música → Funciona
□ Generar audio → Funciona
□ Reproducir audio → Funciona
□ Guardar a biblioteca → Funciona
□ Library → Funciona
□ Calendar → Funciona
□ Settings → Funciona
```

### Checklist de Componentes Shared

```
□ CollapsiblePanel.vue existe y compila
□ VoiceSelectorBase.vue existe y compila
□ MusicSelectorBase.vue existe y compila
□ AudioPlayerBase.vue existe y compila
□ Exports configurados correctamente
□ npm run build → Sin errores
□ npm run type-check → Sin errores
```

---

## Notas Importantes

### ¿Por qué NO refactorizar Dashboard?

El Dashboard funciona perfectamente. Refactorizarlo para usar los componentes Base:
- Introduce riesgo innecesario
- No aporta valor inmediato
- Puede hacerse después como mejora opcional

**Estrategia**: Crear componentes Base como NUEVOS. Dashboard no se toca.

### ¿Qué pasa si no hay tiempo para extraer todo?

Prioridad de extracción:
1. **CollapsiblePanel** - OBLIGATORIO (no existe, se necesita)
2. **VoiceSelectorBase** - ALTA (se usa en TTSGenerator)
3. **AudioPlayerBase** - ALTA (se usa en AudioPreviewCard)
4. **MusicSelectorBase** - MEDIA (puede inline en StepGenerate si falta tiempo)

### Alternativa si la extracción es muy compleja

Si extraer es muy arriesgado, crear componentes desde cero para Campaigns:
- Más código duplicado
- Pero cero riesgo de romper Dashboard
- Se puede consolidar después

---

## Resultado Esperado

```
frontend/src/components/
├── shared/                      # NUEVO
│   ├── index.ts
│   ├── audio/
│   │   ├── index.ts
│   │   ├── VoiceSelectorBase.vue
│   │   ├── MusicSelectorBase.vue
│   │   └── AudioPlayerBase.vue
│   └── ui/
│       ├── index.ts
│       └── CollapsiblePanel.vue
│
├── dashboard/                   # SIN CAMBIOS
│   ├── VoiceSelector.vue        # Intacto
│   ├── AudioPreview.vue         # Intacto
│   └── ...
│
└── campaigns/                   # Fase 2+
    └── (vacío por ahora)
```

---

## Implementación Completada (2025-12-21)

### Archivos Creados

```
frontend/src/components/shared/
├── index.ts
├── audio/
│   ├── index.ts
│   ├── VoiceSelectorBase.vue    (~115 líneas)
│   ├── MusicSelectorBase.vue    (~100 líneas)
│   └── AudioPlayerBase.vue      (~100 líneas)
└── ui/
    ├── index.ts
    └── CollapsiblePanel.vue     (~80 líneas)
```

### Verificación
- Dashboard sigue funcionando correctamente
- Build pasa sin errores
- Componentes listos para usar en Campaigns

---

**Siguiente fase**: `PHASE_1_BACKEND.md` - Migración de base de datos y endpoints
