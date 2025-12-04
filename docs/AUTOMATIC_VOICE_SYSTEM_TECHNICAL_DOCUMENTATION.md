# Sistema de Voz Automática - Documentación Técnica
## MediaFlow Legacy → v2.1 Migration Guide

**Versión:** 1.0
**Fecha:** 3 de diciembre de 2025
**Sistema Legacy:** Casa Costanera `/var/www/casa/src/modules/automatic`
**Sistema Objetivo:** MediaFlow v2.1 `/var/www/mediaflow-v2`

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes Principales](#componentes-principales)
4. [Workflow Completo](#workflow-completo)
5. [Archivos Críticos](#archivos-críticos)
6. [Servicios Backend](#servicios-backend)
7. [Configuraciones](#configuraciones)
8. [Dependencias Externas](#dependencias-externas)
9. [Guía de Implementación](#guía-de-implementación)
10. [Consideraciones de Seguridad](#consideraciones-de-seguridad)

---

## 📖 Descripción General

El **Sistema de Voz Automática** permite a los usuarios crear jingles de radio profesionales mediante reconocimiento de voz en tiempo real. El sistema captura audio del usuario, lo transcribe, lo mejora con IA, genera TTS profesional, y lo mezcla con música de fondo.

### Características Principales

- **Reconocimiento de voz en tiempo real** usando Web Speech API (sin backend)
- **Transcripción local** en el navegador (español de Chile)
- **Mejora inteligente de texto** con Claude AI
- **Generación TTS** con ElevenLabs
- **Mezcla automática** de voz + música de fondo
- **Ducking inteligente** para reducir música durante el habla
- **Normalización de audio** (LUFS) para broadcast quality
- **Interfaz mobile-first** optimizada para dispositivos táctiles

### Tecnologías Utilizadas

**Frontend:**
- Web Speech API (reconocimiento de voz)
- Web Audio API (visualización)
- Canvas API (visualizadores)
- JavaScript ES6+ (módulos)

**Backend:**
- PHP 7.4+ (orquestación)
- FFmpeg (procesamiento de audio)
- SQLite3 (almacenamiento)
- Claude AI (mejora de texto)
- ElevenLabs (TTS)

---

## 🏗 Arquitectura del Sistema

### Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Usuario presiona botón "Grabar"                             │
│  ↓                                                                │
│  2. Web Speech API captura voz en tiempo real                   │
│     - recognition.lang = 'es-CL'                                 │
│     - recognition.continuous = true                              │
│     - recognition.interimResults = true                          │
│  ↓                                                                │
│  3. Transcripción en tiempo real (mostrada al usuario)          │
│  ↓                                                                │
│  4. Usuario detiene grabación (máx 20 segundos)                 │
│  ↓                                                                │
│  5. Usuario selecciona voz de la lista                          │
│  ↓                                                                │
│  6. [OPCIONAL] Usuario configura opciones avanzadas:            │
│     - Música de fondo personalizada                              │
│     - Duración objetivo (5-25 segundos)                          │
│  ↓                                                                │
│  7. Envío de datos al backend via AJAX                          │
│     POST /api/automatic-jingle-service.php                       │
│     {                                                             │
│       "text": "texto transcrito",                                │
│       "voice_id": "juan_carlos",                                 │
│       "music_file": "Uplift.mp3", // opcional                    │
│       "target_duration": 20        // opcional                   │
│     }                                                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  AUTOMATIC-JINGLE-SERVICE.PHP (Orquestador Principal)           │
│  ↓                                                                │
│  8. Validación de texto transcrito                              │
│     - Verificar que no esté vacío                                │
│     - Sanitizar entrada                                          │
│  ↓                                                                │
│  9. PASO 1: Mejora de Texto con Claude AI                       │
│     claude-service.php::generateAnnouncements()                  │
│     - Contexto: texto original del usuario                       │
│     - Category: 'automatic'                                      │
│     - Mode: 'automatic'                                          │
│     - Word limits basados en target_duration:                    │
│       * 5s  → 5-8 palabras                                       │
│       * 10s → 10-15 palabras                                     │
│       * 15s → 15-20 palabras                                     │
│       * 20s → 20-30 palabras (default)                           │
│       * 25s → 30-40 palabras                                     │
│     - Resultado: texto optimizado para radio                     │
│  ↓                                                                │
│  10. PASO 2: Carga de Configuración                             │
│      jingle-config.json::jingle_defaults                         │
│      - Parámetros de mezcla (volumes, fades)                     │
│      - Configuración de ducking                                  │
│      - Voice settings (stability, style, etc.)                   │
│      - Normalización LUFS                                        │
│  ↓                                                                │
│  11. PASO 3: Generación de Jingle                               │
│      jingle-service.php::generateJingle()                        │
│      ↓                                                            │
│      11a. Generar TTS                                            │
│           tts-service.php::generateEnhancedTTS()                 │
│           - Llamada a ElevenLabs API                             │
│           - Voice settings aplicados                             │
│           - Resultado: archivo MP3 temporal                      │
│      ↓                                                            │
│      11b. Procesar Música de Fondo                               │
│           - Cargar archivo desde /public/audio/music/            │
│           - Aplicar fade in/out                                  │
│           - Ajustar volumen según config                         │
│      ↓                                                            │
│      11c. Mezcla con FFmpeg                                      │
│           - Overlay de voz sobre música                          │
│           - Ducking inteligente (reducir música durante voz)     │
│           - Intro silence + mensaje + outro silence              │
│           - Compresión dinámica                                  │
│      ↓                                                            │
│      11d. Normalización LUFS (Opcional)                          │
│           audio-processor.php::normalizeLUFS()                   │
│           - Target: -16 LUFS (broadcast standard)                │
│           - Mantener rango dinámico                              │
│  ↓                                                                │
│  12. Guardar archivo en /src/api/temp/                          │
│      Formato: jingle_auto_YYYYMMDD_HHMMSS_voiceId.mp3           │
│  ↓                                                                │
│  13. Registrar en base de datos SQLite                          │
│      Tabla: audio_metadata                                       │
│      Campos:                                                      │
│      - filename: nombre del archivo generado                     │
│      - display_name: primeras 50 palabras del texto              │
│      - description: texto mejorado completo                      │
│      - category: 'automatic'                                     │
│      - metadata: JSON con detalles completos                     │
│      - created_at: timestamp                                     │
│  ↓                                                                │
│  14. Retornar respuesta JSON                                     │
│      {                                                            │
│        "success": true,                                           │
│        "original_text": "texto del usuario",                     │
│        "improved_text": "texto mejorado por IA",                 │
│        "voice_used": "juan_carlos",                              │
│        "audio_url": "/src/api/temp/jingle_auto_...",            │
│        "filename": "jingle_auto_20251203_152000.mp3",           │
│        "duration": 20.5                                          │
│      }                                                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND - REPRODUCCIÓN                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  15. Recibir respuesta del backend                               │
│  ↓                                                                │
│  16. Mostrar reproductor de audio                                │
│      - Custom player con visualizador                            │
│      - Canvas con waveform en tiempo real                        │
│      - Controles de play/pause/seek                              │
│  ↓                                                                │
│  17. Auto-play del jingle generado                               │
│  ↓                                                                │
│  18. Botón "Enviar a Radio"                                      │
│      - Copia archivo a carpeta de reproducción                   │
│      - Añade a cola de radio automática                          │
│  ↓                                                                │
│  19. Animación de éxito y reset del módulo                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes Principales

### 1. Frontend Module (`index.js`)

**Ubicación:** `/var/www/casa/src/modules/automatic/index.js`
**Clase:** `AutomaticModeModule`
**Líneas de código:** ~1,141

#### Responsabilidades

- Gestión del ciclo de vida del módulo
- Manejo de Web Speech API para reconocimiento de voz
- Interfaz de usuario y eventos táctiles
- Gestión de estado del workflow
- Visualización de audio con Canvas
- Comunicación con backend via AJAX

#### Estado del Módulo (`this.state`)

```javascript
{
  isRecording: false,           // Está grabando actualmente
  isProcessing: false,          // Está procesando con backend
  currentAudio: null,           // URL del audio actual
  selectedVoice: null,          // Voz seleccionada (key: 'juan_carlos')
  selectedMusic: null,          // Música seleccionada
  voices: [],                   // Array de voces disponibles
  musicList: [],                // Array de música disponible
  audioBlob: null,              // Blob de audio grabado (deprecated)
  generatedAudio: null,         // Datos del audio generado
  mediaRecorder: null,          // MediaRecorder instance (deprecated)
  recordingTimer: null,         // Timer interval
  recordingSeconds: 0,          // Contador de segundos
  recognition: null,            // Web Speech API instance
  transcribedText: '',          // Texto transcrito
  advancedMode: false           // Opciones avanzadas activas
}
```

#### Métodos Clave

**Inicialización:**
- `load(container)` - Carga el módulo y template
- `loadTemplate()` - Carga HTML desde template.html
- `cacheElements()` - Cachea referencias DOM
- `setupEventListeners()` - Configura listeners de eventos
- `checkMicrophonePermission()` - Verifica permisos de micrófono

**Grabación:**
- `startRecording()` - Inicia Web Speech API (línea 384)
- `stopRecording()` - Detiene reconocimiento (línea 481)
- `startTimer()` - Timer de 20 segundos máximo (línea 516)

**Procesamiento:**
- `processRecording()` - Muestra selector de voces (línea 534)
- `selectVoice(voiceKey, realVoiceId)` - Selecciona voz y procesa (línea 546)
- `processAudio()` - Envía datos al backend (línea 574)

**Reproducción:**
- `playGeneratedAudio(audioUrl)` - Muestra reproductor (línea 646)
- `setupPlayerVisualizer()` - Configura visualizador (línea 745)
- `startVisualizer()` - Animación de waveform (línea 765)
- `togglePlayPause()` - Control de reproducción (línea 713)

**Envío a Radio:**
- `sendToRadio()` - Envía jingle a radio (línea 831)
- `showSuccessAnimation()` - Animación de éxito (línea 874)

**Utilidades:**
- `loadVoices()` - Carga voces desde API (línea 168)
- `loadMusicList()` - Carga música disponible (línea 200)
- `setupAdvancedOptions()` - Configura opciones avanzadas (línea 996)
- `resetState()` - Limpia estado (línea 967)

#### Configuración de Web Speech API

```javascript
// Líneas 401-409
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
this.state.recognition = new SpeechRecognition();

this.state.recognition.lang = 'es-CL';        // Español de Chile
this.state.recognition.continuous = true;      // Continuar escuchando
this.state.recognition.interimResults = true;  // Resultados parciales
this.state.recognition.maxAlternatives = 1;    // Una alternativa
```

#### Request al Backend

```javascript
// Líneas 593-617
const requestData = {
    text: this.state.transcribedText,
    voice_id: this.state.selectedVoice,
    music_file: this.state.selectedMusic || undefined,
    target_duration: parseInt(this.elements.durationSelect.value) || 20
};

const response = await fetch('/api/automatic-jingle-service.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData)
});
```

---

### 2. Template HTML (`template.html`)

**Ubicación:** `/var/www/casa/src/modules/automatic/template.html`
**Líneas:** 159

#### Estructura

1. **Recording Section** (líneas 5-18)
   - Botón grande de grabación (180px × 180px móvil)
   - Timer de grabación
   - Canvas visualizador (oculto en producción)

2. **Status Message** (línea 21)
   - Mensaje flotante fixed position
   - Estados: info, processing, success, error

3. **Voice Selection** (líneas 24-78)
   - Grid/scroll horizontal de voces
   - Advanced options toggle
   - Music selector
   - Duration selector (5-25 segundos)

4. **Audio Player** (líneas 81-131)
   - Custom player con canvas visualizer
   - Controles de reproducción
   - Progress bar
   - Botón "Enviar a Radio"

#### Elementos Críticos (IDs)

```html
#record-button          → Botón principal de grabación
#recording-timer        → Timer visible
#voices-list            → Contenedor de voces
#voices-section         → Sección completa de voces
#status-message         → Mensajes de estado
#generated-audio        → <audio> element
#player-section         → Sección del reproductor
#player-visualizer      → Canvas del visualizador
#send-to-radio-btn      → Botón de envío
#advanced-toggle        → Toggle de opciones
#music-select           → Selector de música
#duration-select        → Selector de duración
```

---

### 3. Estilos CSS (`automatic.css`)

**Ubicación:** `/var/www/casa/src/modules/automatic/styles/automatic.css`
**Líneas:** ~921
**Enfoque:** Mobile-First Responsive Design

#### Variables CSS (líneas 10-71)

```css
:root {
  /* Breakpoints */
  --mobile-sm: 320px;
  --mobile-md: 375px;
  --mobile-lg: 425px;
  --tablet: 768px;
  --desktop: 1024px;

  /* Touch targets */
  --touch-target-min: 44px;
  --touch-target-optimal: 48px;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  /* Typography responsive */
  --text-xs: clamp(0.75rem, 2.5vw, 0.875rem);
  --text-sm: clamp(0.875rem, 3vw, 1rem);
  --text-base: clamp(1rem, 3.5vw, 1.125rem);
  --text-lg: clamp(1.125rem, 4vw, 1.25rem);
  --text-xl: clamp(1.25rem, 4.5vw, 1.5rem);
  --text-2xl: clamp(1.5rem, 5vw, 2rem);
}
```

#### Componentes Clave

**Botón de Grabación** (líneas 116-173)
- Circular responsive: min(60vw, 220px)
- Gradiente animado
- Estados: normal, recording, active
- Animaciones: pulse-recording, ripple

**Voice Cards** (líneas 280-344)
- Scroll horizontal en móvil
- Grid en tablet/desktop
- Touch-optimized (minimal lag)
- Selected state con checkmark

**Status Messages** (líneas 205-244)
- Fixed position centrado
- Backdrop blur
- Estados diferenciados por color
- Animación fadeInScale

**Custom Audio Player** (líneas 374-472)
- Canvas visualizer clickeable
- Progress bar personalizada
- Time display tabular-nums
- Responsive controls

#### Optimizaciones

**Performance** (líneas 905-910)
```css
.automatic-record-btn,
.voice-card,
.automatic-action-btn {
  will-change: transform;
}
```

**Accesibilidad** (líneas 912-921)
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Touch Optimization** (líneas 76-80)
```css
* {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
```

---

## 🔄 Workflow Completo

### Fase 1: Captura de Voz (Frontend)

**Duración:** 0-20 segundos
**Ubicación:** `index.js::startRecording()` (línea 384)

```
1. Usuario presiona botón "Grabar"
   ↓
2. Verificar permisos de micrófono (HTTPS requerido)
   ↓
3. Iniciar Web Speech API
   - lang: 'es-CL'
   - continuous: true
   - interimResults: true
   ↓
4. Capturar transcripción en tiempo real
   - Mostrar texto parcial en timer
   - Acumular en this.state.transcribedText
   ↓
5. Usuario detiene o timer llega a 20 segundos
   ↓
6. Detener Web Speech API
   ↓
7. Validar que hay texto transcrito
   ↓
8. Mostrar selector de voces
```

### Fase 2: Selección de Voz (Frontend)

**Ubicación:** `index.js::selectVoice()` (línea 546)

```
1. Cargar lista de voces desde /api/generate.php
   action: 'list_voices'
   ↓
2. Renderizar voice cards
   - Filtrar solo voces activas
   - Ordenar por campo 'order'
   ↓
3. Usuario selecciona una voz
   ↓
4. [OPCIONAL] Usuario configura opciones avanzadas
   - Música personalizada
   - Duración objetivo
   ↓
5. Preparar request para backend
   {
     text: transcribedText,
     voice_id: selectedVoice,
     music_file: selectedMusic,
     target_duration: duration
   }
   ↓
6. POST a /api/automatic-jingle-service.php
```

### Fase 3: Procesamiento Backend

**Duración:** 5-15 segundos
**Ubicación:** `automatic-jingle-service.php::processAutomatic()` (línea 112)

#### 3.1 Validación de Entrada

```php
// Líneas 118-131
if ($isText) {
    $originalText = $textOrAudio;

    if (empty(trim($originalText))) {
        return [
            'success' => false,
            'error' => 'No se detectó ningún mensaje',
            'error_type' => 'empty_text'
        ];
    }
}
```

#### 3.2 Mejora de Texto con Claude

**Servicio:** `claude-service.php`
**Líneas:** 155-182

```php
// Determinar límites de palabras según duración
$wordLimits = $this->getWordLimits($targetDuration);
// 5s → [5, 8], 10s → [10, 15], 20s → [20, 30], etc.

$claudeParams = [
    'context' => $originalText,
    'category' => 'automatic',
    'mode' => 'automatic',
    'word_limit' => $wordLimits,
    'duration_seconds' => $targetDuration
];

$claudeResult = $this->claudeService->generateAnnouncements($claudeParams);
$improvedText = $claudeResult['suggestions'][0]['text'];
```

**Prompt usado por Claude:**
```
Mejora este mensaje para radio, manteniendo el tono conversacional y natural.
Debe tener entre X-Y palabras para una duración de Z segundos.
Mensaje original: [texto del usuario]
```

#### 3.3 Carga de Configuración

**Archivo:** `jingle-config.json` (línea 60-107)

```php
$jingleOptions = $this->getJingleConfig();
// Retorna:
[
    'music_file' => 'Uplift.mp3',
    'music_volume' => 1.65,
    'voice_volume' => 2.8,
    'fade_in' => 1.5,
    'fade_out' => 4.5,
    'music_duck' => true,
    'duck_level' => 0.95,
    'intro_silence' => 7,
    'outro_silence' => 4.5,
    'voice_settings' => [
        'style' => 0.15,
        'stability' => 1,
        'similarity_boost' => 0.5,
        'use_speaker_boost' => true
    ]
]
```

#### 3.4 Generación de Jingle

**Servicio:** `jingle-service.php::generateJingle()`
**Pasos:**

**A. Generar TTS** (tts-service.php)
```php
$ttsAudio = generateEnhancedTTS($text, $voice, $voice_settings);
// Llama a ElevenLabs API
// Retorna: audio binario MP3
```

**B. Procesar Música de Fondo**
```php
$musicPath = '/public/audio/music/' . $music_file;
// Aplicar fade in/out
// Ajustar volumen
```

**C. Mezcla con FFmpeg**
```bash
ffmpeg -i voice.mp3 -i music.mp3 \
  -filter_complex "[1]volume=${music_volume},afade=t=in:d=${fade_in},afade=t=out:d=${fade_out}[music];
                   [0]volume=${voice_volume}[voice];
                   [music][voice]amix=inputs=2:duration=first:dropout_transition=0,
                   compand=attacks=0.3:decays=0.8:points=-80/-80|-45/-45|-27/-25|-10/-7|20/-3:
                   soft-knee=6:gain=0:volume=0:delay=0.5" \
  -ar 44100 -ac 2 output.mp3
```

**D. Normalización LUFS** (opcional)
```php
if ($normalization_enabled) {
    $finalAudio = AudioProcessor::normalizeLUFS(
        $mixedAudio,
        $target_lufs = -16  // Broadcast standard
    );
}
```

#### 3.5 Guardar y Registrar

```php
// Guardar archivo (líneas 213-225)
$filename = "jingle_auto_{$timestamp}_{$voiceId}.mp3";
$tempPath = __DIR__ . '/temp/' . $filename;
file_put_contents($tempPath, $jingleResult['audio']);

// Registrar en BD (líneas 255-286)
$db = new SQLite3('/var/www/casa/database/casa.db');
$stmt = $db->prepare("
    INSERT INTO audio_metadata
    (filename, display_name, description, category, metadata, created_at)
    VALUES (?, ?, ?, 'automatic', ?, datetime('now'))
");
```

#### 3.6 Respuesta

```php
return [
    'success' => true,
    'original_text' => $originalText,
    'improved_text' => $improvedText,
    'voice_used' => $voiceId,
    'audio_url' => '/src/api/temp/' . $filename,
    'filename' => $filename,
    'duration' => $jingleResult['duration']
];
```

### Fase 4: Reproducción (Frontend)

**Ubicación:** `index.js::playGeneratedAudio()` (línea 646)

```
1. Recibir respuesta JSON del backend
   ↓
2. Ocultar mensaje de "procesando"
   ↓
3. Mostrar sección de reproductor
   ↓
4. Configurar audio source
   this.elements.audioPlayer.src = audioUrl
   ↓
5. Inicializar visualizador de canvas
   setupPlayerVisualizer()
   ↓
6. Auto-play después de 500ms
   ↓
7. Visualización de waveform en tiempo real
   - Web Audio API analyser
   - Canvas 2D drawing loop
   ↓
8. Controles de reproducción activos
   - Play/pause
   - Seek
   - Time display
```

### Fase 5: Envío a Radio

**Ubicación:** `index.js::sendToRadio()` (línea 831)

```
1. Usuario presiona "Enviar a Radio"
   ↓
2. POST a /api/generate.php
   {
     action: 'send_to_radio',
     filename: 'jingle_auto_...'
   }
   ↓
3. Backend copia archivo a carpeta de reproducción
   ↓
4. Añade a cola de radio automática
   ↓
5. Mostrar animación de éxito (📻)
   ↓
6. Toast "✅ Tu aviso se envió a la radio"
   ↓
7. Reset del módulo después de 3 segundos
```

---

## 📁 Archivos Críticos

### Estructura del Sistema Legacy

```
/var/www/casa/
├── src/
│   ├── modules/
│   │   └── automatic/
│   │       ├── index.js              ★★★ CORE - Módulo principal
│   │       ├── template.html         ★★★ CORE - Template UI
│   │       └── styles/
│   │           └── automatic.css     ★★★ CORE - Estilos mobile-first
│   │
│   └── api/
│       ├── automatic-jingle-service.php     ★★★ CORE - Orquestador principal
│       ├── generate.php                     ★★  - API de generación TTS y voces
│       ├── jingle-service.php               ★★★ CORE - Servicio de mezcla
│       ├── claude-service.php               ★★★ CORE - Mejora de texto con IA
│       ├── whisper-service.php              ★   - Transcripción (deprecated)
│       ├── music-service.php                ★★  - Gestión de música
│       ├── tts-service.php                  ★★  - Generación de TTS
│       ├── audio-processor.php              ★★  - Normalización LUFS
│       ├── automatic-usage-simple.php       ★   - Tracking de uso
│       │
│       └── data/
│           ├── jingle-config.json           ★★★ CONFIG - Configuración de jingles
│           ├── voices-config.json           ★★★ CONFIG - Configuración de voces
│           ├── tts-config.json              ★★  CONFIG - Configuración TTS
│           └── api-config.json              ★   CONFIG - API settings
│
├── public/
│   └── audio/
│       └── music/                           ★★  - Archivos de música de fondo
│           ├── Uplift.mp3
│           ├── Martin Roth - Just Sine Waves.mp3
│           └── [otros archivos MP3]
│
└── database/
    └── casa.db                              ★★  - SQLite database
        └── Tablas:
            ├── audio_metadata               → Almacena jingles generados
            └── automatic_usage              → Tracking de uso
```

### Prioridad de Implementación

**★★★ CRÍTICO** - No funciona sin estos archivos
**★★ IMPORTANTE** - Funcionalidad limitada sin estos
**★ OPCIONAL** - Features adicionales

---

## 🔌 Servicios Backend

### 1. AutomaticJingleService (automatic-jingle-service.php)

**Función:** Orquestador principal del flujo completo

**Métodos Públicos:**
```php
class AutomaticJingleService {
    public function processAutomatic(
        $textOrAudio,      // Texto transcrito o audio blob
        $voiceId,          // ID de voz (key: juan_carlos)
        $isText = false,   // true si es texto directo
        $musicFile = null, // Archivo de música personalizado
        $targetDuration = 20 // Duración objetivo en segundos
    )
}
```

**Dependencias:**
- `whisper-service.php` (deprecated, no se usa con Web Speech API)
- `claude-service.php`
- `jingle-service.php`
- `automatic-usage-simple.php`

**Configuración:** `jingle-config.json`

---

### 2. ClaudeService (claude-service.php)

**Función:** Mejora de texto con Claude AI

**API:** Anthropic Claude API v3 (Haiku)

**Método Principal:**
```php
public function generateAnnouncements($params) {
    // Params:
    // - context: texto original del usuario
    // - category: 'automatic'
    // - mode: 'automatic'
    // - word_limit: [min, max]
    // - duration_seconds: target duration

    // Retorna:
    // [
    //   'success' => true,
    //   'suggestions' => [
    //     ['text' => 'texto mejorado', 'reason' => '...']
    //   ]
    // ]
}
```

**Prompt Template:**
```
System: Eres un locutor profesional de radio. Mejora mensajes para
hacer jingles atractivos y profesionales. Mantén el tono natural
y conversacional. El mensaje debe durar aproximadamente X segundos,
usa entre Y-Z palabras.

User: Mensaje original: [texto del usuario]

Mejóralo para hacerlo más radiofónico, claro y atractivo.
```

**Rate Limiting:**
- Implementado en `automatic-usage-simple.php`
- Límite por IP: configurable

---

### 3. JingleService (jingle-service.php)

**Función:** Mezcla de TTS + música de fondo

**Función Principal:**
```php
function generateJingle($text, $voice, $options = []) {
    // Options:
    // - music_file: archivo de música
    // - music_volume: 0.0 - 2.0
    // - voice_volume: 0.0 - 2.0
    // - fade_in: segundos
    // - fade_out: segundos
    // - music_duck: true/false
    // - duck_level: 0.0 - 1.0
    // - intro_silence: segundos
    // - outro_silence: segundos
    // - voice_settings: array

    // Retorna:
    // [
    //   'success' => true,
    //   'audio' => binary MP3 data,
    //   'duration' => float seconds
    // ]
}
```

**Proceso FFmpeg:**

1. **Preparar Música**
```bash
ffmpeg -i input_music.mp3 \
  -af "volume=${music_volume},
       afade=t=in:st=0:d=${fade_in},
       afade=t=out:st=${duration-fade_out}:d=${fade_out}" \
  music_processed.mp3
```

2. **Generar TTS**
```php
$ttsAudio = generateEnhancedTTS($text, $voice, $voice_settings);
// Llama a ElevenLabs API
```

3. **Mezcla con Ducking**
```bash
ffmpeg -i voice.mp3 -i music_processed.mp3 \
  -filter_complex "
    [0]volume=${voice_volume}[voice];
    [1]volume=${music_volume}[music];
    [voice][music]sidechaincompress=
      threshold=${duck_level}:
      ratio=4:
      attack=200:
      release=1000
      [mixed]" \
  -map '[mixed]' output.mp3
```

4. **Compresión Dinámica**
```bash
ffmpeg -i mixed.mp3 \
  -af "compand=
        attacks=0.3:
        decays=0.8:
        points=-80/-80|-45/-45|-27/-25|-10/-7|20/-3:
        soft-knee=6:
        gain=0:
        volume=0:
        delay=0.5" \
  compressed.mp3
```

5. **Normalización LUFS** (opcional)
```php
AudioProcessor::normalizeLUFS($audio, -16);
// Target: -16 LUFS (broadcast standard)
```

**Dependencias:**
- FFmpeg 4.0+
- `tts-service.php`

---

### 4. MusicService (music-service.php)

**Función:** Gestión de música de fondo

**Función Principal:**
```php
function getAvailableMusic() {
    // Retorna:
    // [
    //   [
    //     'file' => 'Uplift.mp3',
    //     'name' => 'Uplift - Energético',
    //     'category' => 'upbeat',
    //     'mood' => 'energetic',
    //     'description' => 'Música...',
    //     'duration' => 180.5
    //   ],
    //   ...
    // ]
}
```

**Ubicación de Archivos:** `/public/audio/music/`

**Formatos Soportados:** MP3, WAV, OGG

---

### 5. TTSService (tts-service.php)

**Función:** Generación de TTS con ElevenLabs

**API:** ElevenLabs Text-to-Speech API v1/v3

**Función Principal:**
```php
function generateEnhancedTTS($text, $voiceId, $settings = []) {
    // Settings:
    // - style: 0.0 - 1.0
    // - stability: 0.0 - 1.0
    // - similarity_boost: 0.0 - 1.0
    // - use_speaker_boost: true/false

    // Endpoint: https://api.elevenlabs.io/v1/text-to-speech/{voiceId}

    // Retorna: binary MP3 data
}
```

**Voice IDs:** Configurados en `voices-config.json`

---

## ⚙️ Configuraciones

### 1. jingle-config.json

**Ubicación:** `/var/www/casa/src/api/data/jingle-config.json`

```json
{
  "jingle_defaults": {
    "enabled_by_default": false,
    "intro_silence": 7,            // Silencio antes del mensaje (segundos)
    "outro_silence": 4.5,          // Silencio después del mensaje
    "music_volume": 1.65,          // Volumen de música (multiplicador)
    "voice_volume": 2.8,           // Volumen de voz (multiplicador)
    "fade_in": 1.5,                // Fade in de música (segundos)
    "fade_out": 4.5,               // Fade out de música (segundos)
    "ducking_enabled": true,       // Reducir música durante voz
    "duck_level": 0.95,            // Nivel de ducking (0.0 = silencio, 1.0 = sin cambio)
    "default_music": "Uplift.mp3", // Música por defecto
    "voice_settings": {
      "style": 0.15,               // Estilo de voz (0 = neutro, 1 = expresivo)
      "stability": 1,              // Estabilidad (0 = variable, 1 = consistente)
      "similarity_boost": 0.5,     // Similitud con voz original
      "use_speaker_boost": true    // Boost de calidad
    },
    "normalization_settings": {
      "enabled": false,            // Normalización LUFS
      "target_lufs": -10,          // Target LUFS level
      "mode": "standard"           // standard, dynamic, aggressive
    },
    "compressor_settings": {
      "threshold": 0.055,          // Umbral de compresión
      "ratio": 6,                  // Ratio de compresión
      "attack": 5,                 // Attack time (ms)
      "release": 200,              // Release time (ms)
      "makeup": 1.4                // Makeup gain
    }
  },
  "allowed_music": "all",          // "all" o array de archivos permitidos
  "user_can_override": false       // Permitir usuario cambiar config
}
```

**Valores Recomendados para Broadcast:**

- **intro_silence:** 2-7 segundos (suficiente para captar atención)
- **outro_silence:** 3-5 segundos (transición suave)
- **music_volume:** 0.3-0.5 para música como fondo, 1.0-2.0 para música prominente
- **voice_volume:** 1.0-3.0 (siempre debe ser más alto que música)
- **duck_level:** 0.15-0.3 (reduce música 70-85% durante voz)
- **target_lufs:** -16 LUFS (estándar broadcast), -14 LUFS (streaming), -23 LUFS (TV)

---

### 2. voices-config.json

**Ubicación:** `/var/www/casa/src/api/data/voices-config.json`

```json
{
  "voices": {
    "juan_carlos": {
      "id": "G4IAP30yc6c1gK0csDfu",        // ID real de ElevenLabs
      "label": "Juan Carlos",               // Nombre mostrado al usuario
      "gender": "M",                        // M o F
      "active": true,                       // Mostrar en UI
      "is_default": false,                  // Voz por defecto
      "order": 1,                           // Orden de visualización
      "description": "Voz masculina profesional",
      "language": "es",                     // Idioma
      "accent": "neutral"                   // Acento
    },
    "veronica": {
      "id": "jsCqWAovK2LkecY7zXl4",
      "label": "Verónica",
      "gender": "F",
      "active": true,
      "is_default": true,
      "order": 2,
      "description": "Voz femenina cálida",
      "language": "es",
      "accent": "chilean"
    }
    // ... más voces
  }
}
```

**Notas:**
- `id`: ID real de ElevenLabs (no cambiar)
- `key` (juan_carlos): usado internamente en el código
- `active: false`: oculta la voz sin eliminarla
- `order`: determina posición en el selector

---

### 3. tts-config.json

**Ubicación:** `/var/www/casa/src/api/data/tts-config.json`

```json
{
  "voice_settings": {
    "style": 0.5,
    "stability": 0.75,
    "similarity_boost": 0.8,
    "use_speaker_boost": true
  },
  "normalization": {
    "output_volume": 1.0
  }
}
```

---

## 🔗 Dependencias Externas

### APIs de Terceros

#### 1. ElevenLabs Text-to-Speech API

**Versión:** v1 (producción), v3 (beta)
**Endpoint:** `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
**Autenticación:** API Key en header `xi-api-key`

**Request:**
```json
{
  "text": "Texto a sintetizar",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.75,
    "similarity_boost": 0.8,
    "style": 0.5,
    "use_speaker_boost": true
  }
}
```

**Response:** Binary MP3 data

**Rate Limits:**
- Free tier: 10,000 caracteres/mes
- Creator tier: 100,000 caracteres/mes
- Pro tier: 500,000 caracteres/mes

**Costos (aproximados):**
- $0.30 por 1,000 caracteres (Creator)
- $0.18 por 1,000 caracteres (Pro)

**Ejemplo:** Un jingle de 30 palabras (~150 caracteres) = $0.045

---

#### 2. Anthropic Claude API

**Versión:** Claude 3 Haiku
**Endpoint:** `https://api.anthropic.com/v1/messages`
**Autenticación:** API Key en header `x-api-key`

**Request:**
```json
{
  "model": "claude-3-haiku-20240307",
  "max_tokens": 200,
  "temperature": 0.7,
  "messages": [
    {
      "role": "user",
      "content": "Mejora este texto: [texto original]"
    }
  ]
}
```

**Rate Limits:**
- Tier 1: 50 requests/min
- Tier 2: 1000 requests/min

**Costos:**
- Haiku: $0.25 / 1M tokens input, $1.25 / 1M tokens output
- Promedio por jingle: ~100 tokens = $0.0001

---

### Software Backend

#### 1. FFmpeg

**Versión Mínima:** 4.0
**Recomendada:** 4.4+

**Codecs Requeridos:**
- libmp3lame (MP3 encoding)
- aac (AAC encoding)

**Filtros Usados:**
- `volume` - Ajuste de volumen
- `afade` - Fade in/out
- `amix` - Mezcla de audio
- `sidechaincompress` - Ducking
- `compand` - Compresión dinámica
- `loudnorm` - Normalización LUFS

**Instalación:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Verificar instalación
ffmpeg -version
ffmpeg -filters | grep -E "(volume|amix|loudnorm)"
```

---

#### 2. PHP Extensions

**Requeridas:**
- `php-curl` (llamadas a APIs)
- `php-json` (parsing JSON)
- `php-sqlite3` (base de datos)
- `php-mbstring` (manejo de strings)

**Instalación:**
```bash
# Ubuntu/Debian
sudo apt-get install php-curl php-json php-sqlite3 php-mbstring

# Verificar
php -m | grep -E "(curl|json|sqlite3|mbstring)"
```

---

#### 3. SQLite3

**Versión:** 3.x

**Schema Requerido:**
```sql
CREATE TABLE audio_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    display_name TEXT,
    description TEXT,
    category TEXT,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE automatic_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT,
    access_token TEXT,
    text_length INTEGER,
    voice_used TEXT,
    music_used TEXT,
    duration INTEGER,
    success INTEGER,
    error_message TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### Navegador (Frontend)

#### APIs Requeridas

**1. Web Speech API**
- **Soporte:** Chrome, Edge, Safari 14.1+
- **Requiere:** HTTPS (excepto localhost)
- **Idiomas:** Depende del navegador

**Verificación:**
```javascript
if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('Tu navegador no soporta reconocimiento de voz');
}
```

**2. Web Audio API**
- **Soporte:** Todos los navegadores modernos
- **Usado para:** Visualización de waveform

**3. Canvas API**
- **Soporte:** Universal
- **Usado para:** Dibujar visualizadores

---

## 🚀 Guía de Implementación para MediaFlow v2.1

### Fase 1: Preparación del Entorno

#### 1.1 Verificar Dependencias

```bash
# Verificar FFmpeg
ffmpeg -version
# Debe mostrar versión 4.0+

# Verificar PHP extensions
php -m | grep -E "(curl|json|sqlite3|mbstring)"

# Verificar SQLite
sqlite3 --version
```

#### 1.2 Crear Estructura de Directorios

```bash
cd /var/www/mediaflow-v2

# Backend
mkdir -p backend/app/api/v1/services/automatic
mkdir -p backend/storage/audio/temp
mkdir -p backend/storage/audio/music
mkdir -p backend/app/config/automatic

# Frontend
mkdir -p frontend/src/components/settings/automatic
mkdir -p frontend/src/composables/automatic
```

#### 1.3 Configurar Permisos

```bash
# Permisos de escritura para audio generado
chmod 755 backend/storage/audio/temp
chown www-data:www-data backend/storage/audio/temp

# Permisos de lectura para música
chmod 755 backend/storage/audio/music
```

---

### Fase 2: Migración del Backend

#### 2.1 Copiar Servicios PHP

**Prioridad 1 - Servicios Core:**

```bash
# Orquestador principal
cp /var/www/casa/src/api/automatic-jingle-service.php \
   /var/www/mediaflow-v2/backend/app/api/v1/services/automatic/AutomaticJingleService.php

# Servicio de mezcla
cp /var/www/casa/src/api/jingle-service.php \
   /var/www/mediaflow-v2/backend/app/api/v1/services/automatic/JingleService.php

# Mejora de texto con IA
cp /var/www/casa/src/api/claude-service.php \
   /var/www/mediaflow-v2/backend/app/api/v1/services/automatic/ClaudeService.php
```

**Prioridad 2 - Servicios Complementarios:**

```bash
# TTS
cp /var/www/casa/src/api/tts-service.php \
   /var/www/mediaflow-v2/backend/app/api/v1/services/TTSService.php

# Música
cp /var/www/casa/src/api/music-service.php \
   /var/www/mediaflow-v2/backend/app/api/v1/services/MusicService.php

# Procesador de audio
cp /var/www/casa/src/api/audio-processor.php \
   /var/www/mediaflow-v2/backend/app/api/v1/services/AudioProcessor.php
```

#### 2.2 Adaptar Código PHP a Estructura v2.1

**Cambios Necesarios:**

1. **Namespaces:**
```php
// Antiguo (Legacy)
class AutomaticJingleService { }

// Nuevo (v2.1)
namespace App\Services\Automatic;

class AutomaticJingleService { }
```

2. **Rutas de Archivos:**
```php
// Antiguo
$tempPath = __DIR__ . '/temp/' . $filename;
$configFile = __DIR__ . '/data/jingle-config.json';

// Nuevo
$tempPath = storage_path('audio/temp/' . $filename);
$configFile = config_path('automatic/jingle-config.json');
```

3. **Base de Datos:**
```php
// Antiguo
$db = new SQLite3('/var/www/casa/database/casa.db');

// Nuevo (usar FastAPI/SQLAlchemy desde PHP)
// O adaptar a PostgreSQL/MySQL si es el caso
```

#### 2.3 Crear Endpoint API

**Archivo:** `backend/app/api/v1/endpoints/automatic.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import subprocess
import json

router = APIRouter()

class AutomaticJingleRequest(BaseModel):
    text: str
    voice_id: str
    music_file: Optional[str] = None
    target_duration: Optional[int] = 20

@router.post("/automatic/generate")
async def generate_automatic_jingle(request: AutomaticJingleRequest):
    """
    Genera un jingle automático desde texto transcrito
    """
    try:
        # Llamar al servicio PHP usando subprocess
        # (Temporal hasta migrar completamente a Python)
        php_script = "/var/www/mediaflow-v2/backend/app/api/v1/services/automatic/AutomaticJingleService.php"

        result = subprocess.run(
            ["php", php_script],
            input=json.dumps(request.dict()),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        response = json.loads(result.stdout)
        return response

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Timeout processing jingle")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/automatic/voices")
async def list_voices():
    """
    Lista todas las voces disponibles para el modo automático
    """
    # Leer desde voices-config.json
    pass
```

#### 2.4 Copiar Configuraciones

```bash
# Configuración de jingles
cp /var/www/casa/src/api/data/jingle-config.json \
   /var/www/mediaflow-v2/backend/app/config/automatic/

# Configuración de voces
cp /var/www/casa/src/api/data/voices-config.json \
   /var/www/mediaflow-v2/backend/app/config/automatic/

# Configuración de TTS
cp /var/www/casa/src/api/data/tts-config.json \
   /var/www/mediaflow-v2/backend/app/config/automatic/
```

#### 2.5 Copiar Música de Fondo

```bash
# Copiar archivos de música
cp -r /var/www/casa/public/audio/music/* \
      /var/www/mediaflow-v2/backend/storage/audio/music/

# Verificar permisos
chmod 644 /var/www/mediaflow-v2/backend/storage/audio/music/*.mp3
```

---

### Fase 3: Migración del Frontend

#### 3.1 Crear Componente Vue Principal

**Archivo:** `frontend/src/components/settings/automatic/AutomaticMode.vue`

```vue
<template>
  <div class="automatic-mode min-h-screen bg-base-100">
    <SettingsNav />

    <div class="p-6">
      <div class="container mx-auto max-w-4xl">

        <!-- Recording Section -->
        <RecordingSection
          :is-recording="isRecording"
          :recording-seconds="recordingSeconds"
          :transcribed-text="transcribedText"
          @toggle-recording="toggleRecording"
        />

        <!-- Voice Selection -->
        <VoiceSelection
          v-if="showVoiceSelection"
          :voices="voices"
          :selected-voice="selectedVoice"
          :advanced-mode="advancedMode"
          :music-list="musicList"
          @select-voice="handleSelectVoice"
          @toggle-advanced="advancedMode = !advancedMode"
        />

        <!-- Audio Player -->
        <AudioPlayer
          v-if="generatedAudio"
          :audio-url="generatedAudio.audio_url"
          :improved-text="generatedAudio.improved_text"
          @send-to-radio="handleSendToRadio"
        />

        <!-- Status Messages -->
        <StatusMessage
          v-if="statusMessage"
          :message="statusMessage.text"
          :type="statusMessage.type"
        />

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SettingsNav from '../SettingsNav.vue'
import RecordingSection from './components/RecordingSection.vue'
import VoiceSelection from './components/VoiceSelection.vue'
import AudioPlayer from './components/AudioPlayer.vue'
import StatusMessage from './components/StatusMessage.vue'
import { useAutomaticMode } from './composables/useAutomaticMode'

const {
  isRecording,
  recordingSeconds,
  transcribedText,
  showVoiceSelection,
  voices,
  selectedVoice,
  musicList,
  generatedAudio,
  statusMessage,
  advancedMode,
  toggleRecording,
  handleSelectVoice,
  handleSendToRadio,
  loadVoices,
  loadMusicList
} = useAutomaticMode()

onMounted(() => {
  loadVoices()
  loadMusicList()
})
</script>
```

#### 3.2 Crear Composable useAutomaticMode

**Archivo:** `frontend/src/composables/automatic/useAutomaticMode.ts`

```typescript
import { ref, Ref } from 'vue'

// Web Speech API types
interface SpeechRecognition extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  maxAlternatives: number
  start(): void
  stop(): void
  onerror: (event: any) => void
  onresult: (event: any) => void
  onend: () => void
}

declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

export interface Voice {
  key: string
  id: string
  label: string
  gender: 'M' | 'F'
  active: boolean
  order: number
}

export interface GeneratedAudio {
  success: boolean
  original_text: string
  improved_text: string
  voice_used: string
  audio_url: string
  filename: string
  duration?: number
}

export function useAutomaticMode() {
  // State
  const isRecording = ref(false)
  const recordingSeconds = ref(0)
  const transcribedText = ref('')
  const showVoiceSelection = ref(false)
  const voices: Ref<Voice[]> = ref([])
  const selectedVoice = ref<string | null>(null)
  const musicList = ref([])
  const generatedAudio: Ref<GeneratedAudio | null> = ref(null)
  const statusMessage = ref<{ text: string; type: string } | null>(null)
  const advancedMode = ref(false)

  // Web Speech API
  let recognition: SpeechRecognition | null = null
  let recordingTimer: number | null = null

  /**
   * Cargar lista de voces disponibles
   */
  const loadVoices = async () => {
    try {
      const response = await fetch('/api/v1/settings/voices')
      const data = await response.json()

      if (data.success) {
        voices.value = Object.entries(data.voices).map(([key, voice]: [string, any]) => ({
          key,
          id: voice.id,
          label: voice.label,
          gender: voice.gender,
          active: voice.active !== false,
          order: voice.order || 999
        }))
        .filter(v => v.active)
        .sort((a, b) => a.order - b.order)
      }
    } catch (error) {
      console.error('Error loading voices:', error)
    }
  }

  /**
   * Cargar lista de música disponible
   */
  const loadMusicList = async () => {
    try {
      const response = await fetch('/api/v1/automatic/music')
      const data = await response.json()

      if (data.success) {
        musicList.value = data.music
      }
    } catch (error) {
      console.error('Error loading music:', error)
    }
  }

  /**
   * Toggle grabación
   */
  const toggleRecording = async () => {
    if (isRecording.value) {
      stopRecording()
    } else {
      await startRecording()
    }
  }

  /**
   * Iniciar grabación con Web Speech API
   */
  const startRecording = async () => {
    try {
      // Verificar soporte
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showStatus('Tu navegador no soporta reconocimiento de voz. Usa Chrome o Edge.', 'error')
        return
      }

      // Resetear estado
      transcribedText.value = ''
      showVoiceSelection.value = false
      generatedAudio.value = null

      // Crear instancia de reconocimiento
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognition = new SpeechRecognition()

      // Configurar
      recognition.lang = 'es-CL'
      recognition.continuous = true
      recognition.interimResults = true
      recognition.maxAlternatives = 1

      let finalTranscript = ''

      // Eventos
      recognition.onresult = (event: any) => {
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' '
          } else {
            interimTranscript = transcript
          }
        }

        transcribedText.value = (finalTranscript + interimTranscript).trim()
      }

      recognition.onerror = (event: any) => {
        console.error('Recognition error:', event.error)
        if (event.error === 'no-speech') {
          showStatus('No se detectó voz. Intenta de nuevo.', 'error')
        } else if (event.error === 'not-allowed') {
          showStatus('Permite el acceso al micrófono para continuar.', 'error')
        }
        stopRecording()
      }

      recognition.onend = () => {
        if (isRecording.value) {
          stopRecording()
        }
      }

      // Iniciar
      recognition.start()
      isRecording.value = true

      // Timer (máximo 20 segundos)
      recordingSeconds.value = 0
      recordingTimer = window.setInterval(() => {
        recordingSeconds.value++
        if (recordingSeconds.value >= 20) {
          stopRecording()
        }
      }, 1000)

      showStatus('Escuchando... Habla ahora', 'info')

    } catch (error) {
      console.error('Error starting recording:', error)
      showStatus('Error al iniciar reconocimiento de voz', 'error')
    }
  }

  /**
   * Detener grabación
   */
  const stopRecording = () => {
    if (recognition) {
      recognition.stop()
      recognition = null
    }

    isRecording.value = false

    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }

    // Validar texto
    if (transcribedText.value && transcribedText.value.trim()) {
      showVoiceSelection.value = true
      showStatus('Selecciona una voz para continuar', 'info')
    } else {
      showStatus('No se detectó ningún mensaje. Intenta de nuevo.', 'error')
    }
  }

  /**
   * Seleccionar voz y procesar
   */
  const handleSelectVoice = async (voiceKey: string) => {
    if (!transcribedText.value) return

    selectedVoice.value = voiceKey
    showStatus('Generando jingle...', 'processing')

    try {
      const response = await fetch('/api/v1/automatic/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: transcribedText.value,
          voice_id: voiceKey,
          music_file: advancedMode.value ? selectedMusic.value : undefined,
          target_duration: advancedMode.value ? selectedDuration.value : 20
        })
      })

      const data = await response.json()

      if (data.success) {
        generatedAudio.value = data
        hideStatus()
        // Auto-play se maneja en AudioPlayer component
      } else {
        showStatus('Error: ' + data.error, 'error')
      }

    } catch (error) {
      console.error('Error processing:', error)
      showStatus('Error al procesar el audio', 'error')
    }
  }

  /**
   * Enviar a radio
   */
  const handleSendToRadio = async () => {
    if (!generatedAudio.value) return

    showStatus('Enviando a la radio...', 'processing')

    try {
      const response = await fetch('/api/v1/automatic/send-to-radio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: generatedAudio.value.filename
        })
      })

      const data = await response.json()

      if (data.success) {
        showStatus('✅ Tu aviso se envió a la radio', 'success')

        // Reset después de 3 segundos
        setTimeout(() => {
          resetState()
        }, 3000)
      } else {
        showStatus('Error enviando a radio', 'error')
      }

    } catch (error) {
      console.error('Error sending to radio:', error)
      showStatus('Error al enviar a la radio', 'error')
    }
  }

  /**
   * Mostrar mensaje de estado
   */
  const showStatus = (text: string, type: string) => {
    statusMessage.value = { text, type }

    if (type !== 'processing') {
      setTimeout(() => {
        hideStatus()
      }, 5000)
    }
  }

  /**
   * Ocultar mensaje de estado
   */
  const hideStatus = () => {
    statusMessage.value = null
  }

  /**
   * Reset completo del estado
   */
  const resetState = () => {
    transcribedText.value = ''
    showVoiceSelection.value = false
    selectedVoice.value = null
    generatedAudio.value = null
    statusMessage.value = null
    advancedMode.value = false
  }

  return {
    isRecording,
    recordingSeconds,
    transcribedText,
    showVoiceSelection,
    voices,
    selectedVoice,
    musicList,
    generatedAudio,
    statusMessage,
    advancedMode,
    toggleRecording,
    handleSelectVoice,
    handleSendToRadio,
    loadVoices,
    loadMusicList
  }
}
```

#### 3.3 Crear Componentes Hijos

**RecordingSection.vue:**
- Botón grande de grabación
- Timer
- Visualización del texto transcrito

**VoiceSelection.vue:**
- Grid/scroll de voice cards
- Advanced options panel
- Music selector
- Duration selector

**AudioPlayer.vue:**
- Custom player con canvas visualizer
- Controles play/pause/seek
- Botón "Enviar a Radio"

**StatusMessage.vue:**
- Toast message flotante
- Estados: info, processing, success, error

#### 3.4 Migrar Estilos CSS

**Opción 1: Usar Tailwind (Recomendado para v2.1)**

Convertir las clases custom de `automatic.css` a utility classes de Tailwind.

**Opción 2: Usar CSS Modules**

Copiar `automatic.css` como módulo scoped en el componente Vue.

```vue
<style scoped src="./styles/automatic.css"></style>
```

---

### Fase 4: Testing

#### 4.1 Test de Web Speech API

```javascript
// Test en consola del navegador
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
if (SpeechRecognition) {
  const recognition = new SpeechRecognition()
  recognition.lang = 'es-CL'
  recognition.start()
  console.log('Web Speech API funcionando')
} else {
  console.error('Web Speech API no soportada')
}
```

#### 4.2 Test de Backend

```bash
# Test del servicio de jingles
curl -X POST http://localhost:8000/api/v1/automatic/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola este es un mensaje de prueba",
    "voice_id": "juan_carlos",
    "target_duration": 20
  }'

# Debe retornar JSON con success: true y audio_url
```

#### 4.3 Test de FFmpeg

```bash
# Verificar que FFmpeg puede procesar audio
ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 5 test.mp3
# Debe crear test.mp3 sin errores
```

#### 4.4 Test End-to-End

1. Abrir navegador en `https://demo.mediaflow.cl/settings/automatic`
2. Presionar botón "Grabar"
3. Permitir acceso al micrófono
4. Hablar un mensaje corto
5. Detener grabación
6. Seleccionar una voz
7. Esperar generación (5-15 segundos)
8. Verificar que el audio se reproduce correctamente
9. Presionar "Enviar a Radio"
10. Verificar mensaje de éxito

---

### Fase 5: Optimización

#### 5.1 Caching

**Voces:**
```typescript
// Cache de voces en localStorage
const CACHE_KEY = 'automatic_voices_cache'
const CACHE_DURATION = 1000 * 60 * 60 * 24 // 24 horas

const loadVoices = async () => {
  // Intentar cargar desde cache
  const cached = localStorage.getItem(CACHE_KEY)
  if (cached) {
    const { timestamp, data } = JSON.parse(cached)
    if (Date.now() - timestamp < CACHE_DURATION) {
      voices.value = data
      return
    }
  }

  // Cargar desde API
  const response = await fetch('/api/v1/settings/voices')
  const data = await response.json()

  // Guardar en cache
  localStorage.setItem(CACHE_KEY, JSON.stringify({
    timestamp: Date.now(),
    data: data.voices
  }))

  voices.value = data.voices
}
```

#### 5.2 Rate Limiting en Backend

```python
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def rate_limit_check(request: Request):
    """
    Rate limiting: 10 requests por IP por hora
    """
    ip = request.client.host
    key = f"rate_limit:automatic:{ip}"

    count = redis_client.get(key)

    if count is None:
        redis_client.setex(key, 3600, 1)
    else:
        count = int(count)
        if count >= 10:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again in 1 hour."
            )
        redis_client.incr(key)

    return True
```

#### 5.3 Lazy Loading de Música

```typescript
// Solo cargar lista de música cuando se abre advanced options
const loadMusicList = async () => {
  if (musicList.value.length > 0) return // Ya cargada

  try {
    const response = await fetch('/api/v1/automatic/music')
    const data = await response.json()
    musicList.value = data.music
  } catch (error) {
    console.error('Error loading music:', error)
  }
}

// Llamar solo cuando se expande advanced options
watch(advancedMode, (isAdvanced) => {
  if (isAdvanced) {
    loadMusicList()
  }
})
```

---

## 🔐 Consideraciones de Seguridad

### 1. HTTPS Obligatorio

**Razón:** Web Speech API requiere contexto seguro

**Implementación:**
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name demo.mediaflow.cl;

    ssl_certificate /etc/letsencrypt/live/demo.mediaflow.cl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/demo.mediaflow.cl/privkey.pem;

    # Force HTTPS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name demo.mediaflow.cl;
    return 301 https://$server_name$request_uri;
}
```

### 2. Validación de Entrada

**Backend:**
```php
// Validar texto transcrito
function validateTranscribedText($text) {
    // Longitud mínima
    if (strlen(trim($text)) < 3) {
        throw new Exception('Texto demasiado corto');
    }

    // Longitud máxima (prevenir abuse)
    if (strlen($text) > 1000) {
        throw new Exception('Texto demasiado largo');
    }

    // Sanitizar HTML
    $text = strip_tags($text);

    // Eliminar caracteres especiales peligrosos
    $text = preg_replace('/[^\p{L}\p{N}\s\.,\!\?]/u', '', $text);

    return $text;
}
```

**Frontend:**
```typescript
// Validar antes de enviar
const validateText = (text: string): boolean => {
  // No vacío
  if (!text || !text.trim()) {
    showStatus('No se detectó ningún mensaje', 'error')
    return false
  }

  // Longitud mínima
  if (text.trim().length < 3) {
    showStatus('El mensaje es demasiado corto', 'error')
    return false
  }

  // Longitud máxima
  if (text.length > 1000) {
    showStatus('El mensaje es demasiado largo', 'error')
    return false
  }

  return true
}
```

### 3. Rate Limiting

**Por IP:**
```php
// automatic-rate-limiter.php
class RateLimiter {
    private $db;
    private $maxRequests = 10; // 10 requests
    private $timeWindow = 3600; // por hora

    public function checkLimit($ip) {
        $stmt = $this->db->prepare("
            SELECT COUNT(*) as count
            FROM automatic_usage
            WHERE ip_address = ?
            AND created_at > datetime('now', '-1 hour')
        ");

        $stmt->bindValue(1, $ip);
        $result = $stmt->execute()->fetchArray();

        if ($result['count'] >= $this->maxRequests) {
            throw new Exception('Rate limit exceeded');
        }

        return true;
    }
}
```

### 4. Sanitización de Audio

**Verificar formato:**
```php
// Verificar que el archivo generado es realmente MP3
function verifyAudioFile($filePath) {
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mimeType = finfo_file($finfo, $filePath);
    finfo_close($finfo);

    if ($mimeType !== 'audio/mpeg') {
        unlink($filePath);
        throw new Exception('Invalid audio format');
    }

    return true;
}
```

### 5. Protección de API Keys

**Usar variables de entorno:**
```php
// config.php
define('ELEVENLABS_API_KEY', getenv('ELEVENLABS_API_KEY'));
define('ANTHROPIC_API_KEY', getenv('ANTHROPIC_API_KEY'));

// NUNCA hardcodear en el código
// ❌ define('ELEVENLABS_API_KEY', 'sk-abc123...');
```

**.env:**
```bash
ELEVENLABS_API_KEY=sk-abc123def456...
ANTHROPIC_API_KEY=sk-ant-xyz789...
```

**Cargar en servidor:**
```bash
# En .bashrc o .bash_profile
export ELEVENLABS_API_KEY="sk-abc123..."
export ANTHROPIC_API_KEY="sk-ant-xyz..."
```

### 6. Limpieza de Archivos Temporales

**Cron job para limpiar archivos antiguos:**
```bash
# Limpiar archivos MP3 temporales más antiguos de 24 horas
0 */6 * * * find /var/www/mediaflow-v2/backend/storage/audio/temp -name "jingle_auto_*.mp3" -mtime +1 -delete
```

**Verificación de espacio:**
```bash
# Script de monitoreo
#!/bin/bash
THRESHOLD=90
USAGE=$(df /var/www/mediaflow-v2/backend/storage | awk 'NR==2 {print $5}' | sed 's/%//')

if [ $USAGE -gt $THRESHOLD ]; then
    echo "Storage usage critical: ${USAGE}%"
    # Limpiar archivos más antiguos de 1 hora
    find /var/www/mediaflow-v2/backend/storage/audio/temp -name "*.mp3" -mmin +60 -delete
fi
```

### 7. Logs de Auditoría

**Registrar todas las operaciones:**
```php
// Logger con detalles completos
function logAutomaticUsage($data) {
    $logEntry = [
        'timestamp' => date('Y-m-d H:i:s'),
        'ip' => $_SERVER['REMOTE_ADDR'],
        'user_agent' => $_SERVER['HTTP_USER_AGENT'],
        'text_length' => strlen($data['text']),
        'voice_used' => $data['voice_id'],
        'music_used' => $data['music_file'] ?? 'default',
        'duration' => $data['target_duration'],
        'success' => $data['success'],
        'error' => $data['error'] ?? null
    ];

    // Guardar en base de datos
    $db->insert('automatic_usage', $logEntry);

    // Log file para debugging
    file_put_contents(
        '/var/log/mediaflow/automatic.log',
        json_encode($logEntry) . "\n",
        FILE_APPEND
    );
}
```

---

## 📊 Métricas y Monitoreo

### Métricas Importantes

1. **Tasa de Éxito:**
   - % de grabaciones que resultan en jingle exitoso
   - Target: > 95%

2. **Tiempo de Procesamiento:**
   - Promedio de tiempo backend
   - Target: < 10 segundos

3. **Calidad de Transcripción:**
   - % de textos que requieren re-grabación
   - Target: < 10%

4. **Uso de Recursos:**
   - CPU usage durante generación FFmpeg
   - Storage usado por archivos temporales
   - API calls a ElevenLabs/Claude

5. **Rate Limiting:**
   - Requests por hora por IP
   - Requests bloqueados

### Herramientas de Monitoreo

```bash
# Monitorear logs en tiempo real
tail -f /var/log/mediaflow/automatic.log | jq

# Ver métricas de uso
sqlite3 /var/www/mediaflow-v2/database/mediaflow.db \
  "SELECT DATE(created_at) as date,
          COUNT(*) as total_requests,
          SUM(success) as successful,
          AVG(duration) as avg_duration
   FROM automatic_usage
   GROUP BY DATE(created_at)
   ORDER BY date DESC
   LIMIT 7"
```

---

## 🎓 Recursos Adicionales

### Documentación de APIs

- **Web Speech API:** https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **ElevenLabs API:** https://docs.elevenlabs.io/api-reference
- **Anthropic Claude API:** https://docs.anthropic.com/claude/reference
- **FFmpeg Documentation:** https://ffmpeg.org/documentation.html

### Tutoriales Relevantes

- Web Speech API en Español: https://developer.mozilla.org/es/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API
- Audio Processing with FFmpeg: https://trac.ffmpeg.org/wiki/AudioChannelManipulation
- LUFS Normalization: https://www.audiokinetic.com/en/library/edge/?source=Help&id=understanding_loudness

---

## 📝 Checklist de Implementación

### Backend ✓
- [ ] Copiar servicios PHP core
- [ ] Adaptar namespaces y rutas
- [ ] Crear endpoints API REST
- [ ] Migrar configuraciones JSON
- [ ] Copiar música de fondo
- [ ] Configurar permisos de archivos
- [ ] Implementar rate limiting
- [ ] Configurar logs de auditoría
- [ ] Setup cron job para limpieza
- [ ] Verificar FFmpeg instalado

### Frontend ✓
- [ ] Crear componente AutomaticMode.vue
- [ ] Crear composable useAutomaticMode
- [ ] Crear componentes hijos (Recording, VoiceSelection, etc.)
- [ ] Migrar estilos CSS / convertir a Tailwind
- [ ] Implementar Web Speech API
- [ ] Implementar visualizador de audio
- [ ] Agregar a router de Settings
- [ ] Agregar a SettingsNav
- [ ] Testing en Chrome/Edge
- [ ] Testing en dispositivos móviles

### Configuración ✓
- [ ] Configurar HTTPS
- [ ] Configurar variables de entorno (API keys)
- [ ] Verificar permisos de micrófono
- [ ] Setup base de datos (tablas)
- [ ] Configurar nginx/apache
- [ ] Configurar CORS

### Testing ✓
- [ ] Test de Web Speech API
- [ ] Test de backend endpoints
- [ ] Test de FFmpeg processing
- [ ] Test end-to-end completo
- [ ] Test de rate limiting
- [ ] Test de validación de entrada
- [ ] Test de limpieza de archivos
- [ ] Test en diferentes navegadores
- [ ] Test en móviles (iOS/Android)

### Documentación ✓
- [ ] Documentar configuraciones
- [ ] Documentar endpoints API
- [ ] Documentar flujo de trabajo
- [ ] Crear guía de troubleshooting
- [ ] Documentar métricas y monitoreo

---

## 🐛 Troubleshooting Común

### Problema: "Tu navegador no soporta reconocimiento de voz"

**Causa:** Web Speech API no disponible

**Solución:**
1. Usar Chrome o Edge (mejor soporte)
2. Verificar que el sitio usa HTTPS
3. Verificar en `chrome://flags` que Web Speech API está habilitado

### Problema: "No se detectó ningún mensaje"

**Causa:** Micrófono no captura audio o transcripción vacía

**Solución:**
1. Verificar permisos de micrófono en navegador
2. Probar con otro micrófono
3. Verificar que `lang: 'es-CL'` está configurado
4. Hablar más cerca del micrófono

### Problema: Error 500 en backend

**Causa:** FFmpeg falla o servicios PHP no encuentran dependencias

**Solución:**
```bash
# Verificar logs
tail -50 /var/log/mediaflow/automatic.log

# Verificar FFmpeg
which ffmpeg
ffmpeg -version

# Verificar permisos
ls -la /var/www/mediaflow-v2/backend/storage/audio/temp

# Test manual de FFmpeg
ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 5 test.mp3
```

### Problema: Audio con volumen muy bajo o muy alto

**Causa:** Configuración de volumes incorrecta

**Solución:** Ajustar en `jingle-config.json`:
```json
{
  "music_volume": 0.3,    // Bajar si música tapa voz
  "voice_volume": 2.0,    // Subir si voz se escucha bajo
  "normalization_settings": {
    "enabled": true,      // Activar normalización
    "target_lufs": -16    // Estándar broadcast
  }
}
```

### Problema: Música no hace ducking

**Causa:** Ducking deshabilitado o mal configurado

**Solución:**
```json
{
  "ducking_enabled": true,
  "duck_level": 0.2      // 0.2 = reduce música 80%
}
```

### Problema: Rate limit exceeded

**Causa:** Demasiadas requests desde una IP

**Solución:**
```bash
# Ver requests recientes
sqlite3 /var/www/mediaflow-v2/database/mediaflow.db \
  "SELECT ip_address, COUNT(*) as requests
   FROM automatic_usage
   WHERE created_at > datetime('now', '-1 hour')
   GROUP BY ip_address
   ORDER BY requests DESC"

# Limpiar rate limit de una IP específica (desarrollo)
redis-cli DEL "rate_limit:automatic:192.168.1.100"
```

---

**FIN DE DOCUMENTACIÓN**

---

**Notas Finales:**

Esta documentación fue generada analizando el sistema Legacy de Casa Costanera. Para actualizaciones o preguntas específicas de implementación, consultar el código fuente original en `/var/www/casa/src/modules/automatic/`.

**Última actualización:** 3 de diciembre de 2025
**Autor:** Claude Code - Anthropic
**Versión:** 1.0
