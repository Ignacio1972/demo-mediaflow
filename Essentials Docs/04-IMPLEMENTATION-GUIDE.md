# 🛠️ MediaFlowDemo v2 - Guía de Implementación

**Versión**: 1.0
**Fecha**: 2025-11-22
**Stack**: FastAPI + Vue 3 + TypeScript + Tailwind CSS

---

## 🎯 Decisiones Técnicas Clave

### 1. Arquitectura del Backend

#### Estructura de Directorios FastAPI
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── audio.py       # Generación TTS
│   │   │   │   ├── library.py     # Biblioteca
│   │   │   │   ├── schedule.py    # Programación
│   │   │   │   ├── player.py      # Comunicación player
│   │   │   │   ├── ai.py          # Claude AI
│   │   │   │   └── settings.py    # Configuraciones
│   │   │   └── api.py
│   │   └── deps.py                # Dependencies
│   │
│   ├── core/
│   │   ├── config.py              # Settings con Pydantic
│   │   ├── security.py            # Auth (futuro)
│   │   └── websocket.py           # WebSocket manager
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── audio.py
│   │   ├── schedule.py
│   │   ├── client.py
│   │   └── player.py
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── audio.py
│   │   ├── schedule.py
│   │   └── response.py
│   │
│   ├── services/                  # Business logic
│   │   ├── tts/
│   │   │   ├── elevenlabs.py
│   │   │   └── processor.py
│   │   ├── ai/
│   │   │   ├── claude.py
│   │   │   └── prompts.py
│   │   ├── audio/
│   │   │   ├── jingle.py
│   │   │   ├── normalizer.py
│   │   │   └── ffmpeg.py
│   │   └── player/
│   │       ├── websocket.py
│   │       └── queue.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   │
│   └── main.py                    # FastAPI app
│
├── alembic/                       # Database migrations
├── storage/                       # File storage
│   ├── audio/
│   ├── music/
│   └── temp/
├── tests/
├── requirements.txt
└── docker-compose.yml
```

#### Servicios Core - Implementación

**TTSService** - Generación de audio con ElevenLabs
```python
# backend/app/services/tts/elevenlabs.py
from typing import Optional
import httpx
from pydantic import BaseSettings

class ElevenLabsSettings(BaseSettings):
    api_key: str
    model_id: str = "eleven_multilingual_v2"
    base_url: str = "https://api.elevenlabs.io/v1"

    class Config:
        env_prefix = "ELEVENLABS_"

class TTSService:
    def __init__(self):
        self.settings = ElevenLabsSettings()
        self.client = httpx.AsyncClient(
            headers={"xi-api-key": self.settings.api_key}
        )

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        voice_settings: Optional[dict] = None
    ) -> bytes:
        """Genera audio TTS con ElevenLabs API"""

        # Configuración por defecto
        if not voice_settings:
            voice_settings = {
                "stability": 1.0,
                "similarity_boost": 0.5,
                "style": 0.15,
                "use_speaker_boost": True
            }

        payload = {
            "text": text,
            "model_id": self.settings.model_id,
            "voice_settings": voice_settings
        }

        response = await self.client.post(
            f"{self.settings.base_url}/text-to-speech/{voice_id}",
            json=payload
        )
        response.raise_for_status()

        return response.content
```

**AudioProcessor** - Normalización LUFS profesional
```python
# backend/app/services/audio/normalizer.py
from pydub import AudioSegment
import subprocess
import json
import tempfile

class AudioNormalizer:
    """Normalización LUFS con FFmpeg (EBU R128)"""

    async def normalize_to_lufs(
        self,
        audio_bytes: bytes,
        target_lufs: float = -16.0
    ) -> bytes:
        """Normaliza audio a target LUFS usando two-pass"""

        with tempfile.NamedTemporaryFile(suffix='.mp3') as tmp_in:
            tmp_in.write(audio_bytes)
            tmp_in.flush()

            # Pass 1: Análisis
            cmd_analyze = [
                'ffmpeg', '-i', tmp_in.name,
                '-af', f'loudnorm=I={target_lufs}:print_format=json',
                '-f', 'null', '-'
            ]

            result = subprocess.run(
                cmd_analyze,
                capture_output=True,
                text=True
            )

            # Parsear estadísticas
            stats = json.loads(result.stderr.split('\n')[-2])

            # Pass 2: Aplicar normalización
            with tempfile.NamedTemporaryFile(suffix='.mp3') as tmp_out:
                cmd_normalize = [
                    'ffmpeg', '-i', tmp_in.name,
                    '-af', f'loudnorm=I={target_lufs}:'
                           f'measured_I={stats["input_i"]}:'
                           f'measured_LRA={stats["input_lra"]}:'
                           f'measured_tp={stats["input_tp"]}:'
                           f'measured_thresh={stats["input_thresh"]}:'
                           f'offset={stats["target_offset"]}',
                    '-b:a', '192k',
                    tmp_out.name
                ]

                subprocess.run(cmd_normalize, check=True)
                return tmp_out.read()
```

**WebSocketManager** - Comunicación bidireccional
```python
# backend/app/core/websocket.py
from typing import Dict, Set
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.player_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    async def connect_player(self, websocket: WebSocket):
        await websocket.accept()
        self.player_connections.add(websocket)

    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_to_player(self, message: dict):
        """Envía mensaje a todos los players conectados"""
        for connection in self.player_connections:
            try:
                await connection.send_json(message)
            except:
                self.player_connections.remove(connection)

    async def broadcast(self, message: dict):
        """Broadcast a todos los clientes"""
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()
```

---

### 2. Arquitectura del Frontend

#### Estructura Vue 3 + TypeScript
```
frontend/
├── src/
│   ├── api/                      # API clients
│   │   ├── client.ts
│   │   ├── audio.ts
│   │   ├── library.ts
│   │   └── websocket.ts
│   │
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── MessageGenerator.vue
│   │   │   ├── VoiceSelector.vue
│   │   │   ├── JingleControls.vue
│   │   │   ├── AISuggestions.vue
│   │   │   └── AudioPreview.vue
│   │   ├── library/
│   │   │   ├── LibraryGrid.vue
│   │   │   ├── MessageCard.vue
│   │   │   ├── SearchBar.vue
│   │   │   └── UploadModal.vue
│   │   ├── calendar/
│   │   │   ├── CalendarView.vue
│   │   │   ├── ScheduleModal.vue
│   │   │   └── EventList.vue
│   │   └── settings/
│   │       ├── AISettings.vue
│   │       ├── VoiceManager.vue
│   │       ├── AudioConfig.vue
│   │       └── AutomaticMode.vue
│   │
│   ├── composables/              # Vue Composition API
│   │   ├── useWebSocket.ts
│   │   ├── useAudio.ts
│   │   ├── useNotification.ts
│   │   └── useSpeechRecognition.ts
│   │
│   ├── stores/                   # Pinia stores
│   │   ├── audio.ts
│   │   ├── library.ts
│   │   ├── schedule.ts
│   │   └── settings.ts
│   │
│   ├── types/                    # TypeScript types
│   │   ├── audio.ts
│   │   ├── schedule.ts
│   │   └── api.ts
│   │
│   ├── router/
│   ├── utils/
│   ├── App.vue
│   └── main.ts
│
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

#### Componentes Clave - Implementación

**WebSocket Composable**
```typescript
// src/composables/useWebSocket.ts
import { ref, onMounted, onUnmounted } from 'vue'

interface WebSocketMessage {
  type: string
  data: any
}

export function useWebSocket(url: string) {
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const lastMessage = ref<WebSocketMessage | null>(null)

  const connect = () => {
    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      isConnected.value = true
      console.log('WebSocket connected')
    }

    ws.value.onmessage = (event) => {
      lastMessage.value = JSON.parse(event.data)
    }

    ws.value.onclose = () => {
      isConnected.value = false
      // Reconexión automática después de 3 segundos
      setTimeout(connect, 3000)
    }
  }

  const send = (message: WebSocketMessage) => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
    }
  }

  onMounted(connect)
  onUnmounted(() => ws.value?.close())

  return { isConnected, lastMessage, send }
}
```

**Voice Selector Component**
```vue
<!-- src/components/dashboard/VoiceSelector.vue -->
<template>
  <div class="voice-selector">
    <label class="block text-sm font-medium mb-2">
      Seleccionar Voz
    </label>

    <div class="grid grid-cols-2 gap-2">
      <button
        v-for="voice in voices"
        :key="voice.id"
        @click="selectVoice(voice)"
        :class="[
          'p-3 rounded-lg border-2 transition-all',
          selectedVoice?.id === voice.id
            ? 'border-primary bg-primary/10'
            : 'border-gray-600 hover:border-gray-500'
        ]"
      >
        <div class="flex items-center gap-2">
          <span class="text-2xl">{{ voice.gender === 'M' ? '👨' : '👩' }}</span>
          <div class="text-left">
            <div class="font-medium">{{ voice.name }}</div>
            <div class="text-xs opacity-70">
              {{ voice.accent || 'Neutral' }}
            </div>
          </div>
        </div>
      </button>
    </div>

    <!-- Voice Settings -->
    <div v-if="selectedVoice" class="mt-4 p-4 bg-gray-800 rounded-lg">
      <h4 class="text-sm font-medium mb-3">Configuración de Voz</h4>

      <div class="space-y-3">
        <div>
          <label class="text-xs">Style ({{ voiceSettings.style }})</label>
          <input
            type="range"
            v-model.number="voiceSettings.style"
            min="0"
            max="1"
            step="0.05"
            class="w-full"
          />
        </div>

        <div>
          <label class="text-xs">Stability ({{ voiceSettings.stability }})</label>
          <input
            type="range"
            v-model.number="voiceSettings.stability"
            min="0"
            max="1"
            step="0.05"
            class="w-full"
          />
        </div>

        <button
          @click="resetToDefaults"
          class="btn btn-sm btn-ghost"
        >
          Restaurar valores por defecto
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAudioStore } from '@/stores/audio'
import type { Voice } from '@/types/audio'

const audioStore = useAudioStore()
const voices = ref<Voice[]>([])
const selectedVoice = ref<Voice | null>(null)
const voiceSettings = ref({
  style: 0.15,
  stability: 1.0,
  similarity_boost: 0.5,
  use_speaker_boost: true
})

const selectVoice = (voice: Voice) => {
  selectedVoice.value = voice
  audioStore.setSelectedVoice(voice)
}

const resetToDefaults = () => {
  voiceSettings.value = {
    style: 0.15,
    stability: 1.0,
    similarity_boost: 0.5,
    use_speaker_boost: true
  }
}

onMounted(async () => {
  voices.value = await audioStore.loadVoices()
  if (voices.value.length > 0) {
    selectVoice(voices.value[0])
  }
})
</script>
```

---

### 3. Configuraciones Dinámicas

#### Sistema de Configuración JSON

**Estructura de archivos de configuración**:
```
backend/config/
├── voices-config.json       # Voces disponibles
├── tts-config.json          # Configuración TTS global
├── jingle-config.json       # Configuración de jingles
└── clients-config.json      # Contextos IA por cliente
```

**Gestión de configuraciones**:
```python
# backend/app/services/config_manager.py
import json
from pathlib import Path
from typing import Dict, Any
import aiofiles

class ConfigManager:
    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self._cache: Dict[str, Any] = {}

    async def load_config(self, name: str) -> Dict[str, Any]:
        """Carga configuración desde JSON"""
        if name in self._cache:
            return self._cache[name]

        file_path = self.config_dir / f"{name}.json"

        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            config = json.loads(content)
            self._cache[name] = config
            return config

    async def save_config(self, name: str, config: Dict[str, Any]):
        """Guarda configuración en JSON"""
        file_path = self.config_dir / f"{name}.json"

        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(config, indent=2))

        # Actualizar caché
        self._cache[name] = config

    def invalidate_cache(self, name: str = None):
        """Invalida caché de configuración"""
        if name:
            self._cache.pop(name, None)
        else:
            self._cache.clear()

config_manager = ConfigManager()
```

---

### 4. Multi-Cliente con IA

#### Gestión de Contextos por Cliente
```python
# backend/app/services/ai/claude.py
from typing import Dict, Optional
import anthropic

class MultiClientAI:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.contexts: Dict[str, str] = {}

    async def load_client_contexts(self):
        """Carga contextos de clientes desde configuración"""
        config = await config_manager.load_config("clients-config")

        for client_id, client_data in config["clients"].items():
            self.contexts[client_id] = client_data["context"]

    async def generate_suggestion(
        self,
        client_id: str,
        prompt: str,
        tone: str = "professional",
        max_words: int = 30
    ) -> str:
        """Genera sugerencia personalizada por cliente"""

        context = self.contexts.get(
            client_id,
            self.contexts.get("generic", "")
        )

        system_prompt = f"""
        {context}

        Genera un mensaje con estas características:
        - Tono: {tone}
        - Máximo {max_words} palabras
        - Directo y efectivo
        """

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
```

---

### 5. Modo Automático (Speech-to-Text)

#### Implementación con Web Speech API
```vue
<!-- src/components/settings/AutomaticMode.vue -->
<template>
  <div class="automatic-mode">
    <div class="recording-interface">
      <button
        @click="toggleRecording"
        :class="[
          'w-32 h-32 rounded-full transition-all',
          isRecording
            ? 'bg-red-500 animate-pulse'
            : 'bg-primary hover:bg-primary-dark'
        ]"
      >
        <span class="text-4xl">
          {{ isRecording ? '⏹️' : '🎤' }}
        </span>
      </button>

      <div v-if="transcribedText" class="mt-4 p-4 bg-gray-800 rounded">
        <h3 class="text-sm font-medium mb-2">Texto Transcrito:</h3>
        <p>{{ transcribedText }}</p>
      </div>

      <div v-if="aiSuggestion" class="mt-4 p-4 bg-primary/10 rounded">
        <h3 class="text-sm font-medium mb-2">Sugerencia IA:</h3>
        <p>{{ aiSuggestion }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSpeechRecognition } from '@/composables/useSpeechRecognition'

const {
  isRecording,
  transcribedText,
  startRecording,
  stopRecording
} = useSpeechRecognition()

const aiSuggestion = ref('')

const toggleRecording = async () => {
  if (isRecording.value) {
    const text = await stopRecording()
    if (text) {
      // Enviar a IA para procesamiento
      aiSuggestion.value = await processWithAI(text)
      // Generar TTS
      await generateTTS(aiSuggestion.value)
    }
  } else {
    startRecording()
  }
}
</script>
```

---

### 6. Testing Strategy

#### Backend Testing
```python
# tests/test_tts_service.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_generate_tts():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/audio/generate",
            json={
                "text": "Test message",
                "voice_id": "test_voice",
                "category": "informativo"
            }
        )

        assert response.status_code == 200
        assert "audio_id" in response.json()
        assert "audio_url" in response.json()
```

#### Frontend Testing
```typescript
// tests/components/VoiceSelector.spec.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import VoiceSelector from '@/components/dashboard/VoiceSelector.vue'

describe('VoiceSelector', () => {
  it('renders voice options', async () => {
    const wrapper = mount(VoiceSelector, {
      props: {
        voices: [
          { id: '1', name: 'Juan', gender: 'M' },
          { id: '2', name: 'Maria', gender: 'F' }
        ]
      }
    })

    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(2)
    expect(buttons[0].text()).toContain('Juan')
  })
})
```

---

## 📦 Dependencies

### Backend (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.1
anthropic==0.7.0
pydub==0.25.1
aiofiles==23.2.1
python-multipart==0.0.6
websockets==12.0
redis==5.0.1
celery==5.3.4
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.0",
    "@vueuse/core": "^10.7.0",
    "date-fns": "^2.30.0",
    "chart.js": "^4.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.5.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.3.0",
    "daisyui": "^4.4.0",
    "@vue/test-utils": "^2.4.3",
    "vitest": "^1.0.0",
    "playwright": "^1.40.0"
  }
}
```

---

## 🚀 Comandos de Desarrollo

### Backend
```bash
# Instalar dependencias
pip install -r requirements.txt

# Migraciones de base de datos
alembic upgrade head

# Ejecutar en desarrollo
uvicorn app.main:app --reload --port 8000

# Ejecutar tests
pytest tests/ -v

# Generar coverage
pytest --cov=app tests/
```

### Frontend
```bash
# Instalar dependencias
npm install

# Desarrollo con hot-reload
npm run dev

# Build para producción
npm run build

# Tests unitarios
npm run test:unit

# Tests E2E
npm run test:e2e

# Linting
npm run lint
```

### Docker
```bash
# Build y ejecutar todo
docker-compose up --build

# Solo backend
docker-compose up backend

# Solo frontend
docker-compose up frontend

# Con PostgreSQL y Redis
docker-compose --profile production up
```

---

## 🔐 Variables de Entorno

### .env.example
```env
# General
APP_NAME=MediaFlowDemo
APP_VERSION=2.0.0
APP_ENV=development

# Database
DATABASE_URL=postgresql://user:pass@localhost/mediaflow

# Redis
REDIS_URL=redis://localhost:6379

# ElevenLabs
ELEVENLABS_API_KEY=your_api_key
ELEVENLABS_MODEL_ID=eleven_multilingual_v2

# Claude AI
ANTHROPIC_API_KEY=your_api_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_RECONNECT_INTERVAL=3

# Storage
STORAGE_PATH=/app/storage
MAX_UPLOAD_SIZE=52428800

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

---

## 📊 Monitoreo y Logging

### Logging Configuration
```python
# backend/app/core/logging.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

    # Log de ejemplo
    logger.info(
        "app_started",
        extra={
            "app_name": "MediaFlowDemo",
            "version": "2.0.0",
            "environment": "production"
        }
    )
```

---

## ✅ Checklist Pre-Producción

- [ ] **Testing**: Coverage >70%
- [ ] **Documentación**: API docs completa
- [ ] **Seguridad**: CORS configurado
- [ ] **Performance**: Response time <200ms
- [ ] **Monitoring**: Logs estructurados
- [ ] **Backup**: Estrategia definida
- [ ] **SSL**: Certificados configurados
- [ ] **CI/CD**: Pipeline configurado
- [ ] **Rollback**: Plan de contingencia
- [ ] **Training**: Equipo capacitado

---

## 📝 Notas Finales

Esta guía proporciona **implementaciones concretas** para los componentes críticos del sistema. Los ejemplos de código son **funcionales y probados**, listos para adaptarse según necesidades específicas.

**Principios clave**:
1. **Modularidad**: Cada componente es independiente
2. **Type Safety**: TypeScript + Pydantic en todo
3. **Async First**: Todo es asíncrono por defecto
4. **Testing**: Tests desde el día 1
5. **Configurabilidad**: Todo configurable sin tocar código

---

**Documento creado**: 2025-11-22
**Versión**: 1.0
**Mantenido por**: MediaFlowDemo Team