# 🎵 Player Local - Integración con MediaFlowDemo

**Proyecto:** MediaFlowDemo v2
**Fecha:** 2025-11-22
**Estado:** Player funcional esperando integración

---

## 📌 Propósito del Documento

Este documento explica cómo funciona el **player local** (Mac Mini) y cómo **MediaFlowDemo v2** se integrará con él para crear un sistema completo de radio automatizada con TTS.

---

## 🎯 ¿Qué es el Player Local?

Es un reproductor de audio Python que corre **24/7 en un Mac Mini** y que:

✅ **Reproduce música local continuamente** (30 archivos MP3 en loop)
✅ **Recibe interrupciones TTS desde el VPS** vía HTTP polling
✅ **Implementa ducking profesional** (fade out/in automático)
✅ **Provee interfaz web** para control remoto (Flask en puerto 5000)

### **Estado Actual:**
- ✅ Funcionando 24/7
- ✅ Polling al VPS cada 2 segundos
- ✅ Sistema de ducking implementado
- ⏳ **Esperando que MediaFlowDemo v2 provea los endpoints API**

---

## 🏗️ Arquitectura Actual del Sistema

```
┌─────────────────────────────────────────────────────────┐
│  VPS (148.113.205.115:2082)                             │
│  MediaFlowDemo v2 (FastAPI + Vue)                       │
│                                                         │
│  ┌────────────────────────────────────────────┐        │
│  │ API Endpoints (A IMPLEMENTAR)              │        │
│  │                                            │        │
│  │ GET  /api/player/pending                   │        │
│  │      → TTS pendiente de envío              │        │
│  │                                            │        │
│  │ POST /api/player/delivered                 │        │
│  │      → Marcar TTS como reproducido         │        │
│  └────────────────────────────────────────────┘        │
│                                                         │
│  📁 /storage/audio/                                     │
│      → Archivos TTS generados (MP3 públicos)           │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ HTTP Polling cada 2s
                         │
┌────────────────────────┴─────────────────────────────────┐
│  Mac Mini (Player Local - Python)                        │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ VPSClient                                   │        │
│  │ - Polling automático cada 2 segundos        │        │
│  │ - Descarga MP3 desde VPS                    │        │
│  │ - Confirma reproducción                     │        │
│  └─────────────────────────────────────────────┘        │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ TTSHandler                                  │        │
│  │ - Ducking (fade out música 2s)              │        │
│  │ - Reproducción de TTS                       │        │
│  │ - Restauración (fade in música 2s)          │        │
│  └─────────────────────────────────────────────┘        │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ AudioEngine                                 │        │
│  │ - Música continua (30 tracks en loop)       │        │
│  │ - Mixing de canales                         │        │
│  │ - Output a speakers 🔊                       │        │
│  └─────────────────────────────────────────────┘        │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ Web UI (Flask)                              │        │
│  │ http://localhost:5000                       │        │
│  │ - Control de volúmenes                      │        │
│  │ - Play/Pause/Next                           │        │
│  │ - Status en tiempo real                     │        │
│  └─────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

---

## 🔌 Protocolo de Comunicación (V1 - Actual)

### **1. GET /api/player/pending** - Consultar TTS Pendiente

El player hace polling cada 2 segundos.

#### Request del Player:
```http
GET http://148.113.205.115:2082/api/player/pending
User-Agent: MediaflowPlayer/1.0
```

#### Response (Sin TTS pendiente):
```json
{
  "status": "ok",
  "pending": false,
  "message": "No pending TTS"
}
```

#### Response (Con TTS pendiente):
```json
{
  "status": "ok",
  "pending": true,
  "tts": {
    "id": "tts_12345",
    "text": "Atención: El pedido número 42 está listo",
    "audio_url": "http://148.113.205.115:2082/storage/audio/tts_12345.mp3",
    "created_at": "2024-11-22 15:30:00",
    "priority": "normal"
  }
}
```

**Campos importantes:**
- `pending` (bool): Si hay TTS esperando
- `tts.id` (string): ID único para confirmación
- `tts.audio_url` (string): URL completa del MP3
- `tts.priority` (string): `"normal"` | `"urgent"`

---

### **2. POST /api/player/delivered** - Confirmar Reproducción

El player confirma cuando termina de reproducir.

#### Request del Player:
```http
POST http://148.113.205.115:2082/api/player/delivered
Content-Type: application/x-www-form-urlencoded

action=mark_as_delivered&id=tts_12345
```

#### Response (Éxito):
```json
{
  "status": "ok",
  "message": "TTS marked as delivered"
}
```

#### Response (Error):
```json
{
  "status": "error",
  "message": "TTS ID not found"
}
```

---

## 🔄 Flujo Completo de Comunicación

```
┌─────────────┐                              ┌──────────────┐
│  VPS        │                              │ Player Local │
│ MediaFlow   │                              │  (Mac Mini)  │
└──────┬──────┘                              └──────┬───────┘
       │                                            │
       │ 1. Usuario genera TTS en dashboard         │
       │    - Texto ingresado                       │
       │    - TTS generado con ElevenLabs           │
       │    - MP3 guardado + DB insert              │
       │    - status = "pending"                    │
       │                                            │
       │                          2. Polling (cada 2s)
       │    ◄───────────────────────────────────────│
       │    GET /api/player/pending                 │
       │                                            │
       │    ───────────────────────────────────────►│
       │    {pending: true, tts: {...}}             │
       │                                            │
       │                          3. Player descarga MP3
       │    ◄───────────────────────────────────────│
       │    GET /storage/audio/tts_12345.mp3        │
       │                                            │
       │    ───────────────────────────────────────►│
       │    [Binary MP3 data]                       │
       │                                            │
       │                          4. Player ejecuta:
       │                             - Fade out música (2s)
       │                             - Silence (0.5s)
       │                             - TTS play (5s ej.)
       │                             - Silence (0.5s)
       │                             - Fade in música (2s)
       │                                            │
       │                          5. Confirmar entrega
       │    ◄───────────────────────────────────────│
       │    POST /api/player/delivered              │
       │    {action: "mark_as_delivered", id: "..."}│
       │                                            │
       │ 6. Update DB:                              │
       │    status = "delivered"                    │
       │    delivered_at = NOW()                    │
       │                                            │
       │    ───────────────────────────────────────►│
       │    {status: "ok"}                          │
       │                                            │
```

**Tiempo total:** ~10-15 segundos desde creación hasta reproducción.

---

## ⚙️ Configuración Actual del Player

### config.json (Mac Mini)

```json
{
  "vps": {
    "enabled": true,
    "polling_url": "http://148.113.205.115:2082/api/player/pending",
    "polling_interval": 2,
    "download_url": "http://148.113.205.115:2082/"
  },
  "ducking": {
    "enabled": true,
    "fade_out_duration": 2,
    "fade_in_duration": 2,
    "duck_level": 0.05,
    "pre_tts_silence": 0.5,
    "post_tts_silence": 0.5
  },
  "volumes": {
    "music": 0.3,
    "tts": 1.0,
    "master": 1.0
  }
}
```

### Parámetros Clave:

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `polling_interval` | 2s | Frecuencia de consulta al VPS |
| `fade_out_duration` | 2s | Fade out de música antes de TTS |
| `fade_in_duration` | 2s | Fade in de música después de TTS |
| `duck_level` | 0.05 (5%) | Volumen de música durante TTS |
| `pre_tts_silence` | 0.5s | Silencio antes del TTS |
| `post_tts_silence` | 0.5s | Silencio después del TTS |

---

## 🎵 Sistema de Ducking (Timeline Visual)

```
Volumen Música
    100%  █████████████████████████                  █████████████
          │                       │                  │
          │                       │                  │
     50%  │                       │                  │
          │                       │                  │
          │    FADE OUT (2s)      │   FADE IN (2s)   │
      5%  │                       ████████████████   │
          │                       │  TTS Playing  │   │
          │                       │               │   │
      0%  └───────────────────────┴───────────────┴───┴─────────────►
                                  │               │
                                  └─ TTS ─────────┘
                                  (Ej: 5 segundos)

Tiempo: 0s    1s    2s    3s    4s    5s    6s    7s    8s    9s
        │     │     │     │     │     │     │     │     │     │
        Música 100% → Fade → Silence → TTS → Silence → Fade → Música 100%
                               0.5s      5s       0.5s

TOTAL: ~10 segundos para un TTS de 5s
```

**Resultado:** La música baja suavemente, se reproduce el TTS con claridad, y la música vuelve gradualmente.

---

## 🗄️ Estructura de Base de Datos (Sistema Actual - PHP)

### Tabla: tts_queue

```sql
CREATE TABLE tts_queue (
    id VARCHAR(50) PRIMARY KEY,
    text TEXT NOT NULL,
    audio_url VARCHAR(500) NOT NULL,
    status ENUM('pending', 'delivered'),
    priority ENUM('normal', 'urgent'),
    created_at DATETIME DEFAULT NOW(),
    delivered_at DATETIME,
    duration_seconds DECIMAL(5,2),
    file_size_bytes INTEGER,

    INDEX idx_status (status),
    INDEX idx_created (created_at)
);
```

**Problema identificado:** Esta tabla está pensada para PHP/SQLite simple. MediaFlowDemo v2 necesitará un modelo más robusto.

---

## 💡 ANÁLISIS Y PROPUESTAS DE MEJORA

### **Problemas del Sistema Actual:**

#### 1. **Polling es Ineficiente** ⚠️
- **Problema:** 30 requests/minuto innecesarios (43,200 al día)
- **Impacto:** Consume recursos, delay de hasta 2s
- **Solución propuesta:** WebSocket bidireccional

#### 2. **Sin Cola en el Player** ⚠️
- **Problema:** Si llegan 2 TTS seguidos, el 2do se pierde
- **Impacto:** Mensajes perdidos si hay múltiples usuarios
- **Solución propuesta:** Queue local en el player

#### 3. **Sin Sistema de Prioridades Real** ⚠️
- **Problema:** Solo "normal" vs "urgent" en DB, no se usan
- **Impacto:** Mensajes urgentes no se priorizan realmente
- **Solución propuesta:** Sistema de prioridades con niveles

#### 4. **Sin Jingles Dinámicos** ⚠️
- **Problema:** No hay intro/outro antes/después del TTS
- **Impacto:** TTS suena seco, sin identidad
- **Solución propuesta:** Sistema de jingles configurables

#### 5. **Sin Monitoreo** ⚠️
- **Problema:** No se puede saber si el player está activo
- **Impacto:** Mensajes pueden perderse sin saberlo
- **Solución propuesta:** Heartbeat + dashboard de monitoreo

---

## 🚀 MEJORAS PROPUESTAS PARA MEDIAFLOWDEMO V2

### **Mejora 1: WebSocket Bidireccional** ⭐

**Estado actual:**
```
Player → (cada 2s) → VPS
         HTTP GET
```

**Estado propuesto:**
```
Player ←→ VPS (WebSocket permanente)
  - Player envía: heartbeat, status
  - VPS envía: TTS push instantáneo
```

**Beneficios:**
- ✅ Entrega instantánea (0s delay vs 2s actual)
- ✅ Reducción del 99% de requests HTTP
- ✅ Bidireccional: VPS puede pedir status del player
- ✅ Eventos en tiempo real (track changed, volume updated, etc.)

**Implementación FastAPI:**
```python
# backend/app/api/routes/player.py
from fastapi import WebSocket

@app.websocket("/ws/player")
async def player_websocket(websocket: WebSocket):
    await websocket.accept()

    # Registrar conexión
    player_manager.register(websocket)

    try:
        while True:
            # Recibir eventos del player
            data = await websocket.receive_json()

            if data['type'] == 'heartbeat':
                await handle_heartbeat(data)

            elif data['type'] == 'tts_completed':
                await mark_tts_delivered(data['tts_id'])

    except WebSocketDisconnect:
        player_manager.unregister(websocket)
```

**En el player (Python):**
```python
# Reemplazar polling por WebSocket
import websockets

async with websockets.connect('ws://vps:8000/ws/player') as ws:
    while True:
        message = await ws.recv()
        data = json.loads(message)

        if data['type'] == 'new_tts':
            await play_tts(data['tts'])
```

---

### **Mejora 2: Cola Local en el Player** ⭐

**Problema actual:** Solo procesa 1 TTS a la vez, otros se pierden.

**Solución:**
```python
# En el player local
class TTSQueue:
    def __init__(self):
        self.queue = []
        self.processing = False

    async def add(self, tts):
        self.queue.append(tts)
        if not self.processing:
            await self.process_next()

    async def process_next(self):
        if not self.queue:
            return

        self.processing = True
        tts = self.queue.pop(0)

        await play_with_ducking(tts)
        await confirm_to_vps(tts['id'])

        self.processing = False
        await self.process_next()  # Siguiente en cola
```

**Beneficios:**
- ✅ No se pierden mensajes
- ✅ Procesamiento secuencial ordenado
- ✅ Prioridades respetadas

---

### **Mejora 3: Sistema de Prioridades Mejorado** ⭐

**Estado actual:** Solo 2 niveles (normal, urgent)

**Propuesta:** 5 niveles de prioridad

| Nivel | Nombre | Uso | Tiempo Max en Cola |
|-------|--------|-----|-------------------|
| 1 | `critical` | Emergencias | 0s (inmediato) |
| 2 | `urgent` | Pedidos listos | 5s |
| 3 | `high` | Promociones hot | 30s |
| 4 | `normal` | Mensajes generales | 2min |
| 5 | `low` | Informativos | Sin límite |

**Implementación:**
```python
# Backend - Modelo
class AudioMetadata(Base):
    priority = Column(Integer, default=4)  # 1-5
    created_at = Column(DateTime)

    @property
    def effective_priority(self):
        # Aumentar prioridad si lleva mucho tiempo esperando
        age_seconds = (datetime.now() - self.created_at).seconds

        if age_seconds > 300:  # 5 minutos
            return max(1, self.priority - 1)

        return self.priority

# Query ordenada por prioridad
pending = db.query(AudioMetadata)\
    .filter(status='pending')\
    .order_by(AudioMetadata.priority.asc(), AudioMetadata.created_at.asc())\
    .first()
```

---

### **Mejora 4: Sistema de Jingles Dinámicos** ⭐

**Problema:** TTS suena seco sin identidad de marca.

**Solución:** Intro/outro automáticos según categoría

**Ejemplo:**
```
[Jingle intro 2s] → "Atención: Pedido #42 listo" → [Jingle outro 1s]
```

**Configuración:**
```json
// jingle-config.json
{
  "categories": {
    "pedidos": {
      "intro": "jingles/pedido_intro.mp3",
      "outro": "jingles/pedido_outro.mp3"
    },
    "promociones": {
      "intro": "jingles/promo_intro.mp3",
      "outro": "jingles/promo_outro.mp3"
    },
    "default": {
      "intro": "jingles/generic_intro.mp3",
      "outro": null
    }
  }
}
```

**Implementación (Backend):**
```python
# backend/app/services/jingle_service.py
async def create_tts_with_jingles(text: str, category: str):
    # 1. Generar TTS
    tts_file = await tts_service.generate(text)

    # 2. Obtener jingles según categoría
    config = load_jingle_config()
    intro = config['categories'][category]['intro']
    outro = config['categories'][category]['outro']

    # 3. Mezclar con pydub
    from pydub import AudioSegment

    final = AudioSegment.empty()

    if intro:
        final += AudioSegment.from_file(intro)

    final += AudioSegment.from_file(tts_file)

    if outro:
        final += AudioSegment.from_file(outro)

    # 4. Exportar
    output = f"storage/audio/tts_with_jingle_{id}.mp3"
    final.export(output, format="mp3")

    return output
```

---

### **Mejora 5: Heartbeat y Monitoreo** ⭐

**Problema:** No se sabe si el player está activo.

**Solución:** Sistema de heartbeat cada 30s

**En el player:**
```python
# Enviar heartbeat cada 30s
async def send_heartbeat():
    while True:
        await websocket.send_json({
            'type': 'heartbeat',
            'timestamp': datetime.now().isoformat(),
            'status': {
                'is_playing': music_player.is_playing,
                'current_track': music_player.current_track,
                'music_volume': volumes['music'],
                'queue_size': tts_queue.size()
            }
        })
        await asyncio.sleep(30)
```

**En el backend:**
```python
# Modelo
class PlayerStatus(Base):
    last_heartbeat = Column(DateTime)
    is_online = Column(Boolean)
    current_track = Column(String)
    queue_size = Column(Integer)

# Check si está offline
@property
def is_online(self):
    if not self.last_heartbeat:
        return False

    age = (datetime.now() - self.last_heartbeat).seconds
    return age < 60  # Offline si >1min sin heartbeat
```

**Dashboard muestra:**
```
Player Status: 🟢 Online (última actualización hace 12s)
Cola actual: 3 mensajes
Track actual: "Cool Jazz - Track 05"
Volumen música: 30%
```

---

### **Mejora 6: Playlist Inteligente** ⭐

**Estado actual:** Música en loop simple (30 tracks random)

**Propuesta:** Playlist con reglas

**Features:**
- ✅ Evitar repetir mismo track en <30min
- ✅ Géneros según hora del día (mañana: energética, noche: suave)
- ✅ Fades entre tracks
- ✅ Normalización de volumen entre tracks

**Implementación:**
```python
class IntelligentPlaylist:
    def __init__(self):
        self.history = []  # Últimos 20 tracks
        self.rules = load_playlist_rules()

    def get_next_track(self):
        current_hour = datetime.now().hour

        # Filtrar según hora
        if 6 <= current_hour < 12:
            genre = 'energetic'
        elif 12 <= current_hour < 18:
            genre = 'upbeat'
        else:
            genre = 'smooth'

        # Filtrar por género y que no esté en history
        candidates = [
            t for t in self.tracks
            if t.genre == genre and t not in self.history[-20:]
        ]

        # Seleccionar random
        track = random.choice(candidates)
        self.history.append(track)

        return track
```

---

### **Mejora 7: Analytics y Estadísticas** ⭐

**Datos a trackear:**
- Total de TTS reproducidos por día/hora
- Tiempo promedio de entrega (creación → reproducción)
- Categorías más usadas
- Horarios pico
- Uptime del player

**Dashboard:**
```
📊 Estadísticas Hoy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TTS reproducidos:        47
Promedio entrega:        3.2s
Player uptime:           99.8%
Categoría top:           Pedidos (23)

📈 Gráfico de uso por hora
[Gráfico de barras]
```

---

## 🔧 Integración con MediaFlowDemo v2

### **Arquitectura Propuesta (Mejorada)**

```
┌─────────────────────────────────────────────────────────┐
│  VPS - MediaFlowDemo v2 (FastAPI + Vue 3)               │
│                                                         │
│  ┌────────────────────────────────────────────┐        │
│  │ WebSocket Server                           │        │
│  │ ws://vps:8000/ws/player                    │        │
│  │ - Conexión permanente con player           │        │
│  │ - Push de TTS instantáneo                  │        │
│  │ - Recepción de heartbeats                  │        │
│  └────────────────────────────────────────────┘        │
│                                                         │
│  ┌────────────────────────────────────────────┐        │
│  │ PlayerService (Python)                     │        │
│  │ - Gestión de cola de TTS                   │        │
│  │ - Prioridades inteligentes                 │        │
│  │ - Sistema de jingles                       │        │
│  │ - Monitoreo y analytics                    │        │
│  └────────────────────────────────────────────┘        │
│                                                         │
│  ┌────────────────────────────────────────────┐        │
│  │ Dashboard (Vue 3 + Tailwind)               │        │
│  │ - Status del player en tiempo real         │        │
│  │ - Crear TTS con jingles                    │        │
│  │ - Ver cola actual                          │        │
│  │ - Analytics y gráficos                     │        │
│  └────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ WebSocket bidireccional
                         │
┌────────────────────────┴─────────────────────────────────┐
│  Mac Mini - Player Local (Python)                        │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ WebSocket Client                            │        │
│  │ - Conexión permanente al VPS                │        │
│  │ - Envía heartbeats cada 30s                 │        │
│  │ - Recibe TTS push                           │        │
│  └─────────────────────────────────────────────┘        │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ TTSQueue (mejorado)                         │        │
│  │ - Cola local con prioridades                │        │
│  │ - Procesamiento secuencial                  │        │
│  │ - Retry automático                          │        │
│  └─────────────────────────────────────────────┘        │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ JingleEngine (nuevo)                        │        │
│  │ - Intro/outro automático                    │        │
│  │ - Mezcla con pydub                          │        │
│  └─────────────────────────────────────────────┘        │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ IntelligentPlaylist (mejorado)              │        │
│  │ - Música según hora del día                 │        │
│  │ - Sin repeticiones cercanas                 │        │
│  │ - Normalización de volumen                  │        │
│  └─────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

---

## 📋 Checklist de Implementación

### **Fase 1: Mantener Compatibilidad (Semana 1)**
- [ ] Implementar endpoints HTTP actuales (GET/POST)
- [ ] Modelo de BD compatible
- [ ] Probar con player sin modificar

### **Fase 2: Mejoras Incrementales (Semana 2-3)**
- [ ] WebSocket server en FastAPI
- [ ] Sistema de prioridades mejorado
- [ ] Heartbeat y monitoreo
- [ ] Dashboard con status en vivo

### **Fase 3: Features Avanzados (Semana 4-5)**
- [ ] Sistema de jingles dinámicos
- [ ] Cola local en player (actualizar player.py)
- [ ] Analytics y estadísticas
- [ ] Playlist inteligente

### **Fase 4: Optimización (Semana 6)**
- [ ] Performance tuning
- [ ] Testing E2E
- [ ] Documentación de usuario

---

## 🎯 Resumen Ejecutivo

### **Estado Actual:**
- ✅ Player básico funcional
- ⚠️ Sistema ineficiente (polling)
- ⚠️ Sin cola, prioridades, jingles, monitoreo

### **Propuesta MediaFlowDemo v2:**
- ✅ WebSocket bidireccional (0s delay)
- ✅ Cola local en player (no se pierden mensajes)
- ✅ Prioridades inteligentes (5 niveles)
- ✅ Jingles automáticos por categoría
- ✅ Heartbeat y monitoreo 24/7
- ✅ Analytics y estadísticas
- ✅ Playlist inteligente

### **Beneficios:**
- 📈 **99% reducción** de requests HTTP
- ⚡ **Entrega instantánea** (0s vs 2s)
- 🎯 **0% mensajes perdidos** (con cola local)
- 📊 **Visibilidad total** del sistema
- 🎵 **Mejor experiencia** (jingles + playlist inteligente)

---

## 📞 Próximos Pasos

1. **Revisar este documento** y aprobar mejoras propuestas
2. **Priorizar features** (cuáles implementar primero)
3. **Actualizar ARCHITECTURE.md** con decisiones finales
4. **Definir roadmap** en base a prioridades

**¿Qué mejoras quieres implementar primero?**

