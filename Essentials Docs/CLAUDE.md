# 🤖 Claude.md - Contexto del Proyecto MediaFlowDemo v2.1

**Fecha Creación**: 2025-11-22
**Última Actualización**: 2025-11-22
**Propósito**: Documentación para Claude en futuras sesiones

---

## 📋 Resumen del Proyecto

**MediaFlowDemo v2.1** es un sistema de radio automatizada con TTS (Text-to-Speech) e IA que permite generar mensajes de audio profesionales con voces personalizadas y reproducirlos en un player local 24/7.

**Stack Tecnológico**:
- **Backend**: FastAPI + SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Vue 3 + TypeScript + Tailwind CSS + DaisyUI
- **APIs Externas**: ElevenLabs (TTS) + Claude AI (Anthropic)

**Arquitectura**: v2.1 con voice settings automáticos y categorías dinámicas

---

## 🎯 Filosofía de Diseño v2.1 (CRÍTICO)

### Cambio Fundamental vs v1.0

```
Dashboard → Generar (simple, rápido, SIN categorías)
Library   → Categorizar (después, flexible)
Playground → Configurar (una vez, automático para siempre)
```

### Características Clave v2.1

1. **Voice Settings Automáticos** ⭐ **IMPLEMENTADO**
   - Cada voz tiene configuración individual (style, stability, similarity)
   - Se aplican AUTOMÁTICAMENTE al generar
   - Usuario NO configura manualmente en Dashboard
   - Todo se gestiona desde Playground

2. **Categorías Dinámicas** ⭐ **MODELO LISTO**
   - Totalmente personalizables (nombre, color, icono)
   - Se asignan en Library, NO en Dashboard
   - Dashboard está simplificado para rapidez

3. **Favoritos Cross-Category** ⭐ **MODELO LISTO**
   - Campo `is_favorite` en AudioMessage
   - Filtro especial que cruza todas las categorías

4. **Vista Dual en Library** ⭐ **PENDIENTE**
   - Grid (cards) + Lista (tabla)
   - Usuario elige su preferencia

5. **Dashboard Simplificado** ⭐ **LANDING LISTO**
   - SIN selector de categoría
   - Mensajes recientes siempre visibles
   - Generación rápida

---

## 🏗️ Estado Actual del Proyecto

**Progreso General**: ~25% (Semana 1, Día 3-4)
**Última Actividad**: 2025-11-22 19:31 (archivos de prueba generados)

### ✅ Backend (FUNCIONANDO - Puerto 3001)

**Implementado**:
- ✅ FastAPI app con CORS configurado
- ✅ 6 Modelos SQLAlchemy v2.1 completos
  - VoiceSettings (con campos individuales)
  - Category (totalmente configurable)
  - AudioMessage (con is_favorite)
  - Schedule, PlayerStatus, ClientConfig
- ✅ Base de datos SQLite operativa (68KB)
- ✅ Alembic migrations configurado
- ✅ 4 Endpoints API funcionando:
  - POST /api/v1/audio/generate ⭐ FUNCIONAL
  - GET /api/v1/audio/voices
  - GET /api/v1/audio/voices/{id}
  - GET /api/v1/audio/recent
- ✅ ElevenLabsService completo (cliente async)
- ✅ VoiceManager con auto-aplicación de settings ⭐ CRÍTICO
- ✅ Storage de archivos (2 MP3 de prueba generados)

**Pendiente Backend Semana 1**:
- ❌ Claude AI service
- ❌ Audio processing (LUFS, jingles)
- ❌ Endpoint /api/v1/ai/suggest
- ❌ Seed de voces iniciales
- ❌ Testing (pytest)

### ✅ Frontend (FUNCIONANDO - Puerto 5173)

**Implementado**:
- ✅ Vue 3 + TypeScript + Composition API
- ✅ Tailwind CSS + DaisyUI (tema personalizado)
- ✅ Vue Router configurado (4 rutas)
- ✅ TypeScript types definidos (Voice, AudioMessage, Category)
- ✅ Dashboard landing page funcional
- ✅ ThemeSelector component

**Pendiente Frontend Semana 1** ⚠️ CRÍTICO:
- ❌ API client (axios wrapper) ← EN PROGRESO
- ❌ Pinia store (audio state)
- ❌ MessageGenerator.vue (textarea + controls)
- ❌ VoiceSelector.vue (fetch + display voces)
- ❌ AudioPreview.vue (player)
- ❌ RecentMessages.vue (display mensajes)
- ❌ AISuggestions.vue
- ❌ JingleControls.vue

---

## 📁 Estructura de Archivos (Importante)

### Backend Key Files

```
backend/
├── app/
│   ├── main.py                          # ✅ FastAPI app
│   ├── core/config.py                   # ✅ Settings
│   ├── models/
│   │   ├── voice_settings.py           # ⭐ Voice settings individuales
│   │   ├── category.py                 # ⭐ Categorías dinámicas
│   │   ├── audio.py                    # ⭐ Con is_favorite
│   │   └── ...
│   ├── api/v1/endpoints/
│   │   └── audio.py                    # ✅ 4 endpoints funcionando
│   ├── services/
│   │   ├── tts/
│   │   │   ├── elevenlabs.py          # ✅ Cliente TTS
│   │   │   └── voice_manager.py       # ⭐ Auto-settings (276 líneas)
│   │   ├── ai/                         # ❌ PENDIENTE
│   │   ├── audio/                      # ❌ PENDIENTE
│   │   └── player/                     # ❌ PENDIENTE
│   └── schemas/audio.py                # ✅ Pydantic schemas
├── storage/audio/                       # ✅ 2 archivos MP3
└── mediaflow.db                         # ✅ SQLite (68KB)
```

### Frontend Key Files

```
frontend/
├── src/
│   ├── main.ts                         # ✅ Entry point
│   ├── App.vue                         # ✅ Root
│   ├── router/index.ts                 # ✅ Router
│   ├── types/
│   │   ├── audio.ts                    # ✅ Types definidos
│   │   └── api.ts                      # ✅ API types
│   ├── api/                            # ❌ PENDIENTE (en progreso)
│   │   ├── client.ts
│   │   └── audio.ts
│   ├── stores/                         # ❌ PENDIENTE
│   │   └── audio.ts
│   └── components/
│       ├── dashboard/
│       │   └── Dashboard.vue           # ✅ Landing page
│       ├── library/Library.vue         # ⚠️ Placeholder
│       ├── calendar/Calendar.vue       # ⚠️ Placeholder
│       └── settings/                   # ⚠️ Placeholders
```

---

## 🔑 Conceptos Clave para Entender el Sistema

### 1. Voice Settings Automáticos (v2.1) ⭐

**Problema que resuelve**: En v1.0, usuario tenía que configurar manualmente style, stability, similarity en cada generación → fricción.

**Solución v2.1**:
```python
# Cada voz tiene settings predefinidos
VoiceSettings:
  - style: 15.0           # 0-100 (15 = formal, 50 = casual)
  - stability: 100.0      # 0-100 (100 = consistente)
  - similarity_boost: 40.0
  - volume_adjustment: 0.0  # dB (-20 to +20)
  - jingle_settings: {...}

# VoiceManager aplica automáticamente
voice_manager.generate_with_voice(text, voice_id)
  → Lee settings de la voz
  → Llama ElevenLabs con esos settings
  → Aplica volume_adjustment
  → Retorna audio procesado
```

**Flujo Usuario**:
1. Admin configura voces UNA VEZ en Playground
2. Usuario en Dashboard solo elige voz
3. Settings se aplican automáticamente
4. Zero fricción

### 2. Categorías Solo en Library (v2.1)

**Cambio Fundamental**:
- v1.0: Dashboard tenía selector de categoría
- v2.1: Dashboard NO tiene categorías

**Razón**:
```
Flujo Natural:
1. Usuario genera mensaje rápido (Dashboard)
2. Escucha preview
3. Si gusta → "Guardar en Library"
4. EN LIBRARY asigna categoría
5. Puede cambiar categoría después

vs Flujo Malo (v1.0):
1. Usuario debe decidir categoría ANTES
2. Genera
3. Si se equivocó de categoría → problema
```

### 3. Modelo de Datos v2.1

```python
# VoiceSettings - Configuración individual por voz
{
  "id": "juan_carlos",
  "name": "Juan Carlos",
  "elevenlabs_id": "G4IAP30yc6c1gK0csDfu",
  "active": true,
  "style": 15.0,                    # Individual por voz
  "stability": 100.0,               # Individual por voz
  "similarity_boost": 40.0,         # Individual por voz
  "volume_adjustment": 0.0,         # dB adjustment
  "jingle_settings": {              # Individual por voz
    "music_volume": 1.65,
    "voice_volume": 2.8,
    "duck_level": 0.95
  }
}

# Category - Totalmente personalizable
{
  "id": "pedidos",
  "name": "Pedidos Listos",         # Editable
  "icon": "📦",                     # Editable (emoji)
  "color": "#FF4444",               # Editable (hex)
  "order": 1,
  "active": true
}

# AudioMessage - Con favoritos
{
  "id": 1,
  "filename": "tts_20251122_193056_juan_carlos.mp3",
  "original_text": "Pedido 42 listo",
  "voice_id": "juan_carlos",
  "category_id": null,              # Nullable! Se asigna después
  "is_favorite": false,             # NEW v2.1
  "has_jingle": false,
  "priority": 4
}
```

---

## 🚀 Roadmap y Prioridades

### Semana 1 (Actual): Foundation & Dashboard
**Días 1-2**: ✅ COMPLETO (Setup + Backend)
**Días 3-5**: 🟡 EN CURSO (Frontend + Claude AI)

**Prioridad INMEDIATA** (Siguiente 24-48h):
1. ✅ API client (client.ts + audio.ts) ← HECHO
2. ⏳ Pinia store (audio.ts) ← EN PROGRESO
3. ⏳ VoiceSelector.vue
4. ⏳ MessageGenerator.vue
5. ⏳ AudioPreview.vue
6. ⏳ RecentMessages.vue
7. ⏳ Integrar en Dashboard.vue
8. ⏳ Seed de voces
9. ⏳ Claude AI básico

### Semana 2: Player Integration
- WebSocket server/client
- Audio processing (LUFS, jingles)
- Player endpoints

### Semana 3: Library Module
- CRUD completo
- Vista dual (Grid + List)
- Favoritos
- Edit in Dashboard

### Semana 4: Calendar
### Semana 5: Settings/Playground ⭐ CRÍTICO
### Semana 6: Testing & Deploy

---

## ⚠️ Puntos Críticos a Recordar

### 1. NO Agregar Categorías al Dashboard
```vue
<!-- ❌ MAL - No hacer esto -->
<CategorySelector v-model="category" />

<!-- ✅ BIEN - Dashboard solo voz -->
<VoiceSelector v-model="voice" />
```

### 2. Voice Settings SON Automáticos
```typescript
// ❌ MAL - Usuario no configura
interface GenerateRequest {
  text: string
  voice_id: string
  voice_settings: {...}  // ← NO
}

// ✅ BIEN - Solo voice_id
interface GenerateRequest {
  text: string
  voice_id: string  // ← Settings vienen de DB
}
```

### 3. Mensajes Recientes SIEMPRE Visibles
```vue
<!-- Dashboard.vue debe mostrar siempre -->
<RecentMessages :messages="recent" />
```

### 4. Favoritos Cross-Category
```sql
-- ❌ MAL - Favoritos por categoría
SELECT * FROM audio_messages
WHERE category_id = 'pedidos' AND is_favorite = true

-- ✅ BIEN - Favoritos de todas las categorías
SELECT * FROM audio_messages
WHERE is_favorite = true
```

---

## 🐛 Troubleshooting Común

### Backend no responde
```bash
# Verificar proceso
ps aux | grep uvicorn

# Reiniciar
cd /var/www/mediaflow-v2/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

### Frontend no carga
```bash
# Verificar proceso
ps aux | grep vite

# Reiniciar
cd /var/www/mediaflow-v2/frontend
npm run dev
```

### Error de CORS
```python
# backend/app/main.py
# Verificar que CORS_ORIGINS incluye http://localhost:5173
```

### Base de datos corrupta
```bash
cd /var/www/mediaflow-v2/backend
rm mediaflow.db
alembic upgrade head
```

---

## 📞 Comandos Útiles

### Backend
```bash
# Activar venv
source venv/bin/activate

# Instalar deps
pip install -r requirements.txt

# Migración
alembic upgrade head
alembic revision --autogenerate -m "descripción"

# Run
uvicorn app.main:app --reload --port 3001

# Tests
pytest tests/ -v
pytest --cov=app tests/
```

### Frontend
```bash
# Instalar
npm install

# Dev
npm run dev

# Build
npm run build

# Lint
npm run lint

# Tests
npm run test:unit
```

---

## 📚 Documentación de Referencia

**Archivos de Documentación**:
- `EXECUTIVE-SUMMARY.md` - Resumen ejecutivo del proyecto
- `01-PLAYER-INTEGRATION.md` - Integración con player local
- `02-ARCHITECTURE-v2.1.md` - ⭐ Arquitectura actualizada v2.1
- `03-ROADMAP-v2.1.md` - Roadmap de 6 semanas
- `04-IMPLEMENTATION-GUIDE.md` - Ejemplos de código
- `PLAYGROUND-ANALYSIS.md` - Análisis del playground actual
- `README.md` - Guía de inicio rápido
- `SETUP-COMPLETE.md` - Estado del setup

**URLs Importantes**:
- Backend API: http://localhost:3001
- API Docs: http://localhost:3001/api/docs
- Frontend: http://localhost:5173

---

## 🎯 Objetivos de Cada Semana

| Semana | Objetivo | Entregable |
|--------|----------|------------|
| 1 | Foundation + Dashboard | Dashboard funcional generando TTS |
| 2 | Player Integration | WebSocket + Audio processing |
| 3 | Library Module | Biblioteca con favoritos y vista dual |
| 4 | Calendar | Programación automática |
| 5 | Settings/Playground | Control total de configuración ⭐ |
| 6 | Testing + Deploy | Production ready (75%+ coverage) |

---

## 💡 Notas Importantes para Claude

1. **Siempre lee 02-ARCHITECTURE-v2.1.md** antes de implementar features
2. **Voice settings son automáticos** - no pedir al usuario configurarlos
3. **Dashboard simple** - sin categorías, sin configuraciones complejas
4. **Library poderosa** - aquí va la categorización y organización
5. **Playground profesional** - configuración una vez, uso automático
6. **Testing es crítico** - objetivo 75%+ coverage
7. **TypeScript estricto** - 100% type-safe
8. **Async/await everywhere** - todo el backend es async

---

## 🔄 Estado Actual de Tareas (2025-11-22)

**En Progreso**:
- ✅ API client (client.ts + audio.ts) - COMPLETADO
- ⏳ Pinia store (audio.ts) - INTERRUMPIDO
- ⏳ Frontend components (VoiceSelector, MessageGenerator, etc)

**Próximos Pasos**:
1. Completar Pinia store
2. VoiceSelector.vue
3. MessageGenerator.vue
4. AudioPreview.vue
5. RecentMessages.vue
6. Integrar en Dashboard
7. Seed de voces
8. Claude AI service

---

**Última actualización**: 2025-11-22
**Autor**: Claude (Anthropic)
**Versión**: 1.0
