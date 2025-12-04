# Playroom Mobile Interface - Especificación Técnica

**Versión**: 1.0
**Fecha**: 2025-12-04
**Target**: 100% Mobile
**Workflow**: 3 clics máximo

---

## 🎯 Objetivo

Crear una interfaz **extremadamente minimal** para mobile que permita generar mensajes de audio en **solo 3 clics**:

1. **Clic 1**: Seleccionar perfil de voz (tap en foto del carousel)
2. **Clic 2**: Detener grabación (tap en botón STOP)
3. **Clic 3**: Enviar a parlantes / Cambiar texto / Cambiar voz

---

## 📱 Diseño General

### Principios de Diseño
- ✅ **Mobile-first**: Diseñado exclusivamente para teléfonos
- ✅ **Minimal**: Sin distracciones, solo lo esencial
- ✅ **Rápido**: 3 clics para completar el flujo
- ✅ **Visual**: Fotos grandes de perfiles, sin texto excesivo
- ✅ **Automático**: Menos decisiones para el usuario

### Pantalla Completa
- **No header**: Sin barra de navegación superior
- **No sidebar**: Solo contenido
- **Full viewport**: Usar 100vh y 100vw
- **Sin scroll inicial**: Todo visible en la primera vista

---

## 🎨 Estados de la Interfaz

### **Estado 1: Selección de Perfil** (Inicial)

```
┌─────────────────────────────────┐
│                                 │
│  ¿Qué quieres anunciar?        │
│                                 │
│  ┌──────────────────────────┐  │
│  │                          │  │
│  │      [FOTO PERFIL]       │  │
│  │       (Fullscreen)       │  │
│  │                          │  │
│  │    Mario                 │  │
│  │    Anuncios              │  │
│  │                          │  │
│  └──────────────────────────┘  │
│                                 │
│        ● ○ ○                   │  <- Dots indicator
│                                 │
│  [TAP PARA GRABAR]             │
│                                 │
└─────────────────────────────────┘
```

#### Elementos
1. **Título**: "¿Qué quieres anunciar?"
   - Font: Bold, 24px
   - Posición: Top, centrado
   - Margin: 20px

2. **Carousel de Fotos**
   - Tamaño: 100% width, 60% height
   - Transición: Suave (300ms ease-in-out)
   - Gestos: Swipe horizontal
   - Loop infinito: Sí

3. **Información del Perfil** (sobre la foto)
   - Nombre: Font 32px, bold
   - Tipo: Font 18px, regular
   - Posición: Bottom overlay con gradiente oscuro

4. **Dots Indicator**
   - 3 dots horizontales
   - Activo: Color primario, grande
   - Inactivo: Gris, pequeño

5. **Call-to-Action**
   - Texto: "TAP PARA GRABAR"
   - Posición: Bottom center
   - Animación: Pulse suave

#### Perfiles Disponibles

| Orden | Nombre | Tipo | Música | Duración |
|-------|--------|------|--------|----------|
| 1 | Mario | Anuncios | NO | 10-15s |
| 2 | Juan Carlos | Ofertas y Promociones | SÍ (track por defecto) | 10-15s |
| 3 | Jose Miguel | Jingles | SÍ (track por defecto) | 10-15s |

#### Comportamiento
- **Swipe left/right**: Cambiar entre perfiles
- **Tap en foto**: Iniciar grabación inmediatamente
- **Scroll**: Disabled en este estado

---

### **Estado 2: Grabando**

```
┌─────────────────────────────────┐
│                                 │
│                                 │
│        ● REC  00:05             │  <- Timer
│                                 │
│      ┌──────────────┐           │
│      │              │           │
│      │   [ICONO     │           │
│      │    MIC       │           │
│      │   PULSANTE]  │           │
│      │              │           │
│      └──────────────┘           │
│                                 │
│                                 │
│      ┌──────────────┐           │
│      │   [  ■  ]    │           │  <- STOP button
│      └──────────────┘           │
│                                 │
└─────────────────────────────────┘
```

#### Elementos

1. **Indicador REC**
   - Posición: Top center
   - Color: Rojo (#FF0000)
   - Dot pulsante: Animación cada 1s
   - Timer: MM:SS format

2. **Ícono Micrófono**
   - Tamaño: 120px x 120px
   - Color: Rojo
   - Animación: Pulse continuo
   - Posición: Center

3. **Botón STOP**
   - Shape: Cuadrado grande dentro de círculo
   - Tamaño: 80px
   - Color: Rojo (#FF0000)
   - Posición: Bottom center, margin 40px
   - Label: "DETENER"

#### Comportamiento
- **Auto-scroll**: Al iniciar grabación, scroll suave hacia abajo
- **Timer**: Incrementa cada segundo desde 00:00
- **Sin límite**: El usuario controla cuando parar
- **Transcripción**: Se captura pero NO se muestra en tiempo real
- **Tap STOP**: Termina grabación y pasa a Estado 3

---

### **Estado 3: Generando Audio**

```
┌─────────────────────────────────┐
│                                 │
│                                 │
│                                 │
│      ┌──────────────┐           │
│      │              │           │
│      │   [SPINNER   │           │
│      │   LOADING]   │           │
│      │              │           │
│      └──────────────┘           │
│                                 │
│    🪄 Haciendo la magia...      │
│                                 │
│                                 │
│                                 │
└─────────────────────────────────┘
```

#### Elementos

1. **Spinner/Loader**
   - Tipo: DaisyUI loading spinner
   - Tamaño: Large (64px)
   - Color: Primary
   - Posición: Center

2. **Mensaje**
   - Texto: "🪄 Haciendo la magia..."
   - Alternativas: "Generando audio...", "Creando tu mensaje..."
   - Font: 20px, centrado
   - Posición: Below spinner

#### Comportamiento
- **Proceso automático**:
  1. Envía audio transcrito al backend
  2. Claude AI mejora el texto
  3. ElevenLabs genera TTS
  4. Si el perfil requiere música, mezcla automáticamente
  5. Pasa automáticamente a Estado 4

- **Sin interacción**: Usuario no puede hacer nada
- **Tiempo estimado**: 3-7 segundos

---

### **Estado 4: Reproduciendo Audio**

```
┌─────────────────────────────────┐
│                                 │
│  ┌─────────────────────────┐   │
│  │  Mario - Anuncios        │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │  [════▶════════════]    │   │  <- Waveform
│  │  00:05 / 00:12          │   │
│  │  ⏸ ⏹ 🔊                 │   │  <- Controls
│  └─────────────────────────┘   │
│                                 │
│  📝 Texto generado:             │
│  "Atención: Se solicita al     │
│   dueño del auto patente..."   │
│                                 │
│                                 │
│  ┌─────────────────────────┐   │
│  │  📝 Cambiar Texto       │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │  🎤 Cambiar Voz         │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │  📢 Enviar a Parlantes  │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
```

#### Elementos

1. **Header con Perfil**
   - Muestra: Nombre + Tipo de mensaje
   - Pequeño, 16px
   - Background: Base-200

2. **Audio Player**
   - **Reproducción AUTOMÁTICA**: Se reproduce apenas termina de generar
   - Waveform visual (opcional, puede ser barra simple)
   - Progress bar con tiempo actual / total
   - Controles:
     - ⏸ Pause (si está reproduciendo)
     - ▶ Play (si está pausado)
     - ⏹ Stop
     - 🔊 Volumen

3. **Preview del Texto**
   - Muestra el texto mejorado por Claude AI
   - Máximo 3 líneas visibles
   - Scroll si es más largo
   - Font: 14px, regular

4. **Botones de Acción** (3 botones principales)

   **Botón 1: Cambiar Texto**
   - Icono: 📝
   - Label: "Cambiar Texto"
   - Color: Secondary
   - Acción: Abre Tab de edición

   **Botón 2: Cambiar Voz**
   - Icono: 🎤
   - Label: "Cambiar Voz"
   - Color: Secondary
   - Acción: Abre Tab de selección de voz

   **Botón 3: Enviar a Parlantes**
   - Icono: 📢
   - Label: "Enviar a Parlantes"
   - Color: Primary (destacado)
   - Acción: Muestra modal de confirmación

#### Comportamiento
- **Auto-play**: El audio se reproduce automáticamente al cargarse
- **Controls visibles**: Usuario puede pausar, detener, ajustar volumen
- **Botones siempre visibles**: Scroll down para verlos si es necesario

---

### **Estado 4.1: Tab - Cambiar Texto** (Expandido)

```
┌─────────────────────────────────┐
│  [Cambiar Texto] [Cambiar Voz] │  <- Tabs
│  ═══════════════                │
│                                 │
│  ┌─────────────────────────┐   │
│  │                         │   │
│  │ [Textarea Editable]     │   │
│  │                         │   │
│  │ "Atención: Se solicita  │   │
│  │  al dueño del auto..."  │   │
│  │                         │   │
│  │                         │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │    🔄 Regenerar Audio    │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │  📢 Enviar a Parlantes  │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
```

#### Elementos

1. **Tabs**
   - Dos tabs: "Cambiar Texto" | "Cambiar Voz"
   - Activo: Subrayado
   - Transición suave entre tabs

2. **Textarea**
   - Editable
   - Muestra el texto mejorado por IA
   - Auto-resize según contenido
   - Max-height: 200px, luego scroll

3. **Botón Regenerar**
   - Label: "🔄 Regenerar Audio"
   - Acción: Envía el texto editado + voz actual → Genera nuevo audio
   - Vuelve a Estado 3 (Generando)

4. **Botón Enviar**
   - Igual que antes
   - Envía el último audio generado

---

### **Estado 4.2: Tab - Cambiar Voz** (Expandido)

```
┌─────────────────────────────────┐
│  [Cambiar Texto] [Cambiar Voz] │  <- Tabs
│                 ═══════════════  │
│                                 │
│  🎤 Selecciona otra voz:        │
│                                 │
│  ┌─────────────────────────┐   │
│  │  ○ Mario                │   │
│  │    Anuncios             │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │  ● Juan Carlos          │   │  <- Selected
│  │    Ofertas y Promo.     │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │  ○ Jose Miguel          │   │
│  │    Jingles              │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │    🔄 Regenerar Audio    │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │  📢 Enviar a Parlantes  │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
```

#### Elementos

1. **Lista de Voces**
   - Radio buttons
   - Muestra: Nombre + Tipo
   - Seleccionado: Marcado visualmente

2. **Botón Regenerar**
   - Label: "🔄 Regenerar Audio"
   - Acción: Envía el texto actual + nueva voz → Genera nuevo audio
   - Vuelve a Estado 3 (Generando)

3. **Botón Enviar**
   - Igual que antes

---

### **Estado 5: Modal de Confirmación**

```
┌─────────────────────────────────┐
│                                 │
│  ┌─────────────────────────┐   │
│  │                         │   │
│  │  📢 Confirmar Envío     │   │
│  │                         │   │
│  │  ¿Enviar este mensaje   │   │
│  │  a los parlantes ahora? │   │
│  │                         │   │
│  │  [  ❌ Cancelar  ]      │   │
│  │  [  ✅ Sí, Enviar ]     │   │
│  │                         │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
```

#### Elementos

1. **Modal**
   - Centrado en la pantalla
   - Overlay oscuro (backdrop)
   - Título: "Confirmar Envío"

2. **Mensaje**
   - "¿Enviar este mensaje a los parlantes ahora?"

3. **Botones**
   - **Cancelar**: Cierra modal, vuelve a Estado 4
   - **Sí, Enviar**: Envía y muestra toast de éxito

#### Comportamiento
- **Cancelar**: Vuelve al estado anterior
- **Enviar**:
  1. Envía audio al sistema de parlantes
  2. Muestra toast: "✅ Mensaje enviado exitosamente"
  3. Vuelve a Estado 1 (reset completo)
  4. (Opcional) Vibración del dispositivo

---

### **Estado 6: Historial** (Swipe Down desde Estado 1)

```
┌─────────────────────────────────┐
│  📜 Últimos mensajes            │
│                                 │
│  ┌─────────────────────────┐   │
│  │ 🎤 Mario - 12:34        │   │
│  │ "Atención: Auto mal..." │   │
│  │ [▶ Reproducir]          │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │ 🎤 Juan Carlos - 12:30  │   │
│  │ "Oferta especial..."    │   │
│  │ [▶ Reproducir]          │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │ 🎤 Jose Miguel - 12:25  │   │
│  │ "Jingle de apertura..." │   │
│  │ [▶ Reproducir]          │   │
│  └─────────────────────────┘   │
│                                 │
│  [Volver al inicio]             │
│                                 │
└─────────────────────────────────┘
```

#### Elementos

1. **Header**
   - Título: "📜 Últimos mensajes"

2. **Lista de Mensajes** (últimos 3)
   - Voz + Hora de creación
   - Preview del texto (1 línea)
   - Botón play individual

3. **Botón Volver**
   - Cierra historial, vuelve a Estado 1

#### Comportamiento
- **Gesto**: Swipe down desde Estado 1
- **Tap en mensaje**: Reproduce ese audio
- **No editable**: Solo reproducción

---

## 🔄 Flujo de Estados (State Machine)

```
Estado 1 (Selección)
    │
    │ [TAP en foto]
    ▼
Estado 2 (Grabando)
    │
    │ [TAP en STOP]
    ▼
Estado 3 (Generando)
    │
    │ [Auto]
    ▼
Estado 4 (Reproduciendo)
    │
    ├─→ [Cambiar Texto] → Estado 4.1 (Tab Texto)
    │                         │
    │                         │ [Regenerar]
    │                         └──→ Estado 3
    │
    ├─→ [Cambiar Voz] → Estado 4.2 (Tab Voz)
    │                       │
    │                       │ [Regenerar]
    │                       └──→ Estado 3
    │
    └─→ [Enviar] → Estado 5 (Modal Confirmación)
                      │
                      ├─→ [Cancelar] → Estado 4
                      │
                      └─→ [Sí, Enviar] → Toast + Estado 1
```

**Estados Adicionales**:
- **Swipe Down** desde Estado 1 → Estado 6 (Historial)
- **Error** en cualquier estado → Modal de error + volver a estado anterior

---

## 🛠️ Especificaciones Técnicas

### Componentes Vue Necesarios

```
frontend/src/components/settings/playroom/mobile/
├── MobilePlayroom.vue              # Componente principal
├── components/
│   ├── VoiceCarousel.vue           # Estado 1: Carousel de perfiles
│   ├── RecordingView.vue           # Estado 2: Vista de grabación
│   ├── GeneratingView.vue          # Estado 3: Loader
│   ├── AudioPlayerView.vue         # Estado 4: Player + botones
│   ├── TextEditorTab.vue           # Estado 4.1: Tab de texto
│   ├── VoiceSelectorTab.vue        # Estado 4.2: Tab de voz
│   ├── ConfirmModal.vue            # Estado 5: Modal
│   └── HistoryPanel.vue            # Estado 6: Historial
└── composables/
    └── useMobilePlayroom.ts        # Lógica del state machine
```

### Composable Principal: `useMobilePlayroom.ts`

```typescript
export interface VoiceProfile {
  id: string
  name: string
  type: string
  photo: string
  hasMusic: boolean
  defaultMusicFile: string | null
  targetDuration: number
}

export type PlayroomState =
  | 'selection'
  | 'recording'
  | 'generating'
  | 'playing'
  | 'history'

export function useMobilePlayroom() {
  // State
  const currentState = ref<PlayroomState>('selection')
  const selectedProfile = ref<VoiceProfile | null>(null)
  const isRecording = ref(false)
  const recordingDuration = ref(0)
  const transcript = ref('')
  const generatedAudio = ref<AudioData | null>(null)
  const audioElement = ref<HTMLAudioElement | null>(null)
  const recentMessages = ref<AudioData[]>([])

  // Actions
  const selectProfile = (profile: VoiceProfile) => { ... }
  const startRecording = async () => { ... }
  const stopRecording = () => { ... }
  const generateAudio = async () => { ... }
  const playAudio = () => { ... }
  const regenerateWithNewText = async (newText: string) => { ... }
  const regenerateWithNewVoice = async (voiceId: string) => { ... }
  const sendToSpeakers = async () => { ... }
  const loadHistory = async () => { ... }

  return {
    currentState,
    selectedProfile,
    isRecording,
    recordingDuration,
    transcript,
    generatedAudio,
    recentMessages,
    selectProfile,
    startRecording,
    stopRecording,
    generateAudio,
    playAudio,
    regenerateWithNewText,
    regenerateWithNewVoice,
    sendToSpeakers,
    loadHistory,
  }
}
```

### Perfiles de Voz (Data)

```typescript
export const VOICE_PROFILES: VoiceProfile[] = [
  {
    id: 'mario',
    name: 'Mario',
    type: 'Anuncios',
    photo: '/profiles/mario.jpg',  // Placeholder por ahora
    hasMusic: false,
    defaultMusicFile: null,
    targetDuration: 12,
  },
  {
    id: 'juan_carlos',
    name: 'Juan Carlos',
    type: 'Ofertas y Promociones',
    photo: '/profiles/juan-carlos.jpg',
    hasMusic: true,
    defaultMusicFile: 'promo_music.mp3',  // Track por defecto
    targetDuration: 15,
  },
  {
    id: 'jose_miguel',
    name: 'Jose Miguel',
    type: 'Jingles',
    photo: '/profiles/jose-miguel.jpg',
    hasMusic: true,
    defaultMusicFile: 'jingle_music.mp3',
    targetDuration: 15,
  },
]
```

---

## 🌐 Endpoints API

### 1. Generar Audio (igual que playroom existente)

```
POST /api/v1/settings/playroom/generate
```

**Request**:
```json
{
  "text": "transcripción del audio",
  "voice_id": "mario",
  "music_file": null,
  "target_duration": 12,
  "improve_text": true
}
```

**Response**:
```json
{
  "success": true,
  "original_text": "texto original",
  "improved_text": "texto mejorado por IA",
  "voice_used": "Mario",
  "audio_url": "/storage/audio/playroom_xxx.mp3",
  "filename": "playroom_xxx.mp3",
  "duration": 12.5,
  "audio_id": 123
}
```

### 2. Enviar a Parlantes (nuevo endpoint)

```
POST /api/v1/playroom/send-to-speakers
```

**Request**:
```json
{
  "audio_id": 123
}
```

**Response**:
```json
{
  "success": true,
  "message": "Audio enviado a los parlantes"
}
```

### 3. Obtener Historial (últimos 3)

```
GET /api/v1/playroom/history?limit=3
```

**Response**:
```json
{
  "messages": [
    {
      "id": 123,
      "voice_name": "Mario",
      "voice_type": "Anuncios",
      "text": "Atención: Auto mal estacionado...",
      "audio_url": "/storage/audio/playroom_xxx.mp3",
      "created_at": "2025-12-04T12:34:00Z"
    },
    ...
  ]
}
```

---

## 🎨 Diseño y Estilos

### Colores

```css
/* Mobile Playroom Theme */
--playroom-primary: #8B5CF6;      /* Purple */
--playroom-secondary: #EC4899;    /* Pink */
--playroom-accent: #10B981;       /* Green */
--playroom-recording: #EF4444;    /* Red */
--playroom-bg: #1F2937;           /* Dark gray */
--playroom-surface: #374151;      /* Light gray */
```

### Tipografía

- **Headers**: Inter Bold, 24-32px
- **Body**: Inter Regular, 16px
- **Captions**: Inter Regular, 14px
- **Buttons**: Inter SemiBold, 18px

### Espaciado

- **Padding general**: 16px
- **Gap entre elementos**: 12px
- **Margin botones**: 40px bottom

### Componentes DaisyUI

Usar componentes existentes:
- `btn` para botones
- `modal` para confirmaciones
- `loading` para spinner
- `toast` para notificaciones
- `tabs` para cambiar texto/voz
- `textarea` para editor

---

## ⚠️ Manejo de Errores

### Error: Sin transcripción (texto vacío)

```
┌─────────────────────────────────┐
│  ⚠️ No se detectó voz           │
│                                 │
│  Por favor, intenta de nuevo    │
│  y habla más cerca del micrófono│
│                                 │
│  [Volver a grabar]              │
└─────────────────────────────────┘
```

**Acción**: Vuelve a Estado 1

### Error: Fallo en generación de TTS

```
┌─────────────────────────────────┐
│  ❌ Error al generar audio      │
│                                 │
│  Hubo un problema con el        │
│  servicio de voz. Intenta       │
│  nuevamente.                    │
│                                 │
│  [Reintentar] [Cancelar]        │
└─────────────────────────────────┘
```

**Acciones**:
- **Reintentar**: Vuelve a Estado 3 (intenta generar de nuevo)
- **Cancelar**: Vuelve a Estado 1

### Error: Fallo al enviar a parlantes

```
Toast: "❌ No se pudo enviar el mensaje. Intenta de nuevo."
```

**Acción**: Permanece en Estado 4, usuario puede reintentar

### Error: Sin conexión a internet

```
Toast: "⚠️ Sin conexión a internet. Verifica tu red."
```

**Acción**: Bloquea acciones que requieran red

### Usuario presiona "Atrás" del navegador

```javascript
// Detectar navegación atrás
window.addEventListener('popstate', (event) => {
  if (currentState.value === 'recording') {
    // Detener grabación automáticamente
    stopRecording()
  }
  // Siempre volver a Estado 1
  resetToInitialState()
})
```

---

## 📐 Layout Responsive

### Mobile Portrait (Target Principal)

```css
/* 375px - 428px (iPhone SE - iPhone Pro Max) */
.mobile-playroom {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.carousel-photo {
  width: 100%;
  height: 60vh;
  object-fit: cover;
}

.button-group {
  padding: 16px;
  gap: 12px;
}
```

### Mobile Landscape (Opcional, menos prioritario)

```css
@media (orientation: landscape) and (max-height: 600px) {
  .carousel-photo {
    height: 80vh;
  }

  .button-group {
    flex-direction: row;
  }
}
```

---

## 🚀 Implementación - Orden de Tareas

### Fase 1: Estructura Base (Día 1)
1. ✅ Crear `MobilePlayroom.vue` con routing
2. ✅ Crear composable `useMobilePlayroom.ts` con state machine básico
3. ✅ Implementar componente `VoiceCarousel.vue` (Estado 1)
4. ✅ Agregar perfiles con fotos placeholder
5. ✅ Implementar swipe gesture y dots indicator

### Fase 2: Grabación (Día 2)
1. ✅ Implementar `RecordingView.vue` (Estado 2)
2. ✅ Integrar Speech Recognition API
3. ✅ Agregar timer de grabación
4. ✅ Implementar botón STOP y auto-scroll

### Fase 3: Generación y Reproducción (Día 3)
1. ✅ Implementar `GeneratingView.vue` (Estado 3)
2. ✅ Conectar con endpoint `/playroom/generate`
3. ✅ Implementar `AudioPlayerView.vue` (Estado 4)
4. ✅ Auto-play del audio generado
5. ✅ Mostrar preview del texto mejorado

### Fase 4: Edición (Día 4)
1. ✅ Implementar `TextEditorTab.vue` (Estado 4.1)
2. ✅ Implementar `VoiceSelectorTab.vue` (Estado 4.2)
3. ✅ Sistema de tabs con transiciones
4. ✅ Botón "Regenerar" con vuelta a Estado 3

### Fase 5: Envío y Confirmación (Día 5)
1. ✅ Implementar `ConfirmModal.vue` (Estado 5)
2. ✅ Crear endpoint `/playroom/send-to-speakers`
3. ✅ Integrar toast de confirmación
4. ✅ Reset a Estado 1 después de enviar

### Fase 6: Historial (Día 6)
1. ✅ Implementar `HistoryPanel.vue` (Estado 6)
2. ✅ Crear endpoint `/playroom/history`
3. ✅ Swipe down gesture desde Estado 1
4. ✅ Reproducción de audios antiguos

### Fase 7: Error Handling (Día 7)
1. ✅ Implementar todos los casos de error
2. ✅ Modales de error con reintentos
3. ✅ Toasts informativos
4. ✅ Manejo de navegación atrás

### Fase 8: Polish y Testing (Día 8)
1. ✅ Animaciones y transiciones suaves
2. ✅ Testing en diferentes dispositivos mobile
3. ✅ Optimización de performance
4. ✅ Documentación final

---

## 📝 Notas para el Desarrollador

### Prioridades
1. **Funcionalidad primero**: Que funcione el flujo completo antes de pulir
2. **Mobile-only**: No preocuparse por desktop en esta versión
3. **Velocidad**: El objetivo es 3 clics, debe ser rápido
4. **Visual**: Las fotos grandes son lo más importante

### Librerías Sugeridas

```json
{
  "dependencies": {
    "vue": "^3.x",
    "swiper": "^11.x",          // Para carousel con gestos
    "howler": "^2.x",            // Para audio player robusto
    "vue-use": "^10.x"           // Para gestures y utilities
  }
}
```

### Testing Checklist

- [ ] Carousel swipe funciona suavemente en iOS y Android
- [ ] Grabación funciona en Chrome y Safari mobile
- [ ] Auto-scroll después de tap funciona correctamente
- [ ] Timer de grabación es preciso
- [ ] Auto-play del audio funciona
- [ ] Tabs cambian sin lag
- [ ] Modal de confirmación aparece correctamente
- [ ] Toast es visible y desaparece automáticamente
- [ ] Swipe down para historial no interfiere con scroll
- [ ] Navegación atrás no rompe el estado
- [ ] Funciona en iPhone SE (pantalla pequeña)
- [ ] Funciona en iPhone Pro Max (pantalla grande)
- [ ] Funciona en Android (diferentes navegadores)

---

## 🎯 Resultado Final Esperado

**Usuario abre la app en mobile**:

1. **Ve carousel con fotos grandes** → Swipe para elegir perfil
2. **Tap en foto** → Graba su mensaje (5-10 segundos)
3. **Tap STOP** → Espera 5 segundos (auto-genera y auto-reproduce)
4. **Escucha resultado** → Si está ok, tap "Enviar a Parlantes"
5. **Confirmación** → Toast de éxito y vuelve al inicio

**Total: 3-4 taps, menos de 30 segundos**

---

**Fin de la Especificación Técnica**
