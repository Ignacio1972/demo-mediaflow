# 🎮 MediaFlowDemo v2.1 - Playground Technical Specification

**Documento**: Especificación Técnica del Playground (Settings)
**Versión**: 2.1.0
**Fecha**: 2025-11-23
**Autor**: Claude (Anthropic)
**Estado**: ✅ Diseño Aprobado - Listo para Implementación

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura General](#arquitectura-general)
3. [Sección 1: Voice Manager](#sección-1-voice-manager)
4. [Sección 2: Audio Config](#sección-2-audio-config)
5. [Sección 3: Category Editor](#sección-3-category-editor)
6. [Sección 4: AI Settings (Fase 2)](#sección-4-ai-settings)
7. [Migración desde Legacy](#migración-desde-legacy)
8. [Cronología de Implementación](#cronología-de-implementación)
9. [Implementación Paso a Paso](#implementación-paso-a-paso)

---

## 📊 Resumen Ejecutivo

### Propósito del Playground

El **Playground** (Settings) es el **centro de control administrativo** de MediaFlowDemo v2.1. Su función principal es permitir la configuración de:

- ✅ **Voces**: Gestión completa de voces ElevenLabs con settings individuales
- ✅ **Audio**: Configuración global de TTS y Jingles
- ✅ **Categorías**: Sistema dinámico de categorización personalizable
- ✅ **IA**: Contextos multi-cliente para Claude AI (Fase 2)

### Filosofía de Diseño v2.1

```
Configurar UNA VEZ en Playground → Usar SIEMPRE en Dashboard
```

El usuario final (Dashboard) **NO configura settings**, solo **usa** lo que el administrador configuró en el Playground.

### Diferencia Clave vs Legacy

| Aspecto | Legacy | v2.1 Playground |
|---------|--------|----------------|
| **Páginas** | 13+ archivos HTML | 4 secciones Vue |
| **Organización** | Caótica | Modular y clara |
| **UI** | CSS custom inconsistente | Tailwind + DaisyUI |
| **Settings por voz** | No existe | ✅ Individual por voz |
| **Categorías** | Hardcoded | ✅ Totalmente dinámicas |
| **Testing** | Manual | Integrado en UI |
| **Type Safety** | No | ✅ 100% TypeScript |

---

## 🏗️ Arquitectura General

### Estructura de Rutas

```
/settings (Playground Root)
│
├── /settings/voices        ⭐ Voice Manager
├── /settings/audio         ⭐ Audio Config
├── /settings/categories    ⭐ Category Editor
└── /settings/ai            🔵 AI Settings (Fase 2)
```

### Stack Tecnológico

**Frontend**:
- Vue 3 + TypeScript + Composition API
- Tailwind CSS + DaisyUI
- Pinia (state management)
- Vue Router

**Backend**:
- FastAPI + SQLAlchemy
- PostgreSQL (producción) / SQLite (dev)
- Pydantic schemas
- Async endpoints

### Flujo de Datos

```
┌─────────────────────────────────────────────────────┐
│              PLAYGROUND (Admin UI)                  │
│  ┌──────────────────────────────────────────────┐   │
│  │ Voice Manager → POST/PATCH → Backend         │   │
│  │ Audio Config  → POST/PATCH → Backend         │   │
│  │ Category Edit → POST/PATCH → Backend         │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       ↓
              ┌─────────────────┐
              │   PostgreSQL    │
              │   - voices      │
              │   - categories  │
              │   - settings    │
              └────────┬────────┘
                       ↓
┌──────────────────────────────────────────────────────┐
│              DASHBOARD (User UI)                     │
│  ┌──────────────────────────────────────────────┐   │
│  │ GET /voices    → Muestra voces configuradas  │   │
│  │ GET /categories → Muestra categorías         │   │
│  │ POST /generate → Usa settings automáticos    │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

---

## 🎙️ Sección 1: Voice Manager

### Propósito

Gestionar la **biblioteca de voces ElevenLabs** con configuración individual por voz. Esta es la sección **MÁS CRÍTICA** del Playground.

### Funcionalidades

1. **CRUD de Voces**
   - ✅ Agregar nueva voz (con ElevenLabs ID)
   - ✅ Editar voz existente
   - ✅ Eliminar voz
   - ✅ Activar/desactivar voz
   - ✅ Establecer voz por defecto
   - ✅ Reordenar voces (drag & drop)

2. **Settings Individuales por Voz** ⭐ NUEVO v2.1
   - Style (0-100%): Expresividad de la voz
   - Stability (0-100%): Consistencia de la voz
   - Similarity Boost (0-100%): Similitud con voz original
   - Use Speaker Boost (boolean)

3. **Volume Adjustment por Voz** ⭐ CRÍTICO
   - Range: -20 dB a +20 dB
   - Permite compensar voces más bajas/altas
   - Ejemplo: Francisca necesita +7dB, Titi necesita -0.5dB

4. **Jingle Settings por Voz** ⭐ AVANZADO
   - Music volume (0-5x)
   - Voice volume (0-5x)
   - Duck level (0-1)
   - Intro/outro silence (segundos)

5. **Test de Voz en Tiempo Real**
   - Texto de prueba configurable
   - Preview con settings actuales
   - Player integrado

### Arquitectura Modular (Evitar Monolito)

```
/settings/voices/
├── VoiceManager.vue              # Componente principal (coordinador)
│   ├── <VoiceList />             # Lista de voces (izquierda)
│   ├── <VoiceEditor />           # Editor de voz seleccionada (derecha)
│   └── <VoiceAddModal />         # Modal para agregar voz
│
├── components/
│   ├── VoiceList.vue             # Lista drag & drop de voces
│   ├── VoiceCard.vue             # Card individual de voz
│   ├── VoiceEditor.vue           # Editor principal
│   │   ├── <BasicInfo />         # Nombre, ID, género
│   │   ├── <VoiceSettings />     # Style, stability, similarity
│   │   ├── <VolumeControl />     # Volume adjustment
│   │   ├── <JingleSettings />    # Jingle config
│   │   └── <VoiceTest />         # Test player
│   ├── VoiceAddModal.vue         # Modal agregar voz
│   └── VoiceDeleteConfirm.vue    # Confirmación de eliminación
│
├── composables/
│   └── useVoiceManager.ts        # Lógica de negocio compartida
│
└── types/
    └── voice.ts                  # TypeScript interfaces
```

### Rescatado de Legacy

Del archivo `test-voice-admin.html`:
- ✅ Sistema de ordenamiento de voces
- ✅ Volume adjustment por voz (-∞ a +∞ dB)
- ✅ Activar/desactivar voces
- ✅ Voz por defecto (is_default)
- ✅ Metadata: género, fecha agregada

**MEJORADO en v2.1**:
- ❌ Legacy: Settings globales para todas las voces
- ✅ v2.1: Settings **individuales** por voz
- ❌ Legacy: Sin jingle settings por voz
- ✅ v2.1: Jingle settings **personalizables** por voz

### API Endpoints

```typescript
// CRUD
GET    /api/v1/settings/voices           // Listar todas
GET    /api/v1/settings/voices/{id}      // Obtener una
POST   /api/v1/settings/voices           // Crear nueva
PATCH  /api/v1/settings/voices/{id}      // Actualizar
DELETE /api/v1/settings/voices/{id}      // Eliminar

// Acciones especiales
PUT    /api/v1/settings/voices/reorder   // Reordenar
POST   /api/v1/settings/voices/{id}/test // Test de voz
```

### Modelo de Datos

```python
class VoiceSettings(Base):
    __tablename__ = "voice_settings"

    # Identificación
    id: str = Column(String, primary_key=True)  # 'juan_carlos'
    name: str = Column(String, nullable=False)  # 'Juan Carlos'
    elevenlabs_id: str = Column(String, nullable=False)

    # Estado
    active: bool = Column(Boolean, default=True)
    is_default: bool = Column(Boolean, default=False)
    order: int = Column(Integer, default=0)

    # Metadata
    gender: str = Column(String)  # 'M', 'F', 'N'
    accent: str = Column(String)
    description: str = Column(Text)

    # Voice Settings ⭐ INDIVIDUAL
    style: float = Column(Float, default=50.0)  # 0-100
    stability: float = Column(Float, default=55.0)  # 0-100
    similarity_boost: float = Column(Float, default=80.0)  # 0-100
    use_speaker_boost: bool = Column(Boolean, default=True)

    # Volume ⭐ CRÍTICO
    volume_adjustment: float = Column(Float, default=0.0)  # dB

    # Jingle Settings ⭐ INDIVIDUAL (JSON)
    jingle_settings: dict = Column(JSON, nullable=True)
    # {
    #   "music_volume": 1.65,
    #   "voice_volume": 2.8,
    #   "duck_level": 0.95,
    #   "intro_silence": 7,
    #   "outro_silence": 4.5
    # }

    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🎙️ Voice Manager                             [+ Add Voice] │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│  Voice List      │         Selected Voice Editor           │
│  (Drag & Drop)   │                                          │
│                  │  ┌────────────────────────────────────┐  │
│  ┌────────────┐  │  │ Basic Info                         │  │
│  │ 👨 Juan C. │◄─┼─►│  Name: [Juan Carlos           ]    │  │
│  │ ⭐ Default │  │  │  ID:   [G4IAP30yc6c1gK0csDfu  ]    │  │
│  │ 🟢 Active  │  │  │  Gender: [M] [F] [N]              │  │
│  │ Vol: 0dB   │  │  └────────────────────────────────────┘  │
│  └────────────┘  │                                          │
│                  │  ┌────────────────────────────────────┐  │
│  ┌────────────┐  │  │ Voice Settings                     │  │
│  │ 👨 Mario   │  │  │  Style:      [====░░░░] 50%       │  │
│  │ Vol:+0.5dB │  │  │  Stability:  [=====░░░] 55%       │  │
│  └────────────┘  │  │  Similarity: [========] 80%       │  │
│                  │  │  ☑ Speaker Boost                   │  │
│  ┌────────────┐  │  └────────────────────────────────────┘  │
│  │ 👩 Francis │  │                                          │
│  │ Vol: +7dB  │  │  ┌────────────────────────────────────┐  │
│  └────────────┘  │  │ Volume Adjustment ⭐                │  │
│                  │  │  [-20dB] [======0dB=====] [+20dB] │  │
│  ┌────────────┐  │  │           Current: 0 dB            │  │
│  │ 👨 Jose M. │  │  └────────────────────────────────────┘  │
│  └────────────┘  │                                          │
│                  │  ┌────────────────────────────────────┐  │
│  ┌────────────┐  │  │ Jingle Settings (Optional)         │  │
│  │ 👩 Titi    │  │  │  Music Vol:  [===░] 1.65x         │  │
│  │ Vol:-0.5dB │  │  │  Voice Vol:  [=====] 2.8x         │  │
│  └────────────┘  │  │  Ducking:    [========] 95%       │  │
│                  │  │  Intro: 7s   Outro: 4.5s          │  │
│                  │  └────────────────────────────────────┘  │
│                  │                                          │
│                  │  ┌────────────────────────────────────┐  │
│                  │  │ Test Voice                         │  │
│                  │  │  Text: [Sample text...        ]   │  │
│                  │  │  [🔊 Test with Current Settings]  │  │
│                  │  │  <audio player here>              │  │
│                  │  └────────────────────────────────────┘  │
│                  │                                          │
│                  │  [Cancel]              [💾 Save Voice] │
└──────────────────┴──────────────────────────────────────────┘
```

---

## 🎛️ Sección 2: Audio Config

### Propósito

Configurar parámetros **globales** de audio que se aplican a todas las generaciones (a menos que una voz tenga overrides).

### Funcionalidades

#### 2.1 TTS Global Settings

- **Normalización LUFS**
  - Target LUFS: -23 a -6 dB (default: -16)
  - Enable compression (boolean)
  - Threshold, ratio, attack, release

- **Silencios Globales**
  - Intro silence: 0-15 segundos (default: 3s)
  - Outro silence: 0-20 segundos (default: 5s)

#### 2.2 Jingle Global Settings

- **Volúmenes por Defecto**
  - Music volume: 0-300% (default: 30%)
  - Voice volume: 0-500% (default: 100%)

- **Auto-Ducking**
  - Enable ducking (boolean)
  - Duck level: 0-100% (default: 20%)
  - Compresor sidechain (threshold, ratio, attack, release, makeup gain)

- **Fades**
  - Fade in: 0-5 segundos (default: 2s)
  - Fade out: 0-5 segundos (default: 2s)

#### 2.3 Music Manager

- **Upload de Música**
  - Drag & drop de archivos MP3/WAV
  - Validación de formato y bitrate
  - Preview integrado

- **Gestión de Biblioteca**
  - Lista de tracks disponibles
  - Metadata (duración, bitrate, tamaño)
  - Eliminar tracks
  - Establecer música por defecto

### Arquitectura Modular

```
/settings/audio/
├── AudioConfig.vue               # Componente principal
│   ├── <TTSSettings />           # Settings globales TTS
│   ├── <JingleSettings />        # Settings globales Jingles
│   └── <MusicManager />          # Gestión de música
│
├── components/
│   ├── TTSSettings.vue
│   │   ├── <LUFSNormalization /> # LUFS controls
│   │   └── <SilenceControls />   # Intro/outro
│   │
│   ├── JingleSettings.vue
│   │   ├── <VolumeControls />    # Música/Voz
│   │   ├── <DuckingControls />   # Auto-ducking
│   │   └── <FadeControls />      # Fades
│   │
│   └── MusicManager.vue
│       ├── <MusicUpload />       # Upload interface
│       ├── <MusicList />         # Lista de tracks
│       └── <MusicPlayer />       # Preview player
│
└── composables/
    └── useAudioConfig.ts         # Lógica compartida
```

### Rescatado de Legacy

Del archivo `tts-config.html`:
- ✅ Voice settings globales (style, stability, similarity)
- ✅ Silencios (intro, outro)
- ✅ Normalización LUFS
- ✅ Sistema de guardado remoto

Del archivo `jingle-config.html`:
- ✅ Control de volúmenes (música, voz)
- ✅ Auto-ducking con nivel configurable
- ✅ Compresor sidechain (threshold, ratio, attack, release, makeup)
- ✅ Fades (in, out)
- ✅ Música por defecto

Del archivo `music-manager.html`:
- ✅ Upload de archivos con validación
- ✅ Lista con metadata (duración, bitrate)
- ✅ Preview inline
- ✅ Eliminación con confirmación

**MEJORADO en v2.1**:
- ❌ Legacy: 3 páginas separadas
- ✅ v2.1: Una sola página con tabs
- ❌ Legacy: Sin hierarchy (global vs per-voice)
- ✅ v2.1: Jerarquía clara: Global → Override por voz

### API Endpoints

```typescript
// TTS Settings
GET   /api/v1/settings/audio/tts
PATCH /api/v1/settings/audio/tts

// Jingle Settings
GET   /api/v1/settings/audio/jingle
PATCH /api/v1/settings/audio/jingle

// Music
GET    /api/v1/settings/audio/music       // Listar tracks
POST   /api/v1/settings/audio/music       // Upload track
DELETE /api/v1/settings/audio/music/{id}  // Eliminar track
```

### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🎛️ Audio Configuration                                     │
├─────────────────────────────────────────────────────────────┤
│  [TTS Settings] [Jingle Settings] [Music Manager]          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tab 1: TTS Settings                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🎚️ Normalización LUFS                                 │  │
│  │   Target LUFS: [-16 dB] [-23 to -6]                  │  │
│  │   ☑ Enable Compression                                │  │
│  │   Threshold: [====░] -20dB                            │  │
│  │   Ratio: [===░] 4:1                                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ⏱️ Silencios Globales                                  │  │
│  │   Intro Silence:  [==░] 3 segundos                    │  │
│  │   Outro Silence:  [====░] 5 segundos                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Tab 2: Jingle Settings                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🎵 Volúmenes por Defecto                               │  │
│  │   Music Volume: [===░] 30% (0-300%)                   │  │
│  │   Voice Volume:  [==========] 100% (0-500%)           │  │
│  │   ⚠️ Estos valores se usan si la voz no tiene         │  │
│  │      jingle settings individuales                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🎚️ Auto-Ducking                                        │  │
│  │   ☑ Enable Ducking                                    │  │
│  │   Duck Level: [==░] 20% (música baja a este nivel)   │  │
│  │   Compresor: Threshold [0.02] Ratio [6:1]            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Tab 3: Music Manager                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 📤 Upload Music                                        │  │
│  │   [Drag & Drop area or click to browse]              │  │
│  │   Supported: MP3, WAV (max 10MB)                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🎵 Music Library (12 tracks)                          │  │
│  │   🎸 Cool.mp3         3:24  320kbps  [▶] [🗑️]        │  │
│  │   🎷 Smooth.mp3       4:12  256kbps  [▶] [🗑️] ⭐     │  │
│  │   🎹 Uplift.mp3       2:56  320kbps  [▶] [🗑️]        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Reset to Defaults]                      [💾 Save Config] │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Sección 3: Category Editor

### Propósito

Gestionar el sistema de **categorías totalmente dinámicas** que se usan en Library para organizar audios.

### Funcionalidades

1. **CRUD de Categorías**
   - ✅ Crear nueva categoría
   - ✅ Editar categoría existente
   - ✅ Eliminar categoría (con validación)
   - ✅ Reordenar categorías (drag & drop)

2. **Personalización Visual**
   - Nombre editable
   - Color (hex color picker)
   - Icono/Emoji
   - Activar/desactivar

3. **Preview en Tiempo Real**
   - Vista previa de cómo se verá en Library
   - Badge preview con color e icono

### Arquitectura Modular

```
/settings/categories/
├── CategoryEditor.vue            # Componente principal
│   ├── <CategoryList />          # Lista drag & drop
│   ├── <CategoryForm />          # Formulario edición
│   └── <CategoryPreview />       # Preview en tiempo real
│
├── components/
│   ├── CategoryList.vue          # Lista de categorías
│   ├── CategoryCard.vue          # Card individual
│   ├── CategoryForm.vue          # Formulario CRUD
│   ├── CategoryPreview.vue       # Preview badge
│   └── CategoryDeleteConfirm.vue # Confirmación
│
└── composables/
    └── useCategoryEditor.ts      # Lógica compartida
```

### Rescatado de Legacy

❌ **No existe en Legacy** - Las categorías estaban hardcoded

**NUEVO en v2.1**:
- ✅ Categorías completamente dinámicas
- ✅ Personalización visual (nombre, color, icono)
- ✅ Sistema de orden configurable
- ✅ Activar/desactivar categorías

### API Endpoints

```typescript
GET    /api/v1/settings/categories           // Listar todas
POST   /api/v1/settings/categories           // Crear nueva
PATCH  /api/v1/settings/categories/{id}      // Actualizar
DELETE /api/v1/settings/categories/{id}      // Eliminar
PUT    /api/v1/settings/categories/reorder   // Reordenar
```

### Modelo de Datos

```python
class Category(Base):
    __tablename__ = "categories"

    # Identificación
    id: str = Column(String, primary_key=True)  # 'pedidos'
    name: str = Column(String, nullable=False)  # 'Pedidos Listos'

    # Visual
    icon: str = Column(String, default='📦')  # Emoji o icon class
    color: str = Column(String, default='#FF4444')  # Hex color

    # Estado
    active: bool = Column(Boolean, default=True)
    order: int = Column(Integer, default=0)

    # Metadata
    description: str = Column(Text, nullable=True)
    created_at: datetime
    updated_at: datetime
```

### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  📂 Category Editor                        [+ Add Category]  │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│  Category List   │     Selected Category Editor            │
│  (Drag & Drop)   │                                          │
│                  │  ┌────────────────────────────────────┐  │
│  ┌────────────┐  │  │ Category Info                      │  │
│  │ 📦 Pedidos │◄─┼─►│  Name:  [Pedidos Listos      ]     │  │
│  │ #FF4444    │  │  │  Icon:  [📦] (emoji picker)        │  │
│  │ 🟢 Active  │  │  │  Color: [#FF4444] 🎨               │  │
│  └────────────┘  │  │  ID:    pedidos (auto-generated)   │  │
│                  │  └────────────────────────────────────┘  │
│  ┌────────────┐  │                                          │
│  │ 🎉 Promos  │  │  ┌────────────────────────────────────┐  │
│  │ #00AA00    │  │  │ Preview                            │  │
│  │ 🟢 Active  │  │  │  This is how it will look:         │  │
│  └────────────┘  │  │                                     │  │
│                  │  │  Badge: [📦 Pedidos Listos]        │  │
│  ┌────────────┐  │  │  Color: ████████ #FF4444           │  │
│  │ 📢 Avisos  │  │  └────────────────────────────────────┘  │
│  │ #0088FF    │  │                                          │
│  │ 🔴 Inactive│  │  ┌────────────────────────────────────┐  │
│  └────────────┘  │  │ Usage Statistics                   │  │
│                  │  │  Messages in this category: 42     │  │
│  ┌────────────┐  │  │  Last used: 2 hours ago            │  │
│  │ 🎵 Música  │  │  │  ⚠️ Cannot delete (has messages)   │  │
│  │ #FF8800    │  │  └────────────────────────────────────┘  │
│  └────────────┘  │                                          │
│                  │  ☑ Active                                │
│                  │  ☐ Show in Dashboard                     │
│                  │                                          │
│                  │  [Delete Category]     [💾 Save Changes]│
└──────────────────┴──────────────────────────────────────────┘
```

---

## 🤖 Sección 4: AI Settings (Fase 2)

### Propósito

Configurar contextos de **IA multi-cliente** para que Claude genere mensajes personalizados según el tipo de negocio.

### Funcionalidades

1. **Gestión de Clientes**
   - CRUD de clientes (mall, restaurant, retail, etc.)
   - Nombre y descripción del negocio

2. **Contextos Personalizados**
   - Contexto de negocio (descripción detallada)
   - Tono de comunicación (formal, casual, entusiasta)
   - Instrucciones específicas para Claude

3. **Configuración de Modelos**
   - Modelo Claude (sonnet-4, opus-4, haiku-4)
   - Temperatura
   - Max tokens

### Arquitectura Modular

```
/settings/ai/
├── AISettings.vue                # Componente principal
│   ├── <ClientList />            # Lista de clientes
│   └── <ClientEditor />          # Editor de cliente
│
├── components/
│   ├── ClientList.vue
│   ├── ClientCard.vue
│   ├── ClientEditor.vue
│   │   ├── <BasicInfo />
│   │   ├── <ContextEditor />
│   │   └── <ModelConfig />
│   └── ClientTestModal.vue       # Test con IA
│
└── composables/
    └── useAISettings.ts
```

### Rescatado de Legacy

Del archivo `claude.html`:
- ✅ Sistema multi-cliente
- ✅ Contextos personalizados por cliente
- ✅ Configuración de modelos
- ✅ Tonos y estilos

**MEJORADO en v2.1**:
- ✅ UI más clara y organizada
- ✅ TypeScript type safety
- ✅ Validación de contextos
- ✅ Testing integrado

### API Endpoints

```typescript
GET    /api/v1/settings/ai/clients           // Listar clientes
POST   /api/v1/settings/ai/clients           // Crear cliente
PATCH  /api/v1/settings/ai/clients/{id}      // Actualizar
DELETE /api/v1/settings/ai/clients/{id}      // Eliminar
POST   /api/v1/settings/ai/clients/{id}/test // Test con IA
```

---

## 🔄 Migración desde Legacy

### Archivos Legacy a Migrar

```
Legacy System → MediaFlowDemo v2.1
─────────────────────────────────────────────────────────
/var/www/casa/src/api/data/voices-config.json
  → PostgreSQL tabla: voice_settings
  → Script: backend/app/db/migrate_voices.py

/var/www/casa/stable-releases/configs/jingle-config.json
  → PostgreSQL tabla: audio_settings (jingle)
  → Script: backend/app/db/migrate_audio_settings.py

/var/www/casa/stable-releases/configs/api-config.json
  → PostgreSQL tabla: audio_settings (tts)
  → Script: backend/app/db/migrate_audio_settings.py

Categorías: NO EXISTEN en legacy (hardcoded)
  → Crear categorías por defecto en seed
  → Ejemplo: pedidos, promos, avisos, musica
```

### Script de Migración

```python
# backend/app/db/migrate_legacy_config.py

import json
from pathlib import Path
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.voice_settings import VoiceSettings
from app.models.audio_settings import AudioSettings

async def migrate_voices_from_legacy():
    """
    Migra voices-config.json del sistema legacy a PostgreSQL
    """
    # Leer JSON legacy
    legacy_path = Path("/var/www/casa/src/api/data/voices-config.json")
    with open(legacy_path) as f:
        legacy_data = json.load(f)

    async with AsyncSessionLocal() as session:
        for voice_key, voice_data in legacy_data["voices"].items():
            # Convertir scales legacy (0-1) a v2.1 (0-100)
            voice = VoiceSettings(
                id=voice_key,
                name=voice_data["label"],
                elevenlabs_id=voice_data["id"],
                active=voice_data["active"],
                is_default=voice_data.get("is_default", False),
                order=voice_data["order"],
                gender=voice_data.get("gender"),
                volume_adjustment=voice_data.get("volume_adjustment", 0),
                # Legacy usaba settings globales, v2.1 usa individuales
                style=50.0,  # Default
                stability=55.0,  # Default
                similarity_boost=80.0,  # Default
            )
            session.add(voice)

        await session.commit()
        print("✅ Voces migradas exitosamente")
```

### Validación Post-Migración

```bash
# Verificar que todas las voces se migraron
SELECT COUNT(*) FROM voice_settings;  # Debe ser >= 5

# Verificar voces activas
SELECT id, name, volume_adjustment
FROM voice_settings
WHERE active = true;

# Verificar voz por defecto
SELECT id, name
FROM voice_settings
WHERE is_default = true;  # Debe ser 1
```

---

## 📅 Cronología de Implementación

### Timeline General: 5 días

```
Día 1: Backend APIs + Migraciones
Día 2: Voice Manager UI
Día 3: Audio Config UI
Día 4: Category Editor UI
Día 5: Testing + Integration
```

### Detalle por Día

#### **Día 1: Backend APIs + Migraciones** (8 horas)

**Mañana (4h)**:
- ✅ Crear endpoints de settings
  - `/api/v1/settings/voices/*`
  - `/api/v1/settings/audio/*`
  - `/api/v1/settings/categories/*`
- ✅ Schemas Pydantic para requests/responses
- ✅ Testing con pytest

**Tarde (4h)**:
- ✅ Script de migración de legacy config
- ✅ Seed de categorías por defecto
- ✅ Validación de migración
- ✅ Documentación API

**Entregable**: Backend completamente funcional con datos migrados

---

#### **Día 2: Voice Manager UI** (8 horas)

**Mañana (4h)**:
- ✅ VoiceManager.vue (componente principal)
- ✅ VoiceList.vue (lista drag & drop)
- ✅ VoiceCard.vue (card de voz)
- ✅ Composable useVoiceManager.ts

**Tarde (4h)**:
- ✅ VoiceEditor.vue (editor completo)
  - BasicInfo component
  - VoiceSettings component
  - VolumeControl component
  - JingleSettings component
- ✅ VoiceAddModal.vue
- ✅ VoiceTest.vue (test player)

**Entregable**: Voice Manager completamente funcional

---

#### **Día 3: Audio Config UI** (8 horas)

**Mañana (4h)**:
- ✅ AudioConfig.vue (componente principal con tabs)
- ✅ TTSSettings.vue
  - LUFSNormalization component
  - SilenceControls component
- ✅ Integración con backend

**Tarde (4h)**:
- ✅ JingleSettings.vue
  - VolumeControls component
  - DuckingControls component
  - FadeControls component
- ✅ MusicManager.vue
  - MusicUpload component
  - MusicList component
  - MusicPlayer component

**Entregable**: Audio Config completamente funcional

---

#### **Día 4: Category Editor UI** (6 horas)

**Mañana (3h)**:
- ✅ CategoryEditor.vue (componente principal)
- ✅ CategoryList.vue (drag & drop)
- ✅ CategoryCard.vue
- ✅ Composable useCategoryEditor.ts

**Tarde (3h)**:
- ✅ CategoryForm.vue (CRUD)
- ✅ CategoryPreview.vue (preview en tiempo real)
- ✅ CategoryDeleteConfirm.vue
- ✅ Color picker integration

**Entregable**: Category Editor completamente funcional

---

#### **Día 5: Testing + Integration** (8 horas)

**Mañana (4h)**:
- ✅ Testing E2E de Playground
  - Voice Manager flows
  - Audio Config flows
  - Category Editor flows
- ✅ Testing de integración Playground → Dashboard
- ✅ Verificar que settings se aplican correctamente

**Tarde (4h)**:
- ✅ UI/UX polish
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states
- ✅ Success notifications
- ✅ Documentación de usuario

**Entregable**: Playground production-ready

---

## 🛠️ Implementación Paso a Paso

### PASO 1: Backend Settings APIs

#### 1.1 Crear Archivo de Endpoints

```bash
touch /var/www/mediaflow-v2/backend/app/api/v1/endpoints/settings.py
```

```python
# backend/app/api/v1/endpoints/settings.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from app.db.session import get_db
from app.models.voice_settings import VoiceSettings
from app.models.category import Category
from app.schemas.settings import (
    VoiceSettingsResponse,
    VoiceSettingsCreate,
    VoiceSettingsUpdate,
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
)

router = APIRouter(prefix="/settings", tags=["settings"])

# ==================== VOICES ====================

@router.get("/voices", response_model=List[VoiceSettingsResponse])
async def get_all_voices(db: AsyncSession = Depends(get_db)):
    """Get all voices"""
    result = await db.execute(
        select(VoiceSettings).order_by(VoiceSettings.order)
    )
    voices = result.scalars().all()
    return voices


@router.get("/voices/{voice_id}", response_model=VoiceSettingsResponse)
async def get_voice(voice_id: str, db: AsyncSession = Depends(get_db)):
    """Get single voice"""
    result = await db.execute(
        select(VoiceSettings).filter(VoiceSettings.id == voice_id)
    )
    voice = result.scalar_one_or_none()

    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    return voice


@router.post("/voices", response_model=VoiceSettingsResponse)
async def create_voice(
    voice_data: VoiceSettingsCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new voice"""
    # Check if ID already exists
    result = await db.execute(
        select(VoiceSettings).filter(VoiceSettings.id == voice_data.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Voice ID already exists")

    # Create voice
    voice = VoiceSettings(**voice_data.model_dump())
    db.add(voice)
    await db.commit()
    await db.refresh(voice)

    return voice


@router.patch("/voices/{voice_id}", response_model=VoiceSettingsResponse)
async def update_voice(
    voice_id: str,
    voice_data: VoiceSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update existing voice"""
    result = await db.execute(
        select(VoiceSettings).filter(VoiceSettings.id == voice_id)
    )
    voice = result.scalar_one_or_none()

    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    # Update fields
    update_data = voice_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voice, field, value)

    await db.commit()
    await db.refresh(voice)

    return voice


@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str, db: AsyncSession = Depends(get_db)):
    """Delete voice"""
    result = await db.execute(
        select(VoiceSettings).filter(VoiceSettings.id == voice_id)
    )
    voice = result.scalar_one_or_none()

    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    # Don't allow deleting default voice
    if voice.is_default:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete default voice. Set another voice as default first."
        )

    await db.delete(voice)
    await db.commit()

    return {"success": True, "message": f"Voice {voice_id} deleted"}


# ==================== CATEGORIES ====================

@router.get("/categories", response_model=List[CategoryResponse])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    """Get all categories"""
    result = await db.execute(
        select(Category).order_by(Category.order)
    )
    categories = result.scalars().all()
    return categories


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new category"""
    category = Category(**category_data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update existing category"""
    result = await db.execute(
        select(Category).filter(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete category"""
    result = await db.execute(
        select(Category).filter(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # TODO: Check if category has associated audio messages
    # and prevent deletion if it does

    await db.delete(category)
    await db.commit()

    return {"success": True, "message": f"Category {category_id} deleted"}
```

#### 1.2 Crear Schemas Pydantic

```bash
touch /var/www/mediaflow-v2/backend/app/schemas/settings.py
```

```python
# backend/app/schemas/settings.py

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

# ==================== VOICE SETTINGS ====================

class VoiceSettingsBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    elevenlabs_id: str = Field(..., min_length=1)
    active: bool = True
    is_default: bool = False
    order: int = 0
    gender: Optional[str] = None
    accent: Optional[str] = None
    description: Optional[str] = None
    style: float = Field(50.0, ge=0, le=100)
    stability: float = Field(55.0, ge=0, le=100)
    similarity_boost: float = Field(80.0, ge=0, le=100)
    use_speaker_boost: bool = True
    volume_adjustment: float = Field(0.0, ge=-20, le=20)
    jingle_settings: Optional[Dict] = None


class VoiceSettingsCreate(VoiceSettingsBase):
    id: str = Field(..., min_length=1, max_length=50)


class VoiceSettingsUpdate(BaseModel):
    name: Optional[str] = None
    elevenlabs_id: Optional[str] = None
    active: Optional[bool] = None
    is_default: Optional[bool] = None
    order: Optional[int] = None
    gender: Optional[str] = None
    accent: Optional[str] = None
    description: Optional[str] = None
    style: Optional[float] = Field(None, ge=0, le=100)
    stability: Optional[float] = Field(None, ge=0, le=100)
    similarity_boost: Optional[float] = Field(None, ge=0, le=100)
    use_speaker_boost: Optional[bool] = None
    volume_adjustment: Optional[float] = Field(None, ge=-20, le=20)
    jingle_settings: Optional[Dict] = None


class VoiceSettingsResponse(VoiceSettingsBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== CATEGORIES ====================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = Field("📁", max_length=10)
    color: str = Field("#666666", pattern=r"^#[0-9A-Fa-f]{6}$")
    active: bool = True
    order: int = 0
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    id: str = Field(..., min_length=1, max_length=50)


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None
    order: Optional[int] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

#### 1.3 Registrar Router

```python
# backend/app/api/v1/api.py

from fastapi import APIRouter
from app.api.v1.endpoints import audio, ai, settings  # ← Add settings

api_router = APIRouter()

api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])  # ← Add this
```

#### 1.4 Testing

```bash
# Test endpoints
curl http://localhost:3001/api/v1/settings/voices
curl http://localhost:3001/api/v1/settings/categories
```

---

### PASO 2: Voice Manager UI

#### 2.1 Crear Estructura de Componentes

```bash
mkdir -p /var/www/mediaflow-v2/frontend/src/components/settings/voices
mkdir -p /var/www/mediaflow-v2/frontend/src/composables
```

#### 2.2 Composable useVoiceManager

```typescript
// frontend/src/composables/useVoiceManager.ts

import { ref, computed } from 'vue'
import { api } from '@/api/client'
import type { Voice } from '@/types/audio'

export function useVoiceManager() {
  const voices = ref<Voice[]>([])
  const selectedVoice = ref<Voice | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Load all voices
  const loadVoices = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/settings/voices')
      voices.value = response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to load voices'
      console.error('Failed to load voices:', e)
    } finally {
      isLoading.value = false
    }
  }

  // Create voice
  const createVoice = async (voiceData: Partial<Voice>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post('/settings/voices', voiceData)
      voices.value.push(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to create voice'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // Update voice
  const updateVoice = async (voiceId: string, updates: Partial<Voice>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.patch(`/settings/voices/${voiceId}`, updates)

      // Update in local array
      const index = voices.value.findIndex(v => v.id === voiceId)
      if (index !== -1) {
        voices.value[index] = response.data
      }

      // Update selected if it's the one being edited
      if (selectedVoice.value?.id === voiceId) {
        selectedVoice.value = response.data
      }

      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to update voice'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // Delete voice
  const deleteVoice = async (voiceId: string) => {
    isLoading.value = true
    error.value = null

    try {
      await api.delete(`/settings/voices/${voiceId}`)

      // Remove from local array
      voices.value = voices.value.filter(v => v.id !== voiceId)

      // Clear selection if deleted
      if (selectedVoice.value?.id === voiceId) {
        selectedVoice.value = null
      }
    } catch (e: any) {
      error.value = e.message || 'Failed to delete voice'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // Test voice
  const testVoice = async (voiceId: string, text: string) => {
    try {
      const response = await api.post(`/settings/voices/${voiceId}/test`, {
        text
      })
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to test voice'
      throw e
    }
  }

  return {
    voices,
    selectedVoice,
    isLoading,
    error,
    loadVoices,
    createVoice,
    updateVoice,
    deleteVoice,
    testVoice,
  }
}
```

#### 2.3 VoiceManager.vue (Principal)

```vue
<!-- frontend/src/components/settings/voices/VoiceManager.vue -->

<template>
  <div class="voice-manager min-h-screen bg-base-100 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-3xl font-bold text-primary">🎙️ Voice Manager</h1>
        <p class="text-sm text-base-content/70 mt-1">
          Gestiona voces y sus configuraciones individuales
        </p>
      </div>
      <button @click="showAddModal = true" class="btn btn-primary">
        + Agregar Voz
      </button>
    </div>

    <!-- Main Content -->
    <div class="grid lg:grid-cols-3 gap-6">
      <!-- Left: Voice List -->
      <div class="lg:col-span-1">
        <VoiceList
          :voices="voices"
          :selected-voice="selectedVoice"
          @select-voice="handleSelectVoice"
          @delete-voice="handleDeleteVoice"
        />
      </div>

      <!-- Right: Voice Editor -->
      <div class="lg:col-span-2">
        <VoiceEditor
          v-if="selectedVoice"
          :voice="selectedVoice"
          @update-voice="handleUpdateVoice"
          @test-voice="handleTestVoice"
        />
        <div v-else class="card bg-base-200 shadow-xl">
          <div class="card-body items-center text-center py-12">
            <p class="text-base-content/50">
              Selecciona una voz de la lista para editarla
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Voice Modal -->
    <VoiceAddModal
      v-if="showAddModal"
      @close="showAddModal = false"
      @create="handleCreateVoice"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useVoiceManager } from '@/composables/useVoiceManager'
import VoiceList from './components/VoiceList.vue'
import VoiceEditor from './components/VoiceEditor.vue'
import VoiceAddModal from './components/VoiceAddModal.vue'

const {
  voices,
  selectedVoice,
  isLoading,
  error,
  loadVoices,
  createVoice,
  updateVoice,
  deleteVoice,
  testVoice,
} = useVoiceManager()

const showAddModal = ref(false)

const handleSelectVoice = (voice: any) => {
  selectedVoice.value = voice
}

const handleUpdateVoice = async (updates: any) => {
  if (!selectedVoice.value) return

  try {
    await updateVoice(selectedVoice.value.id, updates)
    // Show success toast
  } catch (e) {
    // Show error toast
  }
}

const handleDeleteVoice = async (voiceId: string) => {
  if (!confirm('¿Estás seguro de eliminar esta voz?')) return

  try {
    await deleteVoice(voiceId)
    // Show success toast
  } catch (e) {
    // Show error toast
  }
}

const handleCreateVoice = async (voiceData: any) => {
  try {
    const newVoice = await createVoice(voiceData)
    showAddModal.value = false
    selectedVoice.value = newVoice
    // Show success toast
  } catch (e) {
    // Show error toast
  }
}

const handleTestVoice = async (text: string) => {
  if (!selectedVoice.value) return

  try {
    const result = await testVoice(selectedVoice.value.id, text)
    // Play audio result
  } catch (e) {
    // Show error toast
  }
}

onMounted(() => {
  loadVoices()
})
</script>
```

**CONTINÚA EN LOS SIGUIENTES PASOS...**

---

## 📊 Métricas de Éxito

### Funcionales
- ✅ Voice Manager: CRUD completo funcionando
- ✅ Settings individuales por voz aplicándose correctamente
- ✅ Audio Config: Todos los parámetros ajustables
- ✅ Category Editor: Categorías dinámicas funcionando

### Técnicos
- ✅ 100% TypeScript sin errores
- ✅ Componentes modulares < 300 líneas cada uno
- ✅ API responses < 200ms
- ✅ Zero errores de validación

### UX
- ✅ UI consistente con Tailwind + DaisyUI
- ✅ Loading states en todas las acciones
- ✅ Error handling claro y útil
- ✅ Success notifications
- ✅ Responsive design completo

---

## 🎯 Conclusión

Este documento define la **arquitectura completa y modular del Playground v2.1**. La clave del éxito está en:

1. **Modularidad**: Componentes pequeños y reutilizables (evitar monolitos)
2. **Separación clara**: Backend APIs → Frontend Components → User Actions
3. **Migración cuidadosa**: Rescatar lo bueno del legacy, mejorar lo malo
4. **Implementación incremental**: Día por día, feature por feature

El Playground es el **corazón administrativo** del sistema. Una vez implementado correctamente, el Dashboard podrá funcionar al 100% con configuraciones reales y profesionales.

---

**Próximos pasos**: Comenzar implementación según cronología definida.

**Estado**: ✅ Documento aprobado - Listo para desarrollo

**Última actualización**: 2025-11-23
