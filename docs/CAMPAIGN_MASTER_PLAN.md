# Campaign Manager - Plan Maestro de Implementación

**Versión**: 1.1
**Fecha**: 2025-12-21
**Estado**: En Desarrollo (Fases 0-2 Completadas)

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Decisiones de Arquitectura](#2-decisiones-de-arquitectura)
3. [Módulos a Crear](#3-módulos-a-crear)
4. [Dependencias con Sistema Actual](#4-dependencias-con-sistema-actual)
5. [Fases de Desarrollo](#5-fases-de-desarrollo)
6. [Riesgos y Mitigaciones](#6-riesgos-y-mitigaciones)
7. [Estructura de Archivos Final](#7-estructura-de-archivos-final)
8. [Documentos Relacionados](#8-documentos-relacionados)

---

## 1. Resumen Ejecutivo

### Objetivo
Implementar un módulo de **Campaign Manager** que permita gestionar campañas publicitarias anuales con generación de TTS asistida por IA, reutilizando la infraestructura existente de MediaFlow v2.1.

### Alcance del MVP
- Página 1: Grid de campañas (basado en Categories existentes)
- Página 2: Detalle de campaña con workflow de generación
- Entrenamiento de IA específico por campaña
- Generación de sugerencias y audio TTS
- Historial de audios por campaña

### Fuera del Alcance (Placeholders)
- Sistema de sucursales/branches
- Envío en tiempo real a parlantes
- Programación avanzada por sucursal

### Principio Rector
**Campañas = Categorías**. No crear nuevo modelo. Extender Category con `ai_instructions`.

---

## 2. Decisiones de Arquitectura

### 2.1 Modelo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                     DECISIÓN: Reutilizar Category               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Category (existente)              Category (extendido)         │
│  ─────────────────────             ─────────────────────        │
│  id                                id                           │
│  name                              name                         │
│  icon                              icon                         │
│  color                             color                        │
│  order                             order                        │
│  active                            active                       │
│                                    ai_instructions  ← NUEVO     │
│                                                                 │
│  Beneficios:                                                    │
│  • AudioMessage.category_id ya conecta audios con campañas      │
│  • Library ya filtra por categoría                              │
│  • No duplicar lógica CRUD                                      │
│  • Settings/Categories ya gestiona categorías                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Integración de IA

```
┌─────────────────────────────────────────────────────────────────┐
│              DECISIÓN: Entrenamiento en 2 Niveles               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Nivel 1: Sistema de Clientes (EXISTENTE - NO TOCAR)            │
│  ─────────────────────────────────────────────────────          │
│  • AIClient model con configuración por cliente                 │
│  • Prompts base del sistema demo                                │
│  • Funciona perfectamente para presentaciones                   │
│                                                                 │
│  Nivel 2: Entrenamiento por Campaña (NUEVO)                     │
│  ─────────────────────────────────────────────────────          │
│  • Category.ai_instructions                                     │
│  • Se AÑADE al prompt, no lo reemplaza                          │
│  • Opcional: si está vacío, usa solo Nivel 1                    │
│                                                                 │
│  Flujo de generación:                                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Prompt Base  │ +  │ AI Client    │ +  │ Campaign     │      │
│  │ (Sistema)    │    │ (Cliente)    │    │ Instructions │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         └───────────────────┴───────────────────┘               │
│                             │                                   │
│                             ▼                                   │
│                    [Prompt Combinado]                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│           DECISIÓN: Componentes Compartidos (shared/)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ANTES (Dashboard actual):                                      │
│  dashboard/                                                     │
│  ├── VoiceSelector.vue      ← Acoplado a Dashboard              │
│  ├── AudioPreview.vue       ← Acoplado a Dashboard              │
│  └── AISuggestions.vue      ← Acoplado a Dashboard              │
│                                                                 │
│  DESPUÉS (Compartido):                                          │
│  shared/                                                        │
│  ├── audio/                                                     │
│  │   ├── VoiceSelectorBase.vue    ← Reutilizable                │
│  │   ├── MusicSelectorBase.vue    ← Reutilizable                │
│  │   └── AudioPlayerBase.vue      ← Reutilizable                │
│  └── ui/                                                        │
│      └── CollapsiblePanel.vue     ← Nuevo componente            │
│                                                                 │
│  dashboard/                                                     │
│  ├── VoiceSelector.vue      ← Usa VoiceSelectorBase             │
│  └── AudioPreview.vue       ← Usa AudioPlayerBase               │
│                                                                 │
│  campaigns/                                                     │
│  ├── TTSGenerator.vue       ← Usa VoiceSelectorBase + Music     │
│  └── AudioPreviewCard.vue   ← Usa AudioPlayerBase + acciones    │
│                                                                 │
│  Beneficio: Dashboard NO SE TOCA, solo se extraen bases         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 Prevención de Monolitos

```
┌─────────────────────────────────────────────────────────────────┐
│         DECISIÓN: CampaignDetail dividido por estados           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PROBLEMA: CampaignDetail.vue podría tener 800+ líneas          │
│                                                                 │
│  SOLUCIÓN: Composable con state machine + componentes por paso  │
│                                                                 │
│  useCampaignWorkflow.ts                                         │
│  ─────────────────────                                          │
│  step: 'input' | 'suggestions' | 'generate' | 'preview'         │
│                                                                 │
│  CampaignDetail.vue (< 150 líneas)                              │
│  ─────────────────────────────────                              │
│  <template>                                                     │
│    <StepInput v-if="step === 'input'" />                        │
│    <StepSuggestions v-if="step === 'suggestions'" />            │
│    <StepGenerate v-if="step === 'generate'" />                  │
│    <StepPreview v-if="step === 'preview'" />                    │
│    <CampaignAudioGrid />  <!-- Siempre visible -->              │
│  </template>                                                    │
│                                                                 │
│  Componentes por paso:                                          │
│  ├── steps/StepInput.vue         (~100 líneas)                  │
│  ├── steps/StepSuggestions.vue   (~120 líneas)                  │
│  ├── steps/StepGenerate.vue      (~150 líneas)                  │
│  └── steps/StepPreview.vue       (~100 líneas)                  │
│                                                                 │
│  Total: ~620 líneas distribuidas vs 800 en monolito             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Módulos a Crear

### 3.1 Backend

| Módulo | Archivo | Descripción | Líneas Est. |
|--------|---------|-------------|-------------|
| Migración | `alembic/versions/xxx_add_ai_instructions.py` | Agregar campo a Category | ~30 |
| Schema | `schemas/campaign.py` | Tipos para AI training | ~50 |
| Endpoint | `endpoints/campaigns.py` | GET campañas + PATCH ai_instructions | ~150 |
| Service | `services/ai/claude.py` | MODIFICAR: aceptar campaign_instructions | ~30 cambios |

**Total Backend**: ~260 líneas nuevas/modificadas

### 3.2 Frontend

| Módulo | Descripción | Componentes | Líneas Est. |
|--------|-------------|-------------|-------------|
| Shared Base | Componentes reutilizables | 3 | ~300 |
| Campaign List | Página 1: Grid | 3 | ~350 |
| Campaign Detail | Página 2: Workflow | 8 | ~650 |
| Store | Estado global | 1 | ~150 |
| Composables | Lógica de negocio | 2 | ~300 |
| Types | Definiciones TS | 1 | ~50 |

**Total Frontend**: ~1,800 líneas nuevas

### 3.3 Módulos que NO se crean

| Módulo | Razón |
|--------|-------|
| Branch/Sucursales model | Placeholder - fase futura |
| SendToSpeakers real | Placeholder - fase futura |
| ScheduleModal real | Reutilizar existente de Library |
| Category CRUD | Ya existe en Settings |

---

## 4. Dependencias con Sistema Actual

### 4.1 Módulos que se REUTILIZAN (sin modificar)

```
┌─────────────────────────────────────────────────────────────────┐
│                    REUTILIZACIÓN DIRECTA                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Backend:                                                       │
│  • Category model → Campañas son categorías                     │
│  • AudioMessage model → category_id conecta audios              │
│  • ElevenLabs service → Generación TTS                          │
│  • JingleService → Mezcla con música                            │
│  • VoiceManager → Obtener voces activas                         │
│                                                                 │
│  Frontend:                                                      │
│  • useAudioStore → Voces, música, generación                    │
│  • audioApi → Llamadas a /api/v1/audio                          │
│  • VoiceSelector pattern → Avatares + selección                 │
│  • AudioPreview pattern → Reproductor + controles               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Módulos que se MODIFICAN (mínimamente)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODIFICACIONES MENORES                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Backend:                                                       │
│  • Category model: +ai_instructions field                       │
│  • ClaudeService: +campaign_instructions parameter              │
│  • /api/v1/ai/generate: +campaign_id optional param             │
│                                                                 │
│  Frontend:                                                      │
│  • router/index.ts: +2 rutas (/campaigns, /campaigns/:id)       │
│  • Sidebar: +1 enlace a Campañas                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Mapa de Dependencias

```
                    ┌──────────────────┐
                    │ Campaign Manager │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    Category     │ │   AudioStore    │ │  ClaudeService  │
│    (Backend)    │ │   (Frontend)    │ │    (Backend)    │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │                   ▼                   │
         │          ┌─────────────────┐          │
         │          │  ElevenLabs     │          │
         │          │  + JingleSvc    │          │
         │          └─────────────────┘          │
         │                                       │
         ▼                                       ▼
┌─────────────────┐                    ┌─────────────────┐
│  AudioMessage   │                    │   AIClient      │
│  (Audios)       │                    │  (Existente)    │
└─────────────────┘                    └─────────────────┘
```

---

## 5. Fases de Desarrollo

### Fase 0: Preparación (Pre-requisito) ✅
**Estado**: Completado (2025-12-21)
**Documentos**: `PHASE_0_PREPARATION.md`

```
Tareas:
✓ Extraer componentes base a shared/
  - VoiceSelectorBase.vue (desde Dashboard)
  - AudioPlayerBase.vue (desde Dashboard)
  - MusicSelectorBase.vue (desde Settings)
✓ Crear CollapsiblePanel.vue
✓ Verificar que Dashboard sigue funcionando
✓ NO tocar lógica, solo extraer UI
```

### Fase 1: Backend ✅
**Estado**: Completado (2025-12-21)
**Documentos**: `PHASE_1_BACKEND.md`

```
Tareas:
✓ Migración: agregar ai_instructions a Category
✓ Schema: CampaignResponse, CampaignCreate, CampaignUpdate
✓ Endpoints CRUD completos en /api/v1/campaigns
✓ Endpoint: GET /api/v1/campaigns/:id/audios
✓ Modificar ClaudeService para aceptar campaign_instructions
```

### Fase 2: Campaign List (Página 1) ✅
**Estado**: Completado (2025-12-21)
**Documentos**: `PHASE_2_CAMPAIGN_LIST.md`

```
Tareas:
✓ types/campaign.ts - Tipos TypeScript
✓ campaignStore.ts - Estado Pinia
✓ CampaignCard.vue - Card individual
✓ NewCampaignModal.vue - Modal crear campaña
✓ CampaignList.vue - Grid de cards
✓ CampaignDetail.vue - Placeholder para Fase 3
✓ Rutas en router (/campaigns, /campaigns/:id)
✓ Link en navegación (RocketLaunchIcon)
```

### Fase 3: Campaign Detail - Layout ✅
**Estado**: Completado (2025-12-21)
**Documentos**: `PHASE_3_CAMPAIGN_DETAIL.md`

```
Tareas:
✓ CampaignDetail.vue - Layout 3:2 + header
✓ AITrainingPanel.vue - Panel colapsable derecho
✓ RecentMessagesPanel.vue - Panel colapsable derecho
✓ useCampaignWorkflow.ts - State machine básica
✓ Navegación desde CampaignList
```

### Fase 4: Campaign Detail - Workflow ✅
**Estado**: Completado (2025-12-21)
**Documentos**: `PHASE_4_WORKFLOW.md`

```
Tareas:
✓ steps/StepInput.vue - Textarea + botón sugerencia
✓ steps/StepSuggestions.vue - Cards de sugerencias
✓ steps/StepGenerate.vue - Voz + música + generar
✓ steps/StepPreview.vue - Audio generado + acciones
✓ Integración con ClaudeService (campaign_instructions)
✓ Integración con AudioStore (generación)
```

### Fase 5: Audio Grid + Finalización
**Duración estimada**: 1 sesión
**Documentos**: `PHASE_5_AUDIO_GRID.md`

```
Tareas:
□ CampaignAudioGrid.vue - Grid de audios de la campaña
□ CampaignAudioCard.vue - Card con acciones (play, schedule placeholder, delete)
□ Guardar audio con category_id = campaign_id
□ Filtrar audios por campaña
□ Testing E2E del flujo completo
```

### Diagrama de Fases

```
Fase 0          Fase 1          Fase 2          Fase 3          Fase 4          Fase 5
────────────────────────────────────────────────────────────────────────────────────────►

[Preparación]   [Backend]       [List Page]     [Detail Layout] [Workflow]      [Grid]
    ✅              ✅              ✅              ✅              ✅              ⏳

Shared/         Migration       CampaignList    CampaignDetail  StepInput       AudioGrid
Components      Schema          CampaignCard    AITraining      StepSuggestions AudioCard
                Endpoints       Modal           RecentMessages  StepGenerate    Save flow
                Claude mod      Store           Workflow.ts     StepPreview     Filter
                                Router                          AI Integration
                                                                Audio Gen

     │               │               │               │               │             │
     ▼               ▼               ▼               ▼               ▼             ▼
[Dashboard OK]  [API Ready]     [Nav Works]     [Layout OK]     [Gen Works]   [Complete]
     ✅              ✅              ✅             ✅              ✅
```

---

## 6. Riesgos y Mitigaciones

### 6.1 Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| CampaignDetail monolítico | Alta | Alto | State machine + componentes por paso |
| Duplicar lógica de Dashboard | Media | Medio | Shared components + composables |
| Romper Dashboard al extraer | Media | Alto | Extraer sin modificar, luego refactorizar |
| ClaudeService breaking change | Baja | Alto | Parámetro opcional, backward compatible |
| Store conflictos con Library | Media | Medio | Store separado (campaignStore) |

### 6.2 Riesgos de Scope

| Riesgo | Mitigación |
|--------|------------|
| Agregar sucursales antes de tiempo | Mantener como placeholder, UI sin funcionalidad |
| Sobre-ingeniar entrenamiento IA | Solo agregar ai_instructions, no nuevo sistema |
| Crear nuevos modelos innecesarios | Campaign = Category, no duplicar |

### 6.3 Checklist Anti-Monolito

Antes de cada PR, verificar:

```
□ ¿Algún archivo supera 300 líneas?
  → Dividir en componentes/composables

□ ¿El composable tiene más de 200 líneas?
  → Extraer helpers o dividir responsabilidades

□ ¿Hay código duplicado con Dashboard?
  → Extraer a shared/

□ ¿El componente tiene más de 3 responsabilidades?
  → Dividir en subcomponentes

□ ¿Hay más de 5 refs en un composable?
  → Considerar dividir estado
```

---

## 7. Estructura de Archivos Final

### 7.1 Frontend

```
frontend/src/
├── components/
│   ├── shared/                          # NUEVO - Componentes reutilizables
│   │   ├── audio/
│   │   │   ├── VoiceSelectorBase.vue    # Extraído de Dashboard
│   │   │   ├── MusicSelectorBase.vue    # Extraído de Settings
│   │   │   └── AudioPlayerBase.vue      # Extraído de Dashboard
│   │   └── ui/
│   │       └── CollapsiblePanel.vue     # Nuevo
│   │
│   ├── campaigns/                       # NUEVO - Módulo de campañas
│   │   ├── CampaignList.vue             # Página 1
│   │   ├── CampaignDetail.vue           # Página 2 (orquestador)
│   │   ├── components/
│   │   │   ├── CampaignCard.vue
│   │   │   ├── AITrainingPanel.vue
│   │   │   ├── RecentMessagesPanel.vue
│   │   │   ├── CampaignAudioGrid.vue
│   │   │   └── CampaignAudioCard.vue
│   │   ├── steps/                       # Pasos del workflow
│   │   │   ├── StepInput.vue
│   │   │   ├── StepSuggestions.vue
│   │   │   ├── StepGenerate.vue
│   │   │   └── StepPreview.vue
│   │   ├── modals/
│   │   │   └── NewCampaignModal.vue
│   │   ├── composables/
│   │   │   ├── useCampaignWorkflow.ts   # State machine
│   │   │   └── useCampaigns.ts          # CRUD
│   │   └── stores/
│   │       └── campaignStore.ts
│   │
│   ├── dashboard/                       # EXISTENTE - Sin cambios funcionales
│   │   ├── VoiceSelector.vue            # Refactorizado para usar Base
│   │   └── ...
│   │
│   └── ...
│
├── types/
│   └── campaign.ts                      # NUEVO
│
└── router/
    └── index.ts                         # MODIFICADO: +2 rutas
```

### 7.2 Backend

```
backend/app/
├── api/v1/endpoints/
│   ├── campaigns.py                     # NUEVO (~150 líneas)
│   └── ...
│
├── schemas/
│   ├── campaign.py                      # NUEVO (~50 líneas)
│   └── ...
│
├── models/
│   └── category.py                      # MODIFICADO: +ai_instructions
│
├── services/ai/
│   └── claude.py                        # MODIFICADO: +campaign_instructions param
│
└── alembic/versions/
    └── xxx_add_ai_instructions.py       # NUEVO
```

---

## 8. Documentos Relacionados

### Documentos de Referencia (Existentes)
- `CLAUDE.md` - Contexto general del proyecto
- `CAMPAIGN_MANAGER.md` - Diseño visual original

### Documentos de Implementación

| Documento | Descripción | Fase | Estado |
|-----------|-------------|------|--------|
| `PHASE_0_PREPARATION.md` | Extracción de componentes shared | 0 | ✅ |
| `PHASE_1_BACKEND.md` | Migración + endpoints | 1 | ✅ |
| `PHASE_2_CAMPAIGN_LIST.md` | Página 1 completa | 2 | ✅ |
| `PHASE_3_CAMPAIGN_DETAIL.md` | Layout + paneles | 3 | Pendiente |
| `PHASE_4_WORKFLOW.md` | Steps + generación | 4 | Pendiente |
| `PHASE_5_AUDIO_GRID.md` | Grid final + integración | 5 | Pendiente |

---

## Apéndice: Criterios de Éxito

### MVP Completo cuando:

1. ✅ **Navegación funciona**: /campaigns muestra grid, click abre detalle
2. ✅ **CRUD campañas**: Crear, ver, actualizar ai_instructions
3. ✅ **Workflow completo**: Input → Sugerencias → TTS → Preview → Guardar
4. ✅ **AI con contexto**: Sugerencias usan ai_instructions de la campaña
5. ✅ **Audios vinculados**: Se guardan con category_id correcto
6. ⏳ **Grid funciona**: Muestra audios de la campaña, permite reproducir

### Métricas de Calidad:

- [x] Ningún archivo frontend > 300 líneas
- [x] Ningún composable > 200 líneas
- [x] Dashboard sigue funcionando idéntico
- [x] 0 duplicación de lógica entre Dashboard y Campaigns
- [x] TypeScript sin errores
- [x] Build exitoso

---

## Progreso Actual (2025-12-21)

### Completado
- **Fase 0**: Componentes shared/ creados (VoiceSelectorBase, MusicSelectorBase, AudioPlayerBase, CollapsiblePanel)
- **Fase 1**: Backend completo con endpoints CRUD en /api/v1/campaigns
- **Fase 2**: Frontend con CampaignList, CampaignCard, NewCampaignModal, campaignStore, rutas y navegación
- **Fase 3**: Layout 3:2 con paneles colapsables (AITrainingPanel, RecentMessagesPanel)
- **Fase 4**: Workflow completo con 4 pasos (Input, Suggestions, Generate, Preview)

### Próximo Paso
Implementar **Fase 5: Audio Grid** para mostrar y gestionar audios de la campaña.

### Archivos Frontend Creados
```
frontend/src/
├── types/campaign.ts
└── components/campaigns/
    ├── CampaignList.vue
    ├── CampaignDetail.vue
    ├── components/
    │   ├── CampaignCard.vue
    │   ├── AITrainingPanel.vue
    │   └── RecentMessagesPanel.vue
    ├── steps/
    │   ├── StepInput.vue
    │   ├── StepSuggestions.vue
    │   ├── StepGenerate.vue
    │   └── StepPreview.vue
    ├── composables/
    │   └── useCampaignWorkflow.ts
    ├── modals/NewCampaignModal.vue
    └── stores/campaignStore.ts
```
