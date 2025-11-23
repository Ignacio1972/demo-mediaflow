# 🔄 MediaFlow Legacy System - Assets Reutilizables para v2.1

**Fecha Análisis**: 2025-11-22
**Sistema Legacy**: http://plataforma.mediaflow.cl:2082 (PHP v1.0)
**Sistema Nuevo**: MediaFlowDemo v2.1 (FastAPI + Vue3)

---

## ⚡ IMPORTANTE: Mismo Servidor

**Ambos sistemas están en el MISMO servidor**:

```
Legacy (v1.0): /var/www/casa/           ← PHP + SQLite
Nuevo (v2.1):  /var/www/mediaflow-v2/   ← FastAPI + Vue3

✅ NO necesitas SSH ni sshpass
✅ Acceso directo con: cp, cat, ls, etc.
✅ Migración local simplificada
```

---

## 📋 Tabla de Contenidos

1. [Credenciales y Acceso](#credenciales-y-acceso)
2. [Configuraciones JSON Reutilizables](#configuraciones-json-reutilizables)
3. [Base de Datos](#base-de-datos)
4. [Archivos de Audio](#archivos-de-audio)
5. [Lógica de Negocio](#lógica-de-negocio)
6. [APIs y Servicios](#apis-y-servicios)
7. [Plan de Migración](#plan-de-migración)

---

## 🔐 Credenciales y Acceso

### Sistema Legacy (PHP v1.0)

**⚠️ IMPORTANTE**: Legacy y v2.1 están en el **MISMO SERVIDOR**

```bash
# Sistema Legacy
Path: /var/www/casa/
URL: http://plataforma.mediaflow.cl:2082

# Sistema v2.1 (actual)
Path: /var/www/mediaflow-v2/
URL: http://localhost:3001 (backend)
URL: http://localhost:5173 (frontend)

# NO necesitas SSH - acceso directo a archivos
# Puedes usar: cat, cp, ls, etc.
```

### API Keys (Reutilizables en v2.1) ✅

```env
# ElevenLabs TTS
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_BASE_URL=https://api.elevenlabs.io/v1
ELEVENLABS_MODEL_ID=eleven_multilingual_v2

# Claude AI (Anthropic)
CLAUDE_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_MAX_TOKENS=500

# AzuraCast Radio
AZURACAST_BASE_URL=http://localhost  # En el servidor legacy
AZURACAST_API_KEY=c3802cba5b5e61e8:fed31be9adb82ca57f1cf482d170851f
AZURACAST_STATION_ID=1
```

**⚠️ IMPORTANTE**: Estas API keys están **activas y funcionando** en producción. Puedes reutilizarlas en v2.1.

---

## 📦 Configuraciones JSON Reutilizables

### 1. Voces TTS (`voices-config.json`) ⭐ CRÍTICO

**Ubicación Legacy**: `/var/www/casa/src/api/data/voices-config.json`

**11 Voces Configuradas** (5 activas):

| ID | Nombre | ElevenLabs ID | Active | Volume Adj | Order | Default |
|----|--------|---------------|--------|------------|-------|---------|
| juan_carlos | Juan Carlos | G4IAP30yc6c1gK0csDfu | ✅ | 0 dB | 1 | ✅ |
| yorman | Mario | J2Jb9yZNvpXUNAL3a2bw | ✅ | +0.5 dB | 2 | ❌ |
| veronica | Francisca | Obg6KIFo8Md4PUo1m2mR | ✅ | +7 dB | 3 | ❌ |
| cristian | Jose Miguel | nNS8uylvF9GBWVSiIt5h | ✅ | +0.5 dB | 4 | ❌ |
| sandra | Titi | rEVYTKPqwSMhytFPayIb | ✅ | -0.5 dB | 5 | ❌ |

**JSON Completo**:
```json
{
    "voices": {
        "juan_carlos": {
            "id": "G4IAP30yc6c1gK0csDfu",
            "label": "Juan Carlos",
            "gender": "M",
            "active": true,
            "category": "custom",
            "is_default": true,
            "order": 1,
            "volume_adjustment": 0
        },
        "yorman": {
            "id": "J2Jb9yZNvpXUNAL3a2bw",
            "label": "Mario",
            "gender": "M",
            "active": true,
            "order": 2,
            "volume_adjustment": 0.5
        },
        "veronica": {
            "id": "Obg6KIFo8Md4PUo1m2mR",
            "label": "Francisca",
            "gender": "F",
            "active": true,
            "order": 3,
            "volume_adjustment": 7
        },
        "cristian": {
            "id": "nNS8uylvF9GBWVSiIt5h",
            "label": "Jose Miguel",
            "gender": "M",
            "active": true,
            "order": 4,
            "volume_adjustment": 0.5
        },
        "sandra": {
            "id": "rEVYTKPqwSMhytFPayIb",
            "label": "Titi",
            "gender": "F",
            "active": true,
            "order": 5,
            "volume_adjustment": -0.5
        }
    },
    "settings": {
        "default_voice": "juan_carlos",
        "version": "2.0"
    }
}
```

**Migración a v2.1**:
```python
# backend/app/seeds/voices.py

VOICES_SEED = [
    {
        "id": "juan_carlos",
        "name": "Juan Carlos",
        "elevenlabs_id": "G4IAP30yc6c1gK0csDfu",
        "gender": "M",
        "active": True,
        "style": 15.0,           # Default de legacy
        "stability": 100.0,      # Default de legacy (ajustado)
        "similarity_boost": 50.0,
        "volume_adjustment": 0.0,
        "order": 1
    },
    {
        "id": "yorman",
        "name": "Mario",
        "elevenlabs_id": "J2Jb9yZNvpXUNAL3a2bw",
        "gender": "M",
        "active": True,
        "style": 15.0,
        "stability": 100.0,
        "similarity_boost": 50.0,
        "volume_adjustment": 0.5,
        "order": 2
    },
    # ... resto de voces
]
```

### 2. TTS Config Global (`tts-config.json`)

**Ubicación Legacy**: `/var/www/casa/src/api/data/tts-config.json`

```json
{
    "silence": {
        "add_silence": true,
        "intro_seconds": 3,
        "outro_seconds": 5
    },
    "normalization": {
        "enabled": false,
        "target_lufs": -12,
        "output_volume": 1.3,
        "enable_compression": false
    },
    "voice_settings": {
        "style": 0.5,           // 50% expresividad (v2.1: 15.0 = 15%)
        "stability": 0.55,      // 55% estabilidad (v2.1: 100.0 = 100%)
        "similarity_boost": 0.8,
        "use_speaker_boost": true
    }
}
```

**⚠️ IMPORTANTE**: Legacy usa valores 0-1, v2.1 usa 0-100. Requiere conversión.

**Conversión para v2.1**:
```python
# Convertir de legacy (0-1) a v2.1 (0-100)
def convert_voice_settings(legacy_settings):
    return {
        "style": legacy_settings["style"] * 100,        # 0.5 → 50.0
        "stability": legacy_settings["stability"] * 100, # 0.55 → 55.0
        "similarity_boost": legacy_settings["similarity_boost"] * 100  # 0.8 → 80.0
    }
```

### 3. Jingle Config (`jingle-config.json`) ⭐ CRÍTICO

**Ubicación Legacy**: `/var/www/casa/src/api/data/jingle-config.json`

```json
{
    "jingle_defaults": {
        "enabled_by_default": false,
        "intro_silence": 7,
        "outro_silence": 4.5,
        "music_volume": 1.65,
        "voice_volume": 2.8,
        "fade_in": 1.5,
        "fade_out": 4.5,
        "ducking_enabled": true,
        "duck_level": 0.95,
        "default_music": "Uplift.mp3",
        "voice_settings": {
            "style": 0.15,      // 15% para jingles (más formal)
            "stability": 1.0,   // 100% estabilidad
            "similarity_boost": 0.5,
            "use_speaker_boost": true
        },
        "normalization_settings": {
            "enabled": false,
            "target_lufs": -10,
            "mode": "standard"
        },
        "compressor_settings": {
            "threshold": 0.055,
            "ratio": 6,
            "attack": 5,
            "release": 200,
            "makeup": 1.4
        }
    }
}
```

**Reutilización en v2.1**:
```python
# VoiceSettings model - campo jingle_settings
jingle_settings = {
    "music_volume_db": -12.0,    # Legacy: 1.65 ratio
    "voice_volume_db": 0.0,      # Legacy: 2.8 ratio
    "intro_silence": 7.0,
    "outro_silence": 4.5,
    "fade_in": 1.5,
    "fade_out": 4.5,
    "ducking_enabled": True,
    "duck_level": 0.95,
    "default_music": "Uplift.mp3"
}
```

### 4. Multi-Cliente AI (`clients-config.json`) ⭐ INNOVADOR

**Ubicación Legacy**: `/var/www/casa/src/api/data/clients-config.json`

**6 Clientes Configurados**:

1. **Casa Costanera** (centro comercial)
2. **Mall Independencia** (centro comercial familiar)
3. **Mall Plaza** (precios bajos)
4. **Restaurante La Pepita** (italiano)
5. **Generic** (cliente genérico)
6. **Supermercado Líder** (activo) ⭐

**Ejemplo de Contexto AI**:
```json
{
    "custom_1757645735": {
        "name": "Supermercado Líder",
        "context": "LÍDER - Identidad y Voz de Marca\n- Cadena líder de supermercados en Chile\n- Target: Familias chilenas, clase media\n- Propuesta: 'Precios Bajos Todos los Días'\n- Tono: Cercano, confiable, ahorrativo\n\nTARJETA LÍDER BCI:\n- 6% de devolución en compras Líder\n- 10% descuento primera compra\n- 3 cuotas precio contado\n\nPALABRAS CLAVE:\n- PROMOCIÓN: anuncio local urgente\n- NO SE OLVIDE: anuncio institucional\n- INFORMACIÓN: anuncio operacional",
        "category": "custom",
        "active": true
    }
}
```

**Reutilización en v2.1**:
```python
# backend/app/models/client_config.py
class ClientConfig(Base):
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    context = Column(Text)  # Prompt AI personalizado
    category = Column(String)
    active = Column(Boolean, default=True)
    claude_model = Column(String, default="claude-sonnet-4-20250514")
    tone = Column(String, default="profesional")
    word_limit = Column(Integer, default=50)
```

---

## 🗄️ Base de Datos

### Schema Actual (SQLite - Legacy)

**Ubicación**: `/var/www/casa/database/casa.db`

```sql
CREATE TABLE audio_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE NOT NULL,
    display_name TEXT,
    category TEXT DEFAULT 'General',
    voice_id TEXT,
    voice_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration REAL,
    file_size INTEGER,
    is_saved BOOLEAN DEFAULT 0,
    tags TEXT,
    notes TEXT,
    play_count INTEGER DEFAULT 0,
    last_played DATETIME,
    source TEXT DEFAULT 'tts',  -- 'tts' o 'upload'
    original_filename TEXT,
    client_id TEXT DEFAULT 'CASA',
    metadata JSON,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    saved_at DATETIME,
    radio_sent_count INTEGER DEFAULT 0,
    last_radio_sent_at DATETIME,
    duration_seconds INTEGER,
    updated_at DATETIME
);
```

### Datos en Producción

**Estadísticas de Categorías** (mensajes guardados activos):

| Categoría | Total Mensajes |
|-----------|----------------|
| emergencias | 1 |
| eventos | 6 |
| informacion | 2 |
| ofertas | 5 |
| servicios | 2 |
| sin_categoria | 26 |
| **TOTAL** | **42** |

### Migración a v2.1 (PostgreSQL)

**Script de Migración**:
```python
# backend/app/migrations/import_legacy_data.py

import sqlite3
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AudioMessage, VoiceSettings, Category

async def migrate_legacy_audio_metadata(db: AsyncSession):
    """
    Migra audio_metadata de SQLite legacy a PostgreSQL v2.1
    """
    # Conectar a SQLite legacy (vía SSH o dump local)
    conn = sqlite3.connect('casa_legacy.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            filename, display_name, category, voice_id,
            created_at, is_saved, source, description,
            play_count, radio_sent_count
        FROM audio_metadata
        WHERE is_active = 1
    """)

    migrated = 0
    for row in cursor.fetchall():
        # Crear AudioMessage en v2.1
        message = AudioMessage(
            filename=row[0],
            original_text=row[7] or "",  # description
            voice_id=row[3],
            category_id=map_category(row[2]),  # Mapear categoría
            is_saved=bool(row[5]),
            is_favorite=False,  # Nuevo campo v2.1
            source=row[6],
            created_at=row[4]
        )
        db.add(message)
        migrated += 1

    await db.commit()
    return migrated

def map_category(legacy_cat):
    """Mapea categorías legacy a IDs v2.1"""
    mapping = {
        "ofertas": "ofertas",
        "eventos": "eventos",
        "informativos": "informativos",
        "servicios": "servicios",
        "emergencias": "emergencias",
        "sin_categoria": None  # Sin categoría en v2.1
    }
    return mapping.get(legacy_cat.lower())
```

---

## 🎵 Archivos de Audio

### Música de Fondo (Jingles)

**Ubicación Legacy**: `/var/www/casa/public/audio/music/`

**7 Archivos MP3 Disponibles**:

| Archivo | Tamaño | Descripción |
|---------|--------|-------------|
| **Uplift.mp3** ⭐ | 10.0 MB | **Default** - Energético, upbeat |
| Cool.mp3 | 11.1 MB | Relajado, cool |
| Kids.mp3 | 9.3 MB | Infantil, alegre |
| Pop.mp3 | 9.2 MB | Pop moderno |
| Slow.mp3 | 8.5 MB | Lento, emocional |
| Smooth.mp3 | 6.4 MB | Suave, profesional |
| _Independencia.mp3 | 2.5 MB | Custom Mall Independencia |

**Comandos para Copiar** (local - mismo servidor):
```bash
# Copiar todos los archivos de música
cp /var/www/casa/public/audio/music/*.mp3 /var/www/mediaflow-v2/storage/jingles/

# O uno por uno
cp /var/www/casa/public/audio/music/Uplift.mp3 /var/www/mediaflow-v2/storage/jingles/

# Verificar
ls -lh /var/www/mediaflow-v2/storage/jingles/
```

### Archivos TTS Generados

**Ubicación Legacy**:
- Temporales: `/var/www/casa/src/api/temp/`
- Permanentes: En AzuraCast Docker

**Total de Archivos**: 42 mensajes guardados (según DB)

**Migración Opcional**:
```bash
# Listar archivos en AzuraCast
ssh root@148.113.205.115 "docker exec azuracast ls -lh /var/azuracast/stations/mediaflow/media/Grabaciones/"

# Descargar archivos específicos si es necesario
# (NO recomendado, mejor regenerar con v2.1)
```

---

## 🧠 Lógica de Negocio Reutilizable

### 1. Sistema de Categorías

**Legacy** (hardcoded):
- ofertas (rojo)
- eventos (morado)
- informativos (azul)
- servicios (azul claro)
- horarios (verde azulado)
- emergencias (naranja)
- sin_categoria (gris)

**v2.1** (dinámico):
```python
# Seed inicial basado en legacy
CATEGORIES_SEED = [
    {"id": "ofertas", "name": "Ofertas", "icon": "🏷️", "color": "#EF4444", "order": 1},
    {"id": "eventos", "name": "Eventos", "icon": "🎉", "color": "#A855F7", "order": 2},
    {"id": "informativos", "name": "Informativos", "icon": "ℹ️", "color": "#3B82F6", "order": 3},
    {"id": "servicios", "name": "Servicios", "icon": "🛠️", "color": "#06B6D4", "order": 4},
    {"id": "emergencias", "name": "Emergencias", "icon": "⚠️", "color": "#F97316", "order": 5},
]
```

### 2. Voice Settings por Tipo de Mensaje

**Legacy**:
- **TTS Normal**: style=0.5, stability=0.55, similarity=0.8
- **Jingles**: style=0.15, stability=1.0, similarity=0.5

**v2.1** (mejorado):
```python
# Cada voz tiene sus propios settings
# NO hay "global" vs "jingle" settings
# Se decide por contexto en VoiceManager
```

### 3. Normalización LUFS

**Legacy**:
- AudioProcessor v2 (PHP)
- Two-pass normalization
- Target: -12 LUFS (TTS), -10 LUFS (jingles)

**v2.1** (mantener):
```python
# backend/app/services/audio/processor.py
TARGET_LUFS = -16.0  # Mejorado para broadcast
TARGET_LRA = 7.0
TARGET_TP = -2.0
```

### 4. Sistema de Ducking

**Legacy** (FFmpeg sidechaincompress):
```bash
ffmpeg -i voice.mp3 -i music.mp3 \
  -filter_complex "[1:a]volume=1.65[music]; \
   [0:a]volume=2.8[voice]; \
   [music][voice]sidechaincompress=threshold=0.055:ratio=6:attack=5:release=200" \
  output.mp3
```

**v2.1** (simplificado con volúmenes):
```python
# Usar volume adjustment en dB
music_volume_db = -12.0  # ~25% (más simple)
voice_volume_db = 0.0    # 100%
```

---

## 🔌 APIs y Servicios

### Endpoints Legacy Disponibles

**Ubicación**: `/var/www/casa/src/api/`

| Archivo PHP | Funcionalidad | Reutilizable v2.1 |
|-------------|---------------|-------------------|
| `generate.php` | Generación TTS principal | ✅ Lógica |
| `jingle-service.php` | Jingles con música | ✅ Lógica |
| `claude-service.php` | Sugerencias AI | ✅ Prompts |
| `audio-scheduler.php` | Programación automática | ✅ Lógica |
| `biblioteca.php` | Gestión de biblioteca | ✅ Funcionalidades |
| `radio-service.php` | Integración AzuraCast | ⚠️ Específico player |
| `music-manager-service.php` | Gestión de música | ✅ Validaciones |

### Lógica de `generate.php` (Reutilizable)

```php
// Legacy: src/api/generate.php (líneas clave)

// 1. Obtener voice settings
$voiceConfig = $voicesConfig['voices'][$voiceKey] ?? null;
$volumeAdjustment = $voiceConfig['volume_adjustment'] ?? 0;

// 2. Generar con ElevenLabs
$ttsAudio = generateWithElevenLabs($text, $voiceId, $voiceSettings);

// 3. Agregar silencios
$withSilence = addSilences($ttsAudio, $introSeconds, $outroSeconds);

// 4. Normalizar LUFS (opcional)
if ($normalize) {
    $normalized = AudioProcessor::normalizeToTarget($withSilence, $targetLufs);
}

// 5. Ajustar volumen
if ($volumeAdjustment != 0) {
    $adjusted = adjustVolume($normalized, $volumeAdjustment);
}

// 6. Guardar metadata
saveToDatabase($filename, $metadata);

// 7. Upload a AzuraCast
uploadToAzuraCast($finalAudio, $filename);
```

**Traducción a v2.1**:
```python
# backend/app/services/tts/voice_manager.py

async def generate_with_voice(
    self,
    text: str,
    voice_id: str,
    apply_jingle: bool = False
) -> tuple[bytes, dict]:

    # 1. Leer voice settings de DB
    voice = self.db.query(VoiceSettings).filter_by(id=voice_id).first()

    # 2. Generar TTS
    tts_audio = await self.elevenlabs.generate_audio(
        text=text,
        voice_id=voice.elevenlabs_id,
        voice_settings={
            "stability": voice.stability,
            "similarity_boost": voice.similarity_boost,
            "style": voice.style
        }
    )

    # 3. Normalizar LUFS
    normalized = await self.processor.normalize_lufs(tts_audio)

    # 4. Ajustar volumen
    adjusted = await self.processor.apply_volume_adjustment(
        normalized,
        voice.volume_adjustment
    )

    # 5. Aplicar jingle (opcional)
    if apply_jingle:
        final = await self.processor.mix_with_jingle(
            adjusted,
            jingle_audio,
            voice.jingle_settings
        )

    return final, metadata
```

---

## 📋 Plan de Migración

### Fase 1: Setup Inicial (Día 1)

**1.1 Copiar API Keys**
```bash
# Agregar al .env de v2.1
cd /var/www/mediaflow-v2/backend
nano .env

# Copiar keys de legacy:
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
CLAUDE_API_KEY=your_anthropic_api_key_here
```

**1.2 Copiar Música** (local - mismo servidor)
```bash
# Crear directorio si no existe
mkdir -p /var/www/mediaflow-v2/storage/jingles/

# Copiar archivos de música
cp /var/www/casa/public/audio/music/*.mp3 \
  /var/www/mediaflow-v2/storage/jingles/

# Verificar
ls -lh /var/www/mediaflow-v2/storage/jingles/
```

### Fase 2: Migración de Datos (Día 2)

**2.1 Crear Seeds de Voces**
```python
# backend/app/seeds/voices.py
# Copiar configuración de voices-config.json
# Convertir volume_adjustment (mantener valores)
# Agregar style, stability, similarity defaults
```

**2.2 Crear Seeds de Categorías**
```python
# backend/app/seeds/categories.py
# Mapear categorías legacy a v2.1
# Agregar iconos y colores
```

**2.3 Migrar Audio Metadata (OPCIONAL)**
```bash
# Copiar base de datos legacy (mismo servidor)
cp /var/www/casa/database/casa.db /tmp/casa_legacy.db

# O acceder directamente
# La BD está en: /var/www/casa/database/casa.db

# Ejecutar script de migración
cd /var/www/mediaflow-v2/backend
python app/migrations/import_legacy_data.py
```

### Fase 3: Configuración (Día 3)

**3.1 Configurar Jingle Settings**
```python
# Para cada voz en VoiceSettings
jingle_settings = {
    "music_volume_db": -12.0,
    "voice_volume_db": 0.0,
    "intro_silence": 7.0,
    "outro_silence": 4.5,
    "fade_in": 1.5,
    "fade_out": 4.5,
    "ducking_enabled": True,
    "duck_level": 0.95
}
```

**3.2 Configurar Multi-Cliente (OPCIONAL)**
```python
# Copiar clients-config.json a ClientConfig model
# Especialmente "Supermercado Líder" que está activo
```

### Fase 4: Testing (Día 4)

**4.1 Pruebas de Generación**
```bash
# Test con voz juan_carlos
curl -X POST http://localhost:3001/api/v1/audio/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Prueba de migración desde sistema legacy",
    "voice_id": "juan_carlos"
  }'
```

**4.2 Verificar Voice Settings**
```bash
# Verificar que volume_adjustment se aplica correctamente
# Comparar audio generado con legacy
```

**4.3 Pruebas de Jingles**
```bash
# Test con jingle
curl -X POST http://localhost:3001/api/v1/audio/generate \
  -d '{
    "text": "Prueba con jingle",
    "voice_id": "juan_carlos",
    "apply_jingle": true,
    "jingle_id": "Uplift"
  }'
```

---

## 🎯 Elementos Críticos a Migrar

### Prioridad ALTA ⭐

1. **API Keys** (ElevenLabs + Claude)
   - ✅ Copiar directamente al .env
   - Validar que funcionan

2. **Voces Configuradas** (5 activas)
   - ✅ Seed con IDs de ElevenLabs
   - ✅ Mantener volume_adjustment exacto
   - ✅ Establecer juan_carlos como default

3. **Música de Fondo** (7 archivos)
   - ✅ Copiar a storage/jingles/
   - ✅ Uplift.mp3 como default

4. **Jingle Settings**
   - ✅ music_volume: 1.65 → -12dB
   - ✅ voice_volume: 2.8 → 0dB
   - ✅ ducking_enabled: true
   - ✅ intro_silence: 7s, outro_silence: 4.5s

### Prioridad MEDIA

5. **Categorías**
   - ✅ Crear seed con 5 categorías legacy
   - Agregar iconos y colores

6. **TTS Config Global**
   - ⚠️ Convertir valores 0-1 a 0-100
   - Aplicar como defaults en Playground

7. **Multi-Cliente AI**
   - ✅ Copiar contexto de "Supermercado Líder"
   - Crear ClientConfig model

### Prioridad BAJA (Opcional)

8. **Audio Metadata Legacy**
   - 42 mensajes guardados
   - Migrar solo si cliente lo requiere

9. **Schedules Activos**
   - Verificar si hay programaciones en producción
   - Migrar manualmente si es crítico

---

## 📊 Comparación Legacy vs v2.1

| Aspecto | Legacy (PHP) | v2.1 (FastAPI) | Acción |
|---------|--------------|----------------|--------|
| **Voice Settings** | Global (tts-config.json) | Individual por voz | ✅ Mejorado |
| **Categorías** | Hardcoded | Dinámico (DB) | ✅ Mejorado |
| **Normalización LUFS** | -12 LUFS | -16 LUFS | ✅ Mejorado |
| **API Keys** | .env | .env | ✅ Reutilizar |
| **Voces** | 11 configuradas (5 activas) | Seed inicial | ✅ Migrar |
| **Música** | 7 archivos MP3 | Storage local | ✅ Copiar |
| **Multi-Cliente** | 6 clientes | ClientConfig | ✅ Migrar |
| **Jingles** | sidechaincompress | Volume mixing | ⚠️ Simplificado |
| **Base de Datos** | SQLite | PostgreSQL | ⚠️ Migración opcional |

---

## 🚀 Scripts de Migración Automática

### Script 1: Copiar Assets (Local - Mismo Servidor)

```bash
#!/bin/bash
# migrate-assets.sh

set -e

LEGACY_PATH="/var/www/casa"
V2_PATH="/var/www/mediaflow-v2"

echo "🔄 Migrando assets de Legacy a v2.1 (mismo servidor)..."

# 1. Copiar música
echo "📁 Copiando archivos de música..."
mkdir -p $V2_PATH/storage/jingles/
cp $LEGACY_PATH/public/audio/music/*.mp3 $V2_PATH/storage/jingles/

# 2. Copiar base de datos (para análisis)
echo "💾 Copiando base de datos legacy..."
cp $LEGACY_PATH/database/casa.db /tmp/casa_legacy.db

# 3. Copiar configs JSON (para referencia)
echo "⚙️ Copiando configuraciones JSON..."
mkdir -p /tmp/legacy_configs
cp $LEGACY_PATH/src/api/data/*.json /tmp/legacy_configs/

# 4. Leer API keys del .env legacy
echo "🔑 Leyendo API keys..."
cat $LEGACY_PATH/.env | grep -E '(ELEVEN|CLAUDE|AZURA)' > /tmp/legacy_api_keys.txt

echo "✅ Migración de assets completada"
echo "📁 Música copiada a: $V2_PATH/storage/jingles/"
echo "💾 BD legacy en: /tmp/casa_legacy.db"
echo "⚙️ Configs en: /tmp/legacy_configs/"
echo "🔑 API keys en: /tmp/legacy_api_keys.txt"
```

### Script 2: Generar Seeds

```python
#!/usr/bin/env python3
# generate_seeds_from_legacy.py

import json
import sqlite3

def generate_voice_seeds():
    """Genera seeds de voces desde voices-config.json legacy"""

    with open('/tmp/legacy_configs/voices-config.json') as f:
        legacy = json.load(f)

    seeds = []
    for key, voice in legacy['voices'].items():
        if not voice.get('active'):
            continue

        seed = {
            'id': key,
            'name': voice['label'],
            'elevenlabs_id': voice['id'],
            'gender': voice['gender'],
            'active': True,
            'style': 15.0,  # Default formal
            'stability': 100.0 if key == 'juan_carlos' else 75.0,
            'similarity_boost': 50.0,
            'volume_adjustment': float(voice.get('volume_adjustment', 0)),
            'order': voice.get('order', 99)
        }
        seeds.append(seed)

    # Guardar
    with open('backend/app/seeds/voices_generated.py', 'w') as f:
        f.write('VOICES_SEED = ')
        f.write(json.dumps(seeds, indent=2))

    print(f"✅ Generados {len(seeds)} seeds de voces")

def generate_category_seeds():
    """Genera seeds de categorías desde audio_metadata"""

    conn = sqlite3.connect('/tmp/casa_legacy.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT category, COUNT(*) as count
        FROM audio_metadata
        WHERE is_active = 1 AND category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
    """)

    # Mapeo de colores
    colors = {
        'ofertas': '#EF4444',
        'eventos': '#A855F7',
        'informativos': '#3B82F6',
        'servicios': '#06B6D4',
        'emergencias': '#F97316',
        'sin_categoria': '#6B7280'
    }

    icons = {
        'ofertas': '🏷️',
        'eventos': '🎉',
        'informativos': 'ℹ️',
        'servicios': '🛠️',
        'emergencias': '⚠️',
        'sin_categoria': '📁'
    }

    seeds = []
    for idx, (cat, count) in enumerate(cursor.fetchall(), 1):
        cat_lower = cat.lower()
        if cat_lower == 'sin_categoria':
            continue  # Skip en v2.1

        seed = {
            'id': cat_lower,
            'name': cat.title(),
            'icon': icons.get(cat_lower, '📦'),
            'color': colors.get(cat_lower, '#6B7280'),
            'order': idx
        }
        seeds.append(seed)

    print(f"✅ Generadas {len(seeds)} categorías")
    return seeds

if __name__ == '__main__':
    generate_voice_seeds()
    generate_category_seeds()
```

---

## 📝 Checklist de Migración

### Pre-Migración
- [ ] Acceso SSH confirmado (root@148.113.205.115)
- [ ] Backup de legacy creado
- [ ] v2.1 en desarrollo funcionando

### Migración de Assets
- [ ] API Keys copiadas al .env
- [ ] Música copiada a storage/jingles/
- [ ] Base de datos legacy descargada
- [ ] Configs JSON descargadas

### Migración de Datos
- [ ] Seeds de voces creados (5 activas)
- [ ] Seeds de categorías creados
- [ ] Jingle settings configurados
- [ ] Multi-cliente configurado (opcional)

### Testing
- [ ] Test generación TTS simple
- [ ] Test con diferentes voces
- [ ] Test volume_adjustment
- [ ] Test generación con jingle
- [ ] Test normalización LUFS
- [ ] Comparación audio legacy vs v2.1

### Post-Migración
- [ ] Documentación actualizada
- [ ] Cliente informado de cambios
- [ ] Plan de cutover definido

---

## 🎓 Lecciones del Sistema Legacy

### ✅ Qué Funcionó Bien

1. **Voice Settings por Voz**
   - `volume_adjustment` individual por voz
   - Facilita calibración fina

2. **Jingle System Robusto**
   - Ducking automático
   - Múltiples músicas disponibles
   - Configuración flexible

3. **Multi-Cliente AI**
   - Contextos personalizados
   - Palabras clave por cliente
   - Tonos configurables

4. **Normalización LUFS**
   - AudioProcessor v2 bien implementado
   - Two-pass para precisión

### ⚠️ Qué Mejorar en v2.1

1. **Voice Settings Globales**
   - Legacy: global en tts-config.json
   - v2.1: individual por voz en VoiceSettings

2. **Categorías Hardcoded**
   - Legacy: 7 categorías fijas en código
   - v2.1: totalmente dinámico en DB

3. **Favoritos por Categoría**
   - Legacy: no existe
   - v2.1: `is_favorite` cross-category

4. **Dashboard Sobrecargado**
   - Legacy: categoría + jingle + AI en una pantalla
   - v2.1: Dashboard simple, Library poderosa

---

## 📞 Contacto y Soporte

**Sistema Legacy** (mismo servidor):
- Path: /var/www/casa/
- URL: http://plataforma.mediaflow.cl:2082
- Acceso: directo (no requiere SSH)

**Documentación Legacy**:
- CLAUDE.md: `/var/www/casa/CLAUDE.md`
- Logs: `/var/www/casa/src/api/logs/`
- DB: `/var/www/casa/database/casa.db`

**Soporte**:
- En caso de dudas sobre legacy, revisar CLAUDE.md del servidor
- Logs disponibles en src/api/logs/ (por servicio)
- Base de datos accesible con sqlite3

---

**Última actualización**: 2025-11-22
**Autor**: Claude (Anthropic)
**Versión**: 1.0
**Estado**: Análisis completo del sistema legacy para migración a v2.1
