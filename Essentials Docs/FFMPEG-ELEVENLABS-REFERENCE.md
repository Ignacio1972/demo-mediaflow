# 🎙️ FFMPEG & ElevenLabs Reference - MediaFlowDemo v2.1

**Fecha Creación**: 2025-11-22
**Propósito**: Referencia técnica específica para audio processing y TTS en MediaFlowDemo

---

## 📚 Tabla de Contenidos

1. [ElevenLabs API Reference](#elevenlabs-api-reference)
2. [FFMPEG Audio Processing](#ffmpeg-audio-processing)
3. [Implementación en MediaFlowDemo](#implementación-en-mediaflowdemo)
4. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 🎤 ElevenLabs API Reference

### 1. Text-to-Speech Endpoint

**Endpoint**: `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`

#### Request Parameters

| Parámetro | Ubicación | Tipo | Descripción |
|-----------|-----------|------|-------------|
| `voice_id` | Path | string | ID de la voz (ej: "G4IAP30yc6c1gK0csDfu") |
| `enable_logging` | Query | boolean | False = zero retention mode (solo Enterprise) |
| `optimize_streaming_latency` | Query | int (0-4) | 0=default, 4=max latency optimization |
| `output_format` | Query | string | Formato de salida (ver tabla abajo) |
| `xi-api-key` | Header | string | API key de ElevenLabs |

#### Request Body (JSON)

```json
{
  "text": "Texto a convertir en audio",
  "model_id": "eleven_multilingual_v2",
  "language_code": "es",  // opcional
  "voice_settings": {
    "stability": 100.0,           // 0-100
    "similarity_boost": 40.0,     // 0-100
    "style": 15.0,                // 0-100
    "speed": 1.0,                 // multiplicador velocidad
    "use_speaker_boost": true
  },
  "seed": 12345,                  // opcional, para reproducibilidad
  "previous_text": "...",         // opcional, para contexto
  "next_text": "..."              // opcional, para mejor pronunciación
}
```

#### Output Formats (MediaFlowDemo usa `mp3_44100_128`)

| Formato | Sample Rate | Bitrate | Tier Requerido |
|---------|-------------|---------|----------------|
| `mp3_44100_128` | 44.1kHz | 128kbps | ⭐ Recomendado (Standard) |
| `mp3_44100_192` | 44.1kHz | 192kbps | Creator+ |
| `pcm_44100` | 44.1kHz | N/A | Pro+ |
| `opus_48000_128` | 48kHz | 128kbps | Standard |

#### Voice Settings Explained

**MediaFlowDemo Context**: Cada voz tiene settings individuales almacenados en `VoiceSettings` model.

```python
# Configuración típica para voz formal (Juan Carlos)
{
  "stability": 100.0,         # Máxima consistencia (100 = robot, 0 = variable)
  "similarity_boost": 40.0,   # Claridad + similitud (balance 40-50)
  "style": 15.0,              # Formalidad (0 = neutro, 100 = expresivo)
  "speed": 1.0,               # Velocidad normal
  "use_speaker_boost": true   # Mejora claridad
}

# Configuración para voz casual
{
  "stability": 75.0,          # Más variación
  "similarity_boost": 50.0,   # Más claridad
  "style": 50.0,              # Más expresividad
  "speed": 1.1,               # Ligeramente más rápido
  "use_speaker_boost": true
}
```

**Guía de Parámetros**:

- **Stability** (Estabilidad):
  - `100` = Voz muy consistente, ideal para anuncios formales
  - `75` = Balance entre consistencia y naturalidad
  - `50` = Más expresiva, puede variar entre generaciones
  - `0` = Muy variable, no recomendado

- **Similarity Boost** (Claridad + Similitud):
  - `40-50` = Balance óptimo para español
  - `>75` = Puede generar artefactos
  - `<25` = Voz puede sonar diferente al modelo

- **Style** (Expresividad):
  - `0-20` = Formal, noticias, anuncios serios
  - `30-50` = Casual, conversacional
  - `60-100` = Muy expresivo, emocional

- **Speed**:
  - `0.5` = Muy lento (50%)
  - `1.0` = Velocidad normal
  - `1.5` = Muy rápido (150%)

### 2. Voice Settings Endpoints

#### Get Voice Settings

```bash
GET https://api.elevenlabs.io/v1/voices/{voice_id}/settings
```

**Response**:
```json
{
  "stability": 100.0,
  "similarity_boost": 40.0,
  "style": 15.0,
  "speed": 1.0,
  "use_speaker_boost": true
}
```

#### Update Voice Settings

```bash
POST https://api.elevenlabs.io/v1/voices/{voice_id}/settings/edit
Content-Type: application/json

{
  "stability": 100.0,
  "similarity_boost": 40.0,
  "style": 15.0,
  "speed": 1.0,
  "use_speaker_boost": true
}
```

**Response**:
```json
{
  "status": "ok"
}
```

### 3. Ejemplo Python (MediaFlowDemo)

```python
# backend/app/services/tts/elevenlabs.py

import aiohttp
from typing import Optional

class ElevenLabsService:
    BASE_URL = "https://api.elevenlabs.io/v1"

    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        voice_settings: dict,
        model_id: str = "eleven_multilingual_v2"
    ) -> bytes:
        """
        Genera audio usando ElevenLabs API

        Args:
            text: Texto a convertir
            voice_id: ID de la voz (ej: "G4IAP30yc6c1gK0csDfu")
            voice_settings: Dict con stability, similarity_boost, style, speed
            model_id: Modelo a usar (default: eleven_multilingual_v2)

        Returns:
            bytes: Audio MP3
        """
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}"

        params = {
            "output_format": "mp3_44100_128",
            "optimize_streaming_latency": 0
        }

        payload = {
            "text": text,
            "model_id": model_id,
            "language_code": "es",
            "voice_settings": voice_settings
        }

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                params=params,
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs API error: {error_text}")

                return await response.read()
```

---

## 🎛️ FFMPEG Audio Processing

### 1. Normalización LUFS (EBU R128)

**Context MediaFlowDemo**: Todos los audios deben normalizarse a **-16 LUFS** para broadcast consistency.

#### 1.1 Filtro `loudnorm`

**Parámetros Clave**:

| Parámetro | Rango | Default | MediaFlowDemo | Descripción |
|-----------|-------|---------|---------------|-------------|
| `I` (integrated loudness) | -70.0 to -5.0 | -24.0 | **-16.0** | Target LUFS |
| `LRA` (loudness range) | 1.0 to 50.0 | 7.0 | **7.0** | Dynamic range |
| `TP` (true peak) | -9.0 to 0.0 | -2.0 | **-2.0** | Peak limiter |
| `linear` | true/false | true | **false** | Linear vs dynamic |

#### 1.2 Two-Pass Normalization (Recomendado)

**Primera Pasada**: Medir el audio

```bash
ffmpeg -i input.mp3 -af loudnorm=I=-16:LRA=7:TP=-2:print_format=json -f null -
```

**Output JSON**:
```json
{
  "input_i": "-18.5",
  "input_tp": "-0.8",
  "input_lra": "5.2",
  "input_thresh": "-28.9"
}
```

**Segunda Pasada**: Normalizar con mediciones

```bash
ffmpeg -i input.mp3 -af loudnorm=I=-16:LRA=7:TP=-2:measured_I=-18.5:measured_LRA=5.2:measured_TP=-0.8:measured_thresh=-28.9:linear=false output.mp3
```

#### 1.3 Single-Pass (MediaFlowDemo usa esto)

```bash
ffmpeg -i input.mp3 -af loudnorm=I=-16:LRA=7:TP=-2 output.mp3
```

**Ventajas**: Más rápido, ideal para generación en tiempo real
**Desventajas**: Menos preciso que two-pass

### 2. Audio Mixing (Jingles + Voz)

**Context MediaFlowDemo**: Sistema de jingles con ducking (música baja cuando habla la voz).

#### 2.1 Filtro `amix`

**Parámetros**:

| Parámetro | Descripción | MediaFlowDemo |
|-----------|-------------|---------------|
| `inputs` | Número de inputs | `2` (jingle + voz) |
| `duration` | Duración output | `longest` |
| `dropout_transition` | Transición al terminar input | `2.0` segundos |
| `weights` | Peso de cada input | `"0.25 1.0"` (música 25%, voz 100%) |
| `normalize` | Normalizar suma | `false` |

#### 2.2 Mixing con Weights (Sin Ducking)

**Simple Mix**: Voz + Música de fondo

```bash
ffmpeg -i voice.mp3 -i jingle.mp3 \
  -filter_complex "amix=inputs=2:duration=longest:weights='1.0 0.25':normalize=0" \
  output.mp3
```

**Explicación**:
- Voz al 100% (weight 1.0)
- Música al 25% (weight 0.25)
- Sin normalización (evita clipping manual)

#### 2.3 Advanced Ducking (MediaFlowDemo v2)

**Ducking Manual con `volume` y `compand`**:

```bash
ffmpeg -i voice.mp3 -i jingle.mp3 -filter_complex \
  "[1:a]volume=0.3[music]; \
   [0:a]asplit=2[voice_out][voice_detect]; \
   [voice_detect]aformat=sample_rates=48000,asetnsamples=n=48000,volume=1.0,aformat=sample_fmts=dbl[voice_norm]; \
   [music][voice_norm]sidechaincompress=threshold=0.1:ratio=4:attack=200:release=1000[ducked]; \
   [voice_out][ducked]amix=inputs=2:duration=first:normalize=0" \
  output.mp3
```

**Explicación**:
1. `[1:a]volume=0.3[music]` = Música al 30%
2. `asplit=2` = Duplicar voz (output + detector)
3. `sidechaincompress` = Ducking cuando detecta voz
   - `threshold=0.1` = Umbral de detección
   - `ratio=4` = Ratio de compresión (música baja 4:1)
   - `attack=200` = 200ms para bajar música
   - `release=1000` = 1000ms para subir música

#### 2.4 Simple Ducking (MediaFlowDemo v2.1 - Recomendado)

**Usando Volume Adjustment en DB**:

```python
# backend/app/services/audio/processor.py

async def apply_jingle(
    voice_audio: bytes,
    jingle_audio: bytes,
    music_volume_db: float = -12.0,  # Música -12dB más baja
    voice_volume_db: float = 0.0      # Voz sin cambio
) -> bytes:
    """
    Mix voz + jingle con volume adjustment

    MediaFlowDemo usa:
    - Música: -12dB (aprox 25% de volumen)
    - Voz: 0dB (100%)
    """

    # Crear archivos temporales
    with tempfile.NamedTemporaryFile(suffix=".mp3") as voice_file, \
         tempfile.NamedTemporaryFile(suffix=".mp3") as jingle_file, \
         tempfile.NamedTemporaryFile(suffix=".mp3") as output_file:

        voice_file.write(voice_audio)
        jingle_file.write(jingle_audio)
        voice_file.flush()
        jingle_file.flush()

        # FFMPEG command
        cmd = [
            "ffmpeg", "-y",
            "-i", voice_file.name,
            "-i", jingle_file.name,
            "-filter_complex",
            f"[0:a]volume={voice_volume_db}dB[voice]; "
            f"[1:a]volume={music_volume_db}dB[music]; "
            f"[voice][music]amix=inputs=2:duration=longest:normalize=0",
            "-ar", "44100",
            "-ac", "2",
            output_file.name
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await process.communicate()

        output_file.seek(0)
        return output_file.read()
```

### 3. Volume Control con `volume` Filter

**Sintaxis**:

```bash
# Volumen en ratio (1.0 = 100%)
volume=0.25          # 25% volumen

# Volumen en dB
volume=-12dB         # -12 decibeles (aprox 25%)
volume=+3dB          # +3 decibeles (aprox 141%)

# Volumen dinámico
volume='if(lt(t,5),0,1)'  # Silencio primeros 5 segundos
```

**Tabla de Conversión dB ↔ Ratio**:

| dB | Ratio | % |
|----|-------|---|
| -20 | 0.10 | 10% |
| -12 | 0.25 | 25% |
| -6 | 0.50 | 50% |
| -3 | 0.71 | 71% |
| 0 | 1.00 | 100% |
| +3 | 1.41 | 141% |
| +6 | 2.00 | 200% |

### 4. Dynamic Audio Normalization

**Filtro `dynaudnorm`**: Alternativa a `loudnorm` con mejor resultado en tiempo real.

```bash
ffmpeg -i input.mp3 \
  -af dynaudnorm=p=0.95:m=10.0:r=0.0:f=500:g=31 \
  output.mp3
```

**Parámetros**:
- `p=0.95` = Peak target (95% = -0.5dB headroom)
- `m=10.0` = Max gain (10x = 20dB)
- `r=0.0` = Target RMS (0 = disabled, usa peak)
- `f=500` = Frame length (500ms)
- `g=31` = Gaussian window size (31 frames)

**MediaFlowDemo**: Usar `loudnorm` para broadcast, `dynaudnorm` para preview rápido.

---

## 🔧 Implementación en MediaFlowDemo

### 1. Arquitectura de Audio Processing

```
┌─────────────────────────────────────────────────────────────┐
│  VoiceManager (backend/app/services/tts/voice_manager.py)  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  1. ElevenLabsService.generate() │
         │     - Aplica voice_settings      │
         │     - Retorna MP3 raw            │
         └──────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  2. AudioProcessor.normalize()   │
         │     - LUFS -16 (loudnorm)        │
         │     - True peak -2dB             │
         └──────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  3. VoiceSettings.volume_adj     │
         │     - Ajuste individual por voz  │
         │     - FFMPEG volume filter       │
         └──────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  4. JingleProcessor.apply()      │
         │     - Mix con jingle (opcional)  │
         │     - Ducking automático         │
         └──────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  5. Storage.save()               │
         │     - Guardar en storage/audio/  │
         │     - Retornar path + metadata   │
         └──────────────────────────────────┘
```

### 2. VoiceSettings Model (Database)

```python
# backend/app/models/voice_settings.py

class VoiceSettings(Base):
    __tablename__ = "voice_settings"

    id = Column(String, primary_key=True)  # "juan_carlos"
    name = Column(String, nullable=False)
    elevenlabs_id = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    # ElevenLabs Voice Settings
    style = Column(Float, default=15.0)              # 0-100
    stability = Column(Float, default=100.0)         # 0-100
    similarity_boost = Column(Float, default=40.0)   # 0-100
    speed = Column(Float, default=1.0)               # multiplicador
    use_speaker_boost = Column(Boolean, default=True)

    # MediaFlowDemo Custom Settings
    volume_adjustment = Column(Float, default=0.0)   # dB (-20 to +20)

    # Jingle Settings (JSON)
    jingle_settings = Column(JSON, default={
        "music_volume_db": -12.0,      # Música -12dB
        "voice_volume_db": 0.0,        # Voz sin cambio
        "duck_threshold": 0.1,         # Umbral ducking
        "duck_ratio": 4.0,             # Ratio compresión
        "duck_attack_ms": 200,         # Attack 200ms
        "duck_release_ms": 1000        # Release 1000ms
    })
```

### 3. Audio Processing Service

```python
# backend/app/services/audio/processor.py

import asyncio
import tempfile
from pathlib import Path

class AudioProcessor:
    """
    Audio processing service para MediaFlowDemo
    Normalización LUFS, volume adjustment, mixing
    """

    TARGET_LUFS = -16.0
    TARGET_LRA = 7.0
    TARGET_TP = -2.0

    async def normalize_lufs(
        self,
        audio_data: bytes,
        target_lufs: float = TARGET_LUFS
    ) -> bytes:
        """
        Normaliza audio a target LUFS usando loudnorm (single-pass)

        Args:
            audio_data: Audio MP3 en bytes
            target_lufs: Target LUFS (default -16.0 para broadcast)

        Returns:
            bytes: Audio normalizado
        """
        with tempfile.NamedTemporaryFile(suffix=".mp3") as input_file, \
             tempfile.NamedTemporaryFile(suffix=".mp3") as output_file:

            input_file.write(audio_data)
            input_file.flush()

            cmd = [
                "ffmpeg", "-y",
                "-i", input_file.name,
                "-af", f"loudnorm=I={target_lufs}:LRA={self.TARGET_LRA}:TP={self.TARGET_TP}",
                "-ar", "44100",
                "-ac", "2",
                "-b:a", "128k",
                output_file.name
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"FFMPEG error: {stderr.decode()}")

            output_file.seek(0)
            return output_file.read()

    async def apply_volume_adjustment(
        self,
        audio_data: bytes,
        volume_db: float
    ) -> bytes:
        """
        Aplica ajuste de volumen en dB

        Args:
            audio_data: Audio MP3 en bytes
            volume_db: Ajuste en dB (-20 to +20)

        Returns:
            bytes: Audio con volumen ajustado
        """
        if volume_db == 0.0:
            return audio_data  # No adjustment needed

        with tempfile.NamedTemporaryFile(suffix=".mp3") as input_file, \
             tempfile.NamedTemporaryFile(suffix=".mp3") as output_file:

            input_file.write(audio_data)
            input_file.flush()

            cmd = [
                "ffmpeg", "-y",
                "-i", input_file.name,
                "-af", f"volume={volume_db}dB",
                "-ar", "44100",
                "-ac", "2",
                "-b:a", "128k",
                output_file.name
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await process.communicate()

            output_file.seek(0)
            return output_file.read()

    async def mix_with_jingle(
        self,
        voice_audio: bytes,
        jingle_audio: bytes,
        jingle_settings: dict
    ) -> bytes:
        """
        Mix voz + jingle con settings personalizados

        Args:
            voice_audio: Audio de voz
            jingle_audio: Audio de jingle
            jingle_settings: Dict con music_volume_db, voice_volume_db

        Returns:
            bytes: Audio mezclado
        """
        music_vol = jingle_settings.get("music_volume_db", -12.0)
        voice_vol = jingle_settings.get("voice_volume_db", 0.0)

        with tempfile.NamedTemporaryFile(suffix=".mp3") as voice_file, \
             tempfile.NamedTemporaryFile(suffix=".mp3") as jingle_file, \
             tempfile.NamedTemporaryFile(suffix=".mp3") as output_file:

            voice_file.write(voice_audio)
            jingle_file.write(jingle_audio)
            voice_file.flush()
            jingle_file.flush()

            filter_complex = (
                f"[0:a]volume={voice_vol}dB[voice]; "
                f"[1:a]volume={music_vol}dB[music]; "
                f"[voice][music]amix=inputs=2:duration=longest:normalize=0"
            )

            cmd = [
                "ffmpeg", "-y",
                "-i", voice_file.name,
                "-i", jingle_file.name,
                "-filter_complex", filter_complex,
                "-ar", "44100",
                "-ac", "2",
                "-b:a", "128k",
                output_file.name
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await process.communicate()

            output_file.seek(0)
            return output_file.read()
```

### 4. Complete Workflow (VoiceManager)

```python
# backend/app/services/tts/voice_manager.py

class VoiceManager:
    """
    Gestiona generación TTS + processing completo
    """

    def __init__(
        self,
        elevenlabs_service: ElevenLabsService,
        audio_processor: AudioProcessor,
        db: Session
    ):
        self.elevenlabs = elevenlabs_service
        self.processor = audio_processor
        self.db = db

    async def generate_with_voice(
        self,
        text: str,
        voice_id: str,
        apply_jingle: bool = False,
        jingle_id: Optional[str] = None
    ) -> tuple[bytes, dict]:
        """
        Genera audio completo con voice settings automáticos

        Pipeline:
        1. Leer voice settings de DB
        2. Generar TTS con ElevenLabs
        3. Normalizar LUFS -16
        4. Aplicar volume adjustment
        5. Aplicar jingle (opcional)
        6. Retornar audio + metadata

        Args:
            text: Texto a convertir
            voice_id: ID de la voz (ej: "juan_carlos")
            apply_jingle: Si aplicar jingle
            jingle_id: ID del jingle (opcional)

        Returns:
            tuple: (audio_bytes, metadata_dict)
        """
        # 1. Leer voice settings
        voice = self.db.query(VoiceSettings).filter_by(id=voice_id).first()
        if not voice:
            raise ValueError(f"Voice {voice_id} not found")

        # 2. Generar TTS
        tts_audio = await self.elevenlabs.generate_audio(
            text=text,
            voice_id=voice.elevenlabs_id,
            voice_settings={
                "stability": voice.stability,
                "similarity_boost": voice.similarity_boost,
                "style": voice.style,
                "speed": voice.speed,
                "use_speaker_boost": voice.use_speaker_boost
            }
        )

        # 3. Normalizar LUFS
        normalized_audio = await self.processor.normalize_lufs(tts_audio)

        # 4. Aplicar volume adjustment
        adjusted_audio = await self.processor.apply_volume_adjustment(
            normalized_audio,
            voice.volume_adjustment
        )

        # 5. Aplicar jingle (opcional)
        final_audio = adjusted_audio
        if apply_jingle and jingle_id:
            jingle_path = Path(f"storage/jingles/{jingle_id}.mp3")
            if jingle_path.exists():
                jingle_audio = jingle_path.read_bytes()
                final_audio = await self.processor.mix_with_jingle(
                    adjusted_audio,
                    jingle_audio,
                    voice.jingle_settings
                )

        # 6. Metadata
        metadata = {
            "voice_id": voice_id,
            "voice_name": voice.name,
            "text_length": len(text),
            "has_jingle": apply_jingle,
            "settings_applied": {
                "stability": voice.stability,
                "similarity_boost": voice.similarity_boost,
                "style": voice.style,
                "volume_adjustment_db": voice.volume_adjustment
            }
        }

        return final_audio, metadata
```

---

## 📋 Ejemplos Prácticos

### Ejemplo 1: Generar TTS Simple

```python
# Dashboard: Usuario escribe mensaje

from app.services.tts.voice_manager import VoiceManager

async def generate_message(text: str, voice_id: str):
    voice_manager = VoiceManager(elevenlabs, processor, db)

    audio, metadata = await voice_manager.generate_with_voice(
        text="Pedido número 42 está listo para retirar",
        voice_id="juan_carlos"
    )

    # Guardar
    filename = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{voice_id}.mp3"
    filepath = Path(f"storage/audio/{filename}")
    filepath.write_bytes(audio)

    return {
        "filename": filename,
        "metadata": metadata
    }
```

### Ejemplo 2: Generar con Jingle

```python
async def generate_with_jingle(text: str, voice_id: str):
    audio, metadata = await voice_manager.generate_with_voice(
        text="Atención! Nueva promoción disponible",
        voice_id="juan_carlos",
        apply_jingle=True,
        jingle_id="promo_intro"
    )

    return audio
```

### Ejemplo 3: Batch Processing

```python
async def generate_batch(messages: list[dict]):
    """
    Genera múltiples mensajes en paralelo
    """
    tasks = [
        voice_manager.generate_with_voice(
            text=msg["text"],
            voice_id=msg["voice_id"],
            apply_jingle=msg.get("has_jingle", False)
        )
        for msg in messages
    ]

    results = await asyncio.gather(*tasks)
    return results
```

### Ejemplo 4: FFMPEG Direct (Testing)

```bash
# Test 1: Normalizar un archivo
ffmpeg -i test.mp3 -af loudnorm=I=-16:LRA=7:TP=-2 normalized.mp3

# Test 2: Mix voz + música
ffmpeg -i voice.mp3 -i music.mp3 \
  -filter_complex "[0:a]volume=0dB[v];[1:a]volume=-12dB[m];[v][m]amix=inputs=2:duration=longest:normalize=0" \
  mixed.mp3

# Test 3: Ajustar volumen
ffmpeg -i input.mp3 -af volume=+3dB louder.mp3

# Test 4: Información de audio
ffprobe -v quiet -print_format json -show_format -show_streams input.mp3
```

---

## 🎯 Best Practices MediaFlowDemo

### 1. Voice Settings

✅ **DO**:
- Configurar voces UNA VEZ en Playground
- Usar `stability=100` para voces formales
- Usar `style=15-20` para anuncios serios
- Aplicar settings automáticamente desde DB

❌ **DON'T**:
- Pedir al usuario configurar en cada generación
- Usar `stability<50` para anuncios (inconsistente)
- Usar `style>60` para voces formales (muy expresivo)

### 2. Audio Processing

✅ **DO**:
- Normalizar TODO a -16 LUFS (broadcast standard)
- Usar single-pass `loudnorm` para velocidad
- Aplicar volume adjustment POR VOZ (no global)
- Mezclar jingles a -12dB (25% volumen)

❌ **DON'T**:
- Saltar normalización LUFS
- Usar `dynaudnorm` para producción (usar en preview)
- Aplicar volumen directamente al TTS (perder rango dinámico)

### 3. Performance

✅ **DO**:
- Usar `asyncio` para operaciones paralelas
- Cache de jingles en memoria
- Batch processing cuando sea posible
- Streaming para archivos grandes

❌ **DON'T**:
- Procesar secuencialmente si puedes paralelizar
- Cargar jingles en cada request
- Two-pass loudnorm en tiempo real

---

## 📖 Referencias

### Documentación Oficial

- **FFMPEG Filters**: https://ffmpeg.org/ffmpeg-filters.html
- **ElevenLabs API**: https://elevenlabs.io/docs/api-reference
- **EBU R128**: https://tech.ebu.ch/docs/r/r128.pdf

### MediaFlowDemo Docs

- `CLAUDE.md` - Contexto del proyecto
- `02-ARCHITECTURE-v2.1.md` - Arquitectura v2.1
- `04-IMPLEMENTATION-GUIDE.md` - Guía de implementación

---

**Última actualización**: 2025-11-22
**Versión**: 1.0
**Autor**: Claude (Anthropic) + MCP Ref Documentation
