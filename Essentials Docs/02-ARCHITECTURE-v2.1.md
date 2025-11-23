# 🏗️ MediaFlowDemo - Arquitectura v2.1 (ACTUALIZADA)

**Proyecto:** MediaFlowDemo - Sistema de Radio Automatizada con TTS e IA
**Versión:** 2.1.0
**Fecha:** 2025-11-22
**Stack:** FastAPI + Vue 3 + Python 3.11 + TypeScript + Tailwind CSS

> **CAMBIOS v2.1:**
> - ✅ Mensajes recientes integrados en Dashboard
> - ✅ Categorías solo en Library (no en Dashboard)
> - ✅ Custom voice settings por voz individual
> - ✅ Categorías configurables (nombres, colores, iconos)
> - ✅ Sistema de favoritos con ⭐ en Library
> - ✅ Editar mensaje de Library → Dashboard (copia)
> - ✅ Vista Lista + Grid en Library
> - ✅ Control granular de volúmenes en Playground

---

## 📌 Propósito del Documento

Este documento define la **arquitectura actualizada v2.1** de MediaFlowDemo, incorporando feedback crítico sobre flujo de trabajo, configuración granular de voces, y flexibilidad multi-cliente.

---

## 🎯 Visión General del Sistema

MediaFlowDemo v2 es una **aplicación web full-stack** que permite:

1. ✅ **Generar mensajes TTS** con ElevenLabs + Claude AI
2. ✅ **Configuración individual por voz** (style, stability, similarity)
3. ✅ **Gestionar biblioteca** con favoritos y vistas múltiples
4. ✅ **Categorías personalizables** por cliente
5. ✅ **Control granular de volúmenes** desde Playground
6. ✅ **Programar reproducción** automática
7. ✅ **Reproducir en vivo** con ducking profesional

---

## 🛠️ Stack Tecnológico

### **Backend**

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.11+ | Lenguaje principal |
| **FastAPI** | 0.104+ | Framework web async |
| **Pydantic** | 2.5+ | Validación de datos |
| **SQLAlchemy** | 2.0+ | ORM + migrations |
| **PostgreSQL** | 15+ | DB producción |
| **pydub** | 0.25+ | Procesamiento de audio |
| **FFmpeg** | 6.0+ | Normalización LUFS |

### **Frontend**

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Vue 3** | 3.3+ | Framework UI |
| **TypeScript** | 5.0+ | Type safety |
| **Pinia** | 2.1+ | State management |
| **Tailwind CSS** | 3.4+ | Utility CSS |
| **DaisyUI** | 4.0+ | Componentes |

---

## 📁 Estructura de Directorios (Actualizada)

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── audio.py
│   │           ├── library.py
│   │           ├── settings.py      # ⭐ NUEVO: Voice settings
│   │           └── categories.py    # ⭐ NUEVO: Categorías dinámicas
│   │
│   ├── services/
│   │   ├── tts/
│   │   │   ├── elevenlabs.py
│   │   │   └── voice_manager.py    # ⭐ NUEVO: Settings por voz
│   │   └── config/
│   │       ├── voice_config.py     # ⭐ NUEVO: Custom settings
│   │       └── category_config.py  # ⭐ NUEVO: Categorías personalizables
│   │
│   └── models/
│       ├── voice_settings.py       # ⭐ NUEVO: Settings individuales
│       └── categories.py           # ⭐ NUEVO: Categorías dinámicas

frontend/
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── MessageGenerator.vue    # SIN selector de categoría
│   │   │   ├── RecentMessages.vue      # ⭐ IMPORTANTE: En Dashboard
│   │   │   └── VoiceSelector.vue       # Usa settings predefinidos
│   │   │
│   │   ├── library/
│   │   │   ├── LibraryGrid.vue         # Vista Grid
│   │   │   ├── LibraryList.vue         # ⭐ NUEVO: Vista Lista
│   │   │   ├── ViewToggle.vue          # ⭐ NUEVO: Toggle Grid/List
│   │   │   ├── CategoryManager.vue     # ⭐ NUEVO: Asignar categoría
│   │   │   ├── FavoriteButton.vue      # ⭐ NUEVO: Marcar favoritos
│   │   │   └── EditInDashboard.vue     # ⭐ NUEVO: Copiar a Dashboard
│   │   │
│   │   └── settings/
│   │       ├── VoiceManager.vue        # ⭐ MEJORADO: Settings por voz
│   │       ├── CategoryEditor.vue      # ⭐ NUEVO: Editor de categorías
│   │       └── VolumeControls.vue      # ⭐ MEJORADO: Control granular
```

---

## 🎯 MÓDULOS ACTUALIZADOS

---

## 5.1 📋 Dashboard (Generador de TTS) - ACTUALIZADO

### **Cambios Principales v2.1**
- ❌ **REMOVIDO**: Selector de categoría (se asigna en Library)
- ✅ **AGREGADO**: Mensajes recientes siempre visible
- ✅ **MEJORADO**: Voces usan settings predefinidos automáticamente

### **Componentes Vue (Actualizado)**

```
Dashboard.vue
├── MessageGenerator.vue          # SIN CategorySelector
│   └── CharacterCounter.vue
│
├── VoiceSelector.vue             # Aplica settings automáticos
│   └── VoicePreview.vue         # Preview con settings de la voz
│
├── JingleControls.vue
│   ├── MusicSelector.vue
│   └── VolumeDisplay.vue        # Solo muestra, no edita
│
├── AISuggestions.vue
│   └── SuggestionCard.vue
│
├── AudioPreview.vue
│   ├── AudioPlayer.vue
│   └── ActionButtons.vue        # Sin "Categorizar"
│
└── RecentMessages.vue            # ⭐ SIEMPRE VISIBLE
    ├── MessageListItem.vue
    └── QuickActions.vue          # Play, Save, Send
```

### **Flujo Actualizado**

```
1. Dashboard muestra Mensajes Recientes al cargar
   ↓
2. Usuario escribe/genera con IA
   ↓
3. Selecciona voz
   → Settings automáticos aplicados:
     • Juan Carlos: Style 15%, Stability 100%, Similarity 50%
     • María: Style 50%, Stability 100%, Similarity 40%
     • (Configurados en Playground previamente)
   ↓
4. Genera audio (SIN categoría)
   ↓
5. Acciones disponibles:
   a) "Guardar en Biblioteca" → Se categoriza allá
   b) "Enviar al Player" → Directo, sin categoría
   c) "Programar" → Se categoriza en Calendar
```

### **API Actualizada**

```typescript
// Generar audio (sin categoría)
POST /api/audio/generate
Request: {
  text: string
  voice_id: string  // La voz trae sus settings
  // NO category aquí
  add_jingles?: boolean
  music_file?: string
  // NO voice_settings manuales (vienen de config)
}

// El backend automáticamente aplica:
// - voice_settings específicos de esa voz
// - volume_adjustment de esa voz
// - jingle settings globales
```

---

## 5.2 📚 Library (Biblioteca) - MEJORADO

### **Cambios Principales v2.1**
- ✅ **AGREGADO**: Vista Lista además de Grid
- ✅ **AGREGADO**: Sistema de favoritos con ⭐
- ✅ **AGREGADO**: Editar en Dashboard (copia)
- ✅ **MEJORADO**: Categorización aquí, no en Dashboard

### **Componentes Vue (Actualizado)**

```
Library.vue
├── ViewToggle.vue                # ⭐ Toggle Grid/List
│
├── SearchBar.vue
├── FilterPanel.vue
│   ├── CategoryFilter.vue        # Incluye "⭐ Favoritos"
│   └── DateRangeFilter.vue
│
├── LibraryGrid.vue                # Vista Grid (cards)
│   └── MessageCard.vue
│       ├── FavoriteButton.vue    # ⭐ Estrella
│       ├── CategoryBadge.vue     # Muestra/edita categoría
│       ├── AudioPlayer.vue
│       └── ActionMenu.vue
│           ├── EditInDashboard   # ⭐ "Editar copia"
│           ├── SendToPlayer
│           ├── Schedule
│           └── Delete
│
└── LibraryList.vue                # ⭐ Vista Lista (tabla)
    └── MessageRow.vue
        ├── FavoriteButton.vue
        ├── CategoryDropdown.vue  # Cambio rápido
        ├── PlayButton.vue
        └── ActionsDropdown.vue
```

### **Flujo de Favoritos**

```typescript
// Modelo actualizado
interface AudioMessage {
  id: number
  filename: string
  display_name: string
  category?: string        // Puede ser null al crear
  is_favorite: boolean     // ⭐ NUEVO
  // ...
}

// Filtro especial
GET /api/library?filter=favorites
// Retorna solo is_favorite=true de TODAS las categorías
```

### **Flujo "Editar en Dashboard"**

```
1. Usuario en Library selecciona mensaje
   ↓
2. Click "Editar en Dashboard"
   ↓
3. Sistema:
   a) Copia el texto del mensaje
   b) Navega a Dashboard
   c) Pre-llena el textarea
   d) Mantiene la misma voz
   e) NO modifica el original
   ↓
4. Usuario edita y genera nuevo
   ↓
5. Nuevo mensaje independiente creado
```

### **Vista Lista (Nueva)**

```vue
<!-- LibraryList.vue -->
<template>
  <table class="table table-zebra">
    <thead>
      <tr>
        <th>⭐</th>
        <th>Nombre</th>
        <th>Categoría</th>
        <th>Duración</th>
        <th>Fecha</th>
        <th>Acciones</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="msg in messages">
        <td><FavoriteButton :message="msg" /></td>
        <td>{{ msg.display_name }}</td>
        <td><CategoryDropdown :message="msg" /></td>
        <td>{{ msg.duration }}s</td>
        <td>{{ formatDate(msg.created_at) }}</td>
        <td>
          <ActionsDropdown :message="msg" />
        </td>
      </tr>
    </tbody>
  </table>
</template>
```

---

## 5.3 ⚙️ Settings/Playground - CRÍTICO

### **Cambios Principales v2.1**
- ✅ **AGREGADO**: Custom settings por voz individual
- ✅ **AGREGADO**: Editor de categorías (nombres, colores, iconos)
- ✅ **MEJORADO**: Control granular de volúmenes
- ✅ **IMPORTANTE**: Todo se aplica automáticamente en Dashboard

### **1. Voice Settings Manager** ⭐ CRÍTICO

```typescript
// Configuración por voz individual
interface VoiceConfig {
  id: string              // 'juan_carlos'
  name: string            // 'Juan Carlos'
  elevenlabs_id: string   // 'G4IAP30yc6c1gK0csDfu'
  active: boolean
  is_default: boolean
  order: number

  // ⭐ NUEVO: Settings específicos de esta voz
  voice_settings: {
    style: number         // 0-100 (ej: 15 para formal, 50 para casual)
    stability: number     // 0-100 (ej: 100 para consistente)
    similarity_boost: number  // 0-100 (ej: 40)
    use_speaker_boost: boolean
  }

  // ⭐ CRÍTICO: Ajuste de volumen
  volume_adjustment: number  // dB (-∞ to +∞)

  // ⭐ NUEVO: Settings de jingle para esta voz
  jingle_settings?: {
    music_volume: number     // 1.65 default
    voice_volume: number     // 2.8 default
    duck_level: number       // 0.95 default
    intro_silence: number    // 3 segundos
    outro_silence: number    // 5 segundos
  }
}
```

### **UI de Voice Manager**

```vue
<!-- settings/VoiceManager.vue -->
<template>
  <div class="voice-manager">
    <h2>Configuración de Voces</h2>

    <!-- Lista de voces -->
    <div v-for="voice in voices" class="voice-card">
      <div class="voice-header">
        <h3>{{ voice.name }}</h3>
        <toggle v-model="voice.active" />
      </div>

      <!-- ⭐ Settings específicos de voz -->
      <div class="voice-settings">
        <h4>Configuración de Voz</h4>

        <label>Estilo ({{ voice.voice_settings.style }}%)</label>
        <input type="range" v-model="voice.voice_settings.style"
               min="0" max="100" />
        <small>15% = Formal, 50% = Casual, 80% = Expresivo</small>

        <label>Estabilidad ({{ voice.voice_settings.stability }}%)</label>
        <input type="range" v-model="voice.voice_settings.stability"
               min="0" max="100" />
        <small>100% = Consistente, 50% = Variable</small>

        <label>Similitud ({{ voice.voice_settings.similarity_boost }}%)</label>
        <input type="range" v-model="voice.voice_settings.similarity_boost"
               min="0" max="100" />
      </div>

      <!-- ⭐ Control de volumen crítico -->
      <div class="volume-control">
        <h4>Ajuste de Volumen</h4>
        <label>Volumen ({{ voice.volume_adjustment }} dB)</label>
        <input type="range" v-model="voice.volume_adjustment"
               min="-20" max="20" step="0.5" />
        <button @click="voice.volume_adjustment = 0">Reset</button>
      </div>

      <!-- ⭐ Jingle settings por voz -->
      <div class="jingle-settings" v-if="voice.jingle_settings">
        <h4>Configuración de Jingle</h4>

        <label>Volumen Música</label>
        <input type="number" v-model="voice.jingle_settings.music_volume"
               step="0.1" />

        <label>Volumen Voz</label>
        <input type="number" v-model="voice.jingle_settings.voice_volume"
               step="0.1" />

        <label>Ducking</label>
        <input type="range" v-model="voice.jingle_settings.duck_level"
               min="0" max="1" step="0.05" />
      </div>

      <!-- Test button -->
      <button @click="testVoice(voice)" class="btn btn-primary">
        🔊 Probar Voz con Settings
      </button>
    </div>

    <!-- Guardar todo -->
    <button @click="saveAllVoices" class="btn btn-success">
      💾 Guardar Configuración
    </button>
  </div>
</template>
```

### **2. Category Editor** ⭐ NUEVO

```typescript
// Categorías totalmente configurables
interface CategoryConfig {
  id: string           // 'pedidos'
  name: string         // 'Pedidos Listos' (personalizable)
  icon: string         // '📦' (emoji o icon class)
  color: string        // '#FF4444' (hex color)
  order: number        // Orden de aparición
  active: boolean      // Si está disponible
}
```

```vue
<!-- settings/CategoryEditor.vue -->
<template>
  <div class="category-editor">
    <h2>Configuración de Categorías</h2>

    <div v-for="cat in categories" class="category-item">
      <input v-model="cat.icon" class="icon-input" />
      <input v-model="cat.name" class="name-input" />
      <input type="color" v-model="cat.color" />
      <toggle v-model="cat.active" />
      <button @click="moveUp(cat)">↑</button>
      <button @click="moveDown(cat)">↓</button>
      <button @click="deleteCategory(cat)">🗑️</button>
    </div>

    <!-- Agregar nueva categoría -->
    <button @click="addCategory" class="btn btn-primary">
      + Agregar Categoría
    </button>

    <button @click="saveCategories" class="btn btn-success">
      💾 Guardar Categorías
    </button>
  </div>
</template>
```

### **3. Volume Control Panel** ⭐ MEJORADO

```vue
<!-- settings/VolumeControls.vue -->
<template>
  <div class="volume-panel">
    <h2>Control Maestro de Volúmenes</h2>

    <!-- Global TTS -->
    <div class="section">
      <h3>TTS Global</h3>
      <label>Normalización LUFS Target ({{ globalSettings.tts.target_lufs }} dB)</label>
      <input type="range" v-model="globalSettings.tts.target_lufs"
             min="-30" max="-6" />

      <label>Volumen de Salida Global</label>
      <input type="range" v-model="globalSettings.tts.output_volume"
             min="0.5" max="2" step="0.1" />
    </div>

    <!-- Global Jingles -->
    <div class="section">
      <h3>Jingles Global</h3>
      <label>Música Default ({{ globalSettings.jingle.music_volume }})</label>
      <input type="range" v-model="globalSettings.jingle.music_volume"
             min="0" max="3" step="0.1" />

      <label>Voz Default ({{ globalSettings.jingle.voice_volume }})</label>
      <input type="range" v-model="globalSettings.jingle.voice_volume"
             min="0" max="5" step="0.1" />

      <label>Ducking ({{ globalSettings.jingle.duck_level }})</label>
      <input type="range" v-model="globalSettings.jingle.duck_level"
             min="0" max="1" step="0.05" />
    </div>

    <!-- Per-Voice Overrides -->
    <div class="section">
      <h3>Ajustes por Voz</h3>
      <p class="info">
        ℹ️ Los ajustes individuales por voz sobrescriben estos valores globales
      </p>
      <button @click="showVoiceManager" class="btn btn-secondary">
        Configurar Voces Individuales →
      </button>
    </div>
  </div>
</template>
```

---

## 🔄 Flujo de Configuración → Dashboard

### **Cómo se aplican los settings automáticamente:**

```python
# backend/app/services/tts/voice_manager.py

class VoiceManager:
    def __init__(self):
        self.voices = self.load_voice_configs()

    def get_voice_with_settings(self, voice_id: str):
        """Obtiene voz con TODOS sus settings predefinidos"""
        voice = self.voices.get(voice_id)

        return {
            'elevenlabs_id': voice['elevenlabs_id'],
            'voice_settings': voice['voice_settings'],  # Custom por voz
            'volume_adjustment': voice['volume_adjustment'],  # dB adjustment
            'jingle_settings': voice.get('jingle_settings', self.get_default_jingle())
        }

    async def generate_with_voice(self, text: str, voice_id: str):
        """Genera TTS con settings automáticos"""
        voice_config = self.get_voice_with_settings(voice_id)

        # 1. Generar TTS con settings específicos
        audio = await elevenlabs.generate(
            text=text,
            voice_id=voice_config['elevenlabs_id'],
            voice_settings=voice_config['voice_settings']  # Auto-aplicados
        )

        # 2. Aplicar volume adjustment
        if voice_config['volume_adjustment'] != 0:
            audio = self.adjust_volume(audio, voice_config['volume_adjustment'])

        # 3. Si tiene jingle, usar sus settings específicos
        if has_jingle:
            audio = await self.mix_jingle(
                audio,
                music_volume=voice_config['jingle_settings']['music_volume'],
                voice_volume=voice_config['jingle_settings']['voice_volume'],
                duck_level=voice_config['jingle_settings']['duck_level']
            )

        return audio
```

### **En el Dashboard (Frontend):**

```typescript
// El usuario SOLO ve:
// 1. Selector de voz (sin settings manuales)
// 2. Toggle de música (sin controles de volumen)

// Todo lo demás viene del Playground:
const generateAudio = async () => {
  const response = await api.generate({
    text: message.value,
    voice_id: selectedVoice.value  // ← Esto es TODO, trae sus settings
    // NO voice_settings
    // NO volume controls
    // NO category
  })
}

// El backend aplica automáticamente:
// - voice_settings de esa voz
// - volume_adjustment de esa voz
// - jingle_settings de esa voz (si aplica)
```

---

## 📊 Tabla de Decisiones de Diseño v2.1

| Característica | Ubicación | Razón |
|----------------|-----------|--------|
| **Categorización** | Library SOLO | Dashboard debe ser rápido y simple |
| **Mensajes Recientes** | Dashboard SIEMPRE | Referencia rápida esencial |
| **Voice Settings** | Playground → Auto | Cliente no debe preocuparse |
| **Volume Controls** | Playground → Auto | Configuración una vez |
| **Favoritos** | Library | Organización personal |
| **Editar Copia** | Library → Dashboard | Flujo natural de trabajo |
| **Vista Lista** | Library | Preferencia de usuario |
| **Category Config** | Playground | Setup por cliente |

---

## 🎯 Beneficios de la Arquitectura v2.1

1. **Dashboard Simplificado**
   - Sin categorías = menos decisiones
   - Settings automáticos = generación rápida
   - Mensajes recientes = contexto inmediato

2. **Library Poderosa**
   - Categorización posterior = más flexible
   - Favoritos cross-category = mejor organización
   - Vista dual = preferencias de usuario
   - Editar copia = reutilización segura

3. **Playground Profesional**
   - Settings por voz = personalización total
   - Categorías editables = adaptable a cualquier cliente
   - Volúmenes granulares = control profesional
   - Todo automático = cero fricción para usuario final

4. **Flujo de Trabajo Natural**
   ```
   Generar (simple) → Guardar → Categorizar → Reutilizar
   ```
   en vez de
   ```
   Categorizar → Generar → Guardar → Buscar por categoría
   ```

---

## 💡 Conclusión v2.1

Esta arquitectura actualizada resuelve los problemas clave:

- ✅ **Simplicidad en Dashboard** sin perder funcionalidad
- ✅ **Control total** desde Playground sin complejidad para usuario
- ✅ **Flexibilidad** con categorías y settings personalizables
- ✅ **Flujo natural** que sigue el proceso mental del usuario

El sistema es ahora más **intuitivo** para el usuario final y más **poderoso** para el administrador.

---

**Documento actualizado**: 2025-11-22
**Versión**: 2.1
**Cambios aplicados**: 8 mejoras críticas basadas en feedback