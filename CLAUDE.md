# MediaFlow v2.1 - Project Context

**Last Updated**: 2026-01-27
**Purpose**: Context documentation for Claude AI assistants

---

## Project Overview

**MediaFlow v2.1** is an automated radio system with TTS (Text-to-Speech) and AI that generates professional audio messages with customizable voices and plays them on a 24/7 local player.

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI + SQLAlchemy + SQLite/PostgreSQL |
| **Frontend** | Vue 3 + TypeScript + Tailwind CSS + DaisyUI |
| **External APIs** | ElevenLabs (TTS) + Claude AI (Anthropic) |

### Key URLs

- Backend API: `http://localhost:3001`
- API Docs: `http://localhost:3001/api/docs`
- Frontend: `http://localhost:5173`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vue 3)                         │
├─────────────┬─────────────┬─────────────┬─────────────┬────────┤
│  Dashboard  │   Library   │  Calendar   │  Settings   │  ...   │
│  (Generate) │  (Organize) │ (Schedule)  │ (Configure) │        │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴────────┘
       │             │             │             │
       └─────────────┴──────┬──────┴─────────────┘
                            │ HTTP/REST
       ┌────────────────────▼────────────────────┐
       │            BACKEND (FastAPI)            │
       ├─────────────────────────────────────────┤
       │  /api/v1/audio     - Audio generation   │
       │  /api/v1/library   - Message library    │
       │  /api/v1/schedules - Scheduling         │
       │  /api/v1/settings  - Configuration      │
       │  /api/v1/ai        - AI suggestions     │
       │  /api/v1/categories - Categories        │
       └─────────────────────────────────────────┘
                            │
       ┌────────────────────▼────────────────────┐
       │              SERVICES                    │
       ├──────────┬──────────┬──────────────────┤
       │ ElevenLabs│  Claude  │  Jingle Service  │
       │   (TTS)   │   (AI)   │  (Audio Mixing)  │
       └──────────┴──────────┴──────────────────┘
```

---

## Backend Structure

```
backend/app/
├── api/v1/
│   ├── endpoints/
│   │   ├── audio.py              # Audio generation
│   │   ├── library.py            # Library CRUD
│   │   ├── schedules.py          # Schedule management
│   │   ├── categories.py         # Public categories (read-only)
│   │   ├── ai.py                 # AI suggestions
│   │   └── settings/             # ⭐ Refactored modular structure
│   │       ├── __init__.py       # Router aggregator
│   │       ├── voices.py         # Voice CRUD (8 endpoints)
│   │       ├── music.py          # Music tracks CRUD (7 endpoints)
│   │       ├── categories.py     # Category management (6 endpoints)
│   │       └── automatic.py      # Automatic mode (2 endpoints)
│   ├── serializers/              # ⭐ Shared serialization
│   │   ├── voice_serializer.py
│   │   └── music_serializer.py
│   └── api.py                    # Main router
├── models/
│   ├── voice_settings.py         # Voice configuration
│   ├── music_track.py            # Background music tracks
│   ├── category.py               # Dynamic categories
│   ├── audio.py                  # Audio messages
│   ├── schedule.py               # Scheduled playback
│   └── player.py                 # Player status
├── schemas/
│   ├── voice.py                  # Voice Pydantic models
│   ├── music.py                  # Music Pydantic models
│   ├── automatic.py              # Automatic mode models
│   ├── category.py               # Category models
│   └── audio.py                  # Audio models
├── services/
│   ├── tts/
│   │   ├── elevenlabs.py         # ElevenLabs TTS client
│   │   └── voice_manager.py      # Voice settings manager
│   ├── ai/
│   │   └── claude.py             # Claude AI integration
│   └── audio/
│       ├── jingle.py             # Audio mixing with FFmpeg
│       └── utils.py              # Audio utilities
└── core/
    └── config.py                 # Application settings
```

### Key Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/audio/generate` | POST | Generate TTS audio |
| `/api/v1/audio/voices` | GET | List active voices |
| `/api/v1/library/messages` | GET | List library messages |
| `/api/v1/settings/voices` | GET/POST/PATCH/DELETE | Voice management |
| `/api/v1/settings/music` | GET/POST/PATCH/DELETE | Music tracks |
| `/api/v1/settings/categories` | GET/POST/PATCH/DELETE | Categories |
| `/api/v1/settings/automatic/generate` | POST | Automatic jingle generation |

---

## Frontend Structure

```
frontend/src/
├── components/
│   ├── dashboard/                # Main generation interface
│   │   ├── Dashboard.vue
│   │   ├── MessageGenerator.vue
│   │   ├── VoiceSelector.vue
│   │   ├── AudioPreview.vue
│   │   ├── RecentMessages.vue
│   │   └── AISuggestions.vue
│   │
│   ├── library/                  # Audio library management
│   │   ├── Library.vue           # Container
│   │   ├── components/
│   │   │   ├── LibraryGrid.vue
│   │   │   ├── LibraryList.vue
│   │   │   ├── MessageCard.vue
│   │   │   └── ...
│   │   ├── composables/
│   │   │   ├── useAudioPlayer.ts
│   │   │   ├── useSelection.ts
│   │   │   └── useFileUpload.ts
│   │   ├── modals/
│   │   │   ├── ScheduleModal.vue
│   │   │   └── UploadModal.vue
│   │   └── stores/
│   │       └── libraryStore.ts
│   │
│   ├── calendar/                 # Schedule management
│   │   ├── Calendar.vue
│   │   ├── components/
│   │   └── stores/
│   │
│   └── settings/                 # Configuration (Playground)
│       ├── SettingsNav.vue
│       ├── voices/               # Voice Manager
│       │   ├── VoiceManager.vue
│       │   ├── components/
│       │   │   ├── VoiceEditor.vue
│       │   │   ├── VoiceList.vue
│       │   │   └── VoiceAddModal.vue
│       │   └── composables/
│       │       └── useVoiceManager.ts
│       ├── music/                # Music Manager
│       │   ├── MusicManager.vue
│       │   ├── components/
│       │   └── composables/
│       ├── categories/           # Category Editor
│       │   ├── CategoryEditor.vue
│       │   ├── components/
│       │   └── composables/
│       └── automatic/            # Automatic Mode
│           ├── AutomaticMode.vue
│           ├── components/
│           └── composables/
│
├── stores/
│   └── audio.ts                  # Global audio store
├── api/
│   ├── client.ts                 # Axios wrapper
│   └── audio.ts                  # Audio API calls
├── types/
│   ├── audio.ts
│   └── api.ts
└── router/
    └── index.ts
```

---

## Design Philosophy

### 1. Automatic Voice Settings

Each voice has pre-configured settings that are applied automatically:

```python
# ElevenLabs recommended defaults (from official documentation):
# https://elevenlabs.io/docs/product-guides/products/studio#settings
VoiceSettings:
  - style: 0.0            # 0-100 (ElevenLabs default: 0 - "keep at 0 at all times")
  - stability: 50.0       # 0-100 (ElevenLabs default: 50 - "stability around 50")
  - similarity_boost: 75.0 # 0-100 (ElevenLabs default: 75 - "similarity near 75")
  - speed: 1.0            # 0.7-1.2 (ElevenLabs default: 1.0)
  - use_speaker_boost: true
  - volume_adjustment: 0.0  # dB (-20 to +20) - MediaFlow specific
  - jingle_settings: {      # MediaFlow specific (per-voice customization)
      music_volume: 1.0,
      voice_volume: 1.0,
      duck_level: 0.2,
      intro_silence: 3.0,
      outro_silence: 5.0
    }
```

**User flow**:
1. Admin configures voices ONCE in Settings
2. User in Dashboard only selects voice
3. Settings apply automatically
4. Zero friction

### 2. Categories Only in Library

- **Dashboard**: Simple, fast generation (NO category selection)
- **Library**: Full organization with categories

```
Flow:
Dashboard → Generate → Save to Library → Assign category
```

### 3. Cross-Category Favorites

Favorites span all categories - use `is_favorite` filter.

---

## Data Models

### VoiceSettings
```python
{
  "id": "juan_carlos",
  "name": "Juan Carlos",
  "elevenlabs_id": "G4IAP30yc6c1gK0csDfu",
  "active": true,
  "is_default": false,
  # ElevenLabs settings (defaults from official docs)
  "style": 0.0,             # ElevenLabs default: 0
  "stability": 50.0,        # ElevenLabs default: 50
  "similarity_boost": 75.0, # ElevenLabs default: 75
  "speed": 1.0,             # ElevenLabs default: 1.0
  "use_speaker_boost": true,
  # MediaFlow settings
  "volume_adjustment": 0.0,
  "jingle_settings": {...}
}
```

### MusicTrack
```python
{
  "id": 1,
  "filename": "cool_beat.mp3",
  "display_name": "Cool Beat",
  "duration": 180.5,
  "is_default": true,
  "active": true
}
```

### Category
```python
{
  "id": "pedidos",
  "name": "Pedidos Listos",
  "icon": "📦",
  "color": "#FF4444",
  "order": 1,
  "active": true
}
```

### AudioMessage
```python
{
  "id": 1,
  "filename": "auto_20251203_123456_juan_carlos.mp3",
  "display_name": "Pedido 42 listo",
  "original_text": "...",
  "voice_id": "juan_carlos",
  "category_id": "pedidos",
  "is_favorite": false,
  "has_jingle": true,
  "music_file": "cool_beat.mp3",
  "duration": 15.5,
  "status": "ready"
}
```

---

## Common Commands

### Backend
```bash
cd /var/www/mediaflow-v2/backend
source venv/bin/activate

# Run server
uvicorn app.main:app --reload --port 3001

# Database migration
alembic upgrade head
alembic revision --autogenerate -m "description"

# Tests
pytest tests/ -v
```

### Frontend
```bash
cd /var/www/mediaflow-v2/frontend

# Development
npm run dev

# Build
npm run build

# Lint
npm run lint
```

---

## Recent Refactoring (2025-12-03)

### Backend Settings Module

The monolithic `settings.py` (1,682 lines) was refactored into:

```
endpoints/settings/
├── __init__.py       # Router aggregator (18 lines)
├── voices.py         # Voice management (422 lines)
├── music.py          # Music management (372 lines)
├── categories.py     # Category management (364 lines)
└── automatic.py      # Automatic mode (278 lines)
```

**Benefits**:
- Single responsibility per file
- Easier testing and maintenance
- Shared serializers eliminate duplication
- Clear separation of concerns

### New Schemas
```
schemas/
├── voice.py      # Voice-related Pydantic models
├── music.py      # Music track models
└── automatic.py  # Automatic mode models
```

### New Serializers
```
api/v1/serializers/
├── voice_serializer.py   # serialize_voice(model) → dict
└── music_serializer.py   # serialize_music_track(model) → response
```

---

## Important Notes for Development

1. **Voice settings are automatic** - Never ask user to configure them in Dashboard
2. **Dashboard is simple** - No categories, no complex configurations
3. **Library is powerful** - Full categorization and organization happens here
4. **Settings/Playground is professional** - Configure once, use automatically
5. **TypeScript strict** - 100% type-safe frontend
6. **Async everywhere** - All backend operations are async

---

## File Size Guidelines

After refactoring, target file sizes:

| Type | Target Lines | Max Lines |
|------|-------------|-----------|
| Vue Component | 100-200 | 300 |
| Composable | 100-150 | 250 |
| API Endpoint | 200-300 | 400 |
| Service | 150-250 | 350 |

---

## Troubleshooting

### Backend not responding
```bash
cd /var/www/mediaflow-v2/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

### Frontend not loading
```bash
cd /var/www/mediaflow-v2/frontend
npm run dev
```

### Database issues
```bash
cd /var/www/mediaflow-v2/backend
rm mediaflow.db
alembic upgrade head
```

### Import verification
```bash
cd /var/www/mediaflow-v2/backend
source venv/bin/activate
python -c "from app.main import app; print('OK')"
```

---

## Campaign Manager (Completo)

Modulo para gestionar campanas publicitarias anuales con generacion TTS asistida por IA.

### Estado Actual

| Fase | Estado | Descripcion |
|------|--------|-------------|
| Fase 0 | ✅ | Componentes shared/ creados |
| Fase 1 | ✅ | Backend /api/v1/campaigns |
| Fase 2 | ✅ | Frontend lista de campanas |
| Fase 3 | ✅ | Detail + paneles colapsables |
| Fase 4 | ✅ | Workflow de generacion completo |
| Fase 5 | ✅ | Grid de audios + eliminacion |

### Que Existe

**Backend:**
- `GET/POST/PATCH /api/v1/campaigns` - CRUD completo
- `GET /api/v1/campaigns/:id/audios` - Audios por campana (incluye `audio_url`)
- `DELETE /api/v1/library/:id` - Soft delete de audios
- `Category.ai_instructions` - Entrenamiento IA por campana

**Frontend:**
```
frontend/src/
├── types/campaign.ts
└── components/campaigns/
    ├── CampaignList.vue              # Grid de campanas
    ├── CampaignDetail.vue            # Layout 3:2 con componentes dinamicos
    ├── components/
    │   ├── CampaignCard.vue
    │   ├── AITrainingPanel.vue       # Panel entrenamiento IA
    │   ├── RecentMessagesPanel.vue   # Panel mensajes recientes
    │   ├── CampaignAudioGrid.vue     # Grid de audios con paginacion
    │   └── CampaignAudioCard.vue     # Card con play/delete
    ├── steps/
    │   ├── StepInput.vue             # Textarea descripcion
    │   ├── StepSuggestions.vue       # Cards sugerencias IA
    │   ├── StepGenerate.vue          # Selector voz + musica
    │   └── StepPreview.vue           # Reproductor + acciones
    ├── composables/
    │   └── useCampaignWorkflow.ts    # State machine completa
    ├── modals/NewCampaignModal.vue
    └── stores/campaignStore.ts
```

**Shared:**
```
components/shared/
├── audio/
│   ├── VoiceSelectorBase.vue
│   ├── MusicSelectorBase.vue
│   └── AudioPlayerBase.vue
└── ui/
    └── CollapsiblePanel.vue
```

### Gotchas Importantes

1. **apiClient devuelve data directamente:**
   ```typescript
   const data = await apiClient.get('/api/v1/campaigns')  // ✅ data directo
   // NO: response.data
   ```

2. **Rutas API siempre con prefijo /api/v1/:**
   ```typescript
   await apiClient.get('/api/v1/campaigns/...')  // ✅
   // NO: '/campaigns/...'
   ```

3. **Tipos correctos para audios de campana:**
   ```typescript
   import type { CampaignAudio } from '@/types/campaign'  // ✅
   // NO: AudioMessage de @/types/audio
   ```

4. **Endpoint DELETE es /library/, no /audio/:**
   ```typescript
   await apiClient.delete(`/api/v1/library/${id}`)  // ✅ soft delete
   // NO: /api/v1/audio/
   ```

5. **CampaignAudio incluye audio_url** - Para reproduccion directa

6. **Probar despues de cada componente:**
   ```bash
   npm run build
   ```

### Documentacion

- Plan completo: `docs/CAMPAIGN_MASTER_PLAN.md`
- Fases: `docs/phases/PHASE_*.md`

---

## Servidor de Desarrollo (Demo)

**Dominio**: demo.mediaflow.cl
**IP**: 148.113.205.115
**Ubicación**: /var/www/mediaflow-v2

### URLs

| Servicio | URL |
|----------|-----|
| **Frontend** | https://demo.mediaflow.cl |
| **API** | https://demo.mediaflow.cl/api/v1/ |
| **API Docs** | https://demo.mediaflow.cl/api/docs |

### Azuracast (Radio Streaming Local)

| Servicio | URL |
|----------|-----|
| **Panel Azuracast** | http://radio.mediaflow.cl |
| **Stream Radio** | http://148.113.205.115:8000 |

**Configuración Azuracast** (`/var/azuracast/.env`):
```env
AZURACAST_HTTP_PORT=10080
AZURACAST_HTTPS_PORT=10443
```

**Nota**: El panel está accesible via nginx proxy en `radio.mediaflow.cl` (puerto 80 → 10080 interno).

**Comandos Azuracast:**
```bash
# Ver estado
cd /var/azuracast && docker compose ps

# Ver logs
cd /var/azuracast && docker compose logs -f

# Reiniciar
cd /var/azuracast && docker compose restart
```

**Ajuste de volumen via Liquidsoap:**
- Ir a: Panel Azuracast → Station → Utilities → Edit Liquidsoap Configuration
- Agregar `radio = amplify(0.7, radio)` para bajar volumen al 70%
- O usar dB: `radio = amplify(lin_of_dB(-3.), radio)` para bajar 3dB

---


---

## OpenClaw - Agente IA via WhatsApp

MediaFlow cuenta con un agente IA autónomo operado por **OpenClaw**, que permite controlar el sistema completo via WhatsApp.

### Servidor OpenClaw

| Dato | Valor |
|------|-------|
| **IP** | `51.38.227.237` |
| **Hostname** | vps-6c8f2ce2 |
| **Acceso SSH** | `ssh root@51.38.227.237` (SSH keys configuradas) |
| **Workspace** | `/root/.openclaw/workspace-mediaflow/` |
| **Config principal** | `/root/.openclaw/openclaw.json` |
| **Docs** | `docs/openclaw-docs.md` (referencia local) |

### Qué es OpenClaw

Plataforma self-hosted de asistentes IA con agentes autónomos. Cada agente tiene su propio workspace, memoria, identidad y herramientas. Se conecta a canales de mensajería (WhatsApp, Telegram, Discord, etc.) y puede ejecutar acciones proactivas via heartbeats y cron jobs.

### Agentes configurados

| Agente | Workspace | Canal |
|--------|-----------|-------|
| **mediaflow** | `workspace-mediaflow/` | WhatsApp (grupo MediaFlow) |
| **radio** | `workspace-radio/` | WhatsApp (grupo Radio) |
| **hogar** | `workspace-hogar/` | WhatsApp (grupo Hogar) |

### Agente MediaFlow - Capacidades

El agente `mediaflow` consume la API REST de MediaFlow y puede:

1. **Generar textos con IA** — `POST /api/v1/ai/generate`
2. **Generar audio TTS** — `POST /api/v1/audio/generate` (con o sin música de fondo)
3. **Enviar audio por WhatsApp** — usando `MEDIA:https://demo.mediaflow.cl/storage/audio/{filename}`
4. **Guardar en biblioteca** — `PATCH /api/v1/audio/{id}/save-to-library`
5. **Crear programaciones** — `POST /api/v1/schedules` (intervalo, horario específico, una vez)
6. **Gestionar schedules** — listar, pausar, eliminar
7. **Consultar biblioteca y categorías**

### Archivos clave del workspace

```
/root/.openclaw/workspace-mediaflow/
├── AGENTS.md        # Instrucciones generales del agente
├── SOUL.md          # Personalidad y comportamiento
├── USER.md          # Info del usuario (Hernan)
├── IDENTITY.md      # Identidad del agente (sin configurar)
├── TOOLS.md         # Endpoints API de MediaFlow documentados
├── HEARTBEAT.md     # Tareas periódicas
├── knowledge/
│   └── mediaflow.md # Contexto del negocio
└── memory/          # Memoria diaria del agente
```

### Config del agente

- **Modelo**: `anthropic/claude-sonnet-4-6`
- **Heartbeat**: cada 30 minutos
- **TTS**: ElevenLabs (`eleven_multilingual_v2`, español, speed 1.15)
- **Web search**: Perplexity (sonar-pro)
- **Browser**: headless habilitado
- **WhatsApp**: no requiere mención en grupo (`requireMention: false`)

### Flujo típico via WhatsApp

```
Usuario escribe descripción en grupo WhatsApp
  → Agente genera sugerencias de texto con IA
  → Usuario elige texto(s)
  → Agente pregunta si quiere música de fondo
  → Genera audio TTS via API
  → Envía audio al grupo WhatsApp
  → Pregunta si guardar en biblioteca / programar / ambos
  → Ejecuta acción correspondiente
```

### Comandos útiles OpenClaw

```bash
# Conectar al servidor
ssh root@51.38.227.237

# Ver config principal
cat /root/.openclaw/openclaw.json

# Ver workspace mediaflow
ls -la /root/.openclaw/workspace-mediaflow/

# Ver TOOLS.md (endpoints API)
cat /root/.openclaw/workspace-mediaflow/TOOLS.md

# Ver logs
ls /root/.openclaw/logs/
```

---

**Version**: 2.1
**Architecture**: Modular with separated concerns
**Status**: Production-ready core functionality
