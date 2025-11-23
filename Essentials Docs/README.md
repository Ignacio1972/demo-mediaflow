# 🎵 MediaFlowDemo v2.1

Sistema de Radio Automatizada con TTS e IA - Arquitectura Moderna

## 📋 Stack Tecnológico

### Backend
- **FastAPI** 0.104+ - Framework web async
- **SQLAlchemy** 2.0+ - ORM con soporte async
- **SQLite** - Base de datos (desarrollo)
- **Pydantic** 2.5+ - Validación de datos
- **Python** 3.11+

### Frontend
- **Vue 3** - Framework UI
- **TypeScript** - Type safety
- **Tailwind CSS** + **DaisyUI** - Styling
- **Pinia** - State management
- **Vite** - Build tool

### APIs Externas
- **ElevenLabs** - Text-to-Speech
- **Claude AI** (Anthropic) - IA para sugerencias

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.11+
- Node.js 18+
- npm o yarn

### 1. Backend Setup

```bash
cd backend

# Ejecutar script de desarrollo (recomendado)
./run_dev.sh

# O manualmente:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

El backend estará disponible en:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 2. Frontend Setup

```bash
cd frontend

# Ejecutar script de desarrollo (recomendado)
./run_dev.sh

# O manualmente:
npm install
npm run dev
```

El frontend estará disponible en:
- **App**: http://localhost:5173

---

## 📁 Estructura del Proyecto

```
mediaflow-v2/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Endpoints API
│   │   ├── core/                # Config y settings
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── db/                  # Database config
│   │   └── main.py              # FastAPI app
│   ├── alembic/                 # Database migrations
│   ├── storage/                 # File storage
│   ├── tests/                   # Backend tests
│   ├── requirements.txt
│   ├── .env                     # Environment variables
│   └── run_dev.sh               # Dev script
│
└── frontend/
    ├── src/
    │   ├── api/                 # API clients
    │   ├── components/          # Vue components
    │   │   ├── dashboard/
    │   │   ├── library/
    │   │   ├── calendar/
    │   │   └── settings/
    │   ├── composables/         # Composition API
    │   ├── stores/              # Pinia stores
    │   ├── types/               # TypeScript types
    │   ├── router/              # Vue Router
    │   └── main.ts
    ├── public/
    ├── package.json
    └── run_dev.sh               # Dev script
```

---

## 🔧 Configuración

### Variables de Entorno (Backend)

Edita `backend/.env` y configura tus API keys:

```env
# ElevenLabs API
ELEVENLABS_API_KEY=tu_api_key_aqui

# Claude AI (Anthropic)
ANTHROPIC_API_KEY=tu_api_key_aqui
```

### Base de Datos

El proyecto usa **SQLite** para desarrollo. No requiere configuración adicional.

Para migrar a PostgreSQL en producción, cambia `DATABASE_URL` en `.env`

---

## 🎯 Características Principales v2.1

### ✨ Nuevas en v2.1

1. **Voice Settings Automáticos**
   - Configuración individual por voz (style, stability, similarity)
   - Volume adjustment por voz (-20 to +20 dB)
   - Settings aplicados automáticamente en Dashboard

2. **Categorías Dinámicas**
   - Totalmente personalizables (nombre, color, icono)
   - Se asignan en Library, no en Dashboard

3. **Favoritos Cross-Category**
   - Marca favoritos sin importar la categoría
   - Filtro especial "⭐ Favoritos"

4. **Vista Dual en Library**
   - Vista Grid (cards)
   - Vista Lista (tabla)

5. **Dashboard Simplificado**
   - Sin selector de categoría
   - Mensajes recientes siempre visibles
   - Generación más rápida

### 🔥 Características Core

- **Multi-Cliente con IA**: Contextos personalizados por cliente
- **TTS Profesional**: ElevenLabs con normalización LUFS
- **Jingles Dinámicos**: Intro/outro automáticos
- **WebSocket**: Comunicación bidireccional con player
- **Programación**: Sistema de scheduling avanzado
- **Modo Automático**: Speech-to-Text → IA → TTS

---

## 📚 Módulos del Sistema

### 1. Dashboard
- Generación rápida de mensajes TTS
- Selector de voz con settings automáticos
- Sugerencias con Claude AI
- Mensajes recientes

### 2. Library
- Biblioteca de audios generados
- Búsqueda y filtros avanzados
- Sistema de favoritos
- Vista Grid + Lista
- Categorización posterior
- "Editar en Dashboard" (copia)

### 3. Calendar
- Programación de mensajes
- Vista de calendario interactiva
- Tipos: interval, specific, once
- Prioridades

### 4. Settings/Playground
- **AI**: Multi-cliente con contextos
- **Voices**: Biblioteca de voces con settings individuales ⭐
- **Audio**: Control granular de volúmenes
- **Automatic**: Modo Speech-to-Text

---

## 🗄️ Modelos de Base de Datos (v2.1)

### VoiceSettings
Configuración individual por voz con settings automáticos

```python
- id: string (PK)
- name: string
- elevenlabs_id: string
- active: boolean
- style: float (0-100)
- stability: float (0-100)
- similarity_boost: float (0-100)
- volume_adjustment: float (dB)
- jingle_settings: JSON
```

### Category
Categorías totalmente configurables

```python
- id: string (PK)
- name: string
- icon: string
- color: string
- order: int
- active: boolean
```

### AudioMessage
Mensajes de audio con favoritos

```python
- id: int (PK)
- filename: string
- display_name: string
- original_text: text
- voice_id: string (FK)
- category_id: string (FK, nullable)
- is_favorite: boolean ⭐ NEW
- has_jingle: boolean
- priority: int
```

### Schedule
Programación de reproducción

```python
- id: int (PK)
- schedule_type: string
- audio_message_id: int (FK, nullable)
- text_to_generate: text (nullable)
- start_date: datetime
- interval_minutes: int
- active: boolean
```

---

## 🛠️ Comandos Útiles

### Backend

```bash
# Crear nueva migración
cd backend
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Tests
pytest tests/ -v

# Coverage
pytest --cov=app tests/
```

### Frontend

```bash
# Desarrollo
npm run dev

# Build producción
npm run build

# Preview build
npm run preview

# Lint
npm run lint

# Tests
npm run test:unit
```

---

## 📖 Roadmap de Desarrollo

- **Semana 1**: ✅ Foundation + Dashboard simplificado
- **Semana 2**: Player Integration + Audio con settings
- **Semana 3**: Library con favoritos y vista dual
- **Semana 4**: Calendar & Scheduling
- **Semana 5**: Settings/Playground (CRÍTICO)
- **Semana 6**: Testing & Deployment

---

## 🐛 Troubleshooting

### Backend no inicia

```bash
# Verificar que el venv esté activado
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall

# Verificar variables de entorno
cat .env
```

### Frontend no inicia

```bash
# Limpiar node_modules y reinstalar
rm -rf node_modules package-lock.json
npm install

# Limpiar caché de Vite
rm -rf .vite
```

### Error de migraciones

```bash
# Eliminar DB y recrear
rm mediaflow.db
alembic upgrade head
```

---

## 📞 Soporte

Para más información consulta:
- **Executive Summary**: `EXECUTIVE-SUMMARY.md`
- **Arquitectura**: `02-ARCHITECTURE-v2.1.md`
- **Roadmap**: `03-ROADMAP-v2.1.md`
- **Implementation Guide**: `04-IMPLEMENTATION-GUIDE.md`

---

## ⚡ Próximos Pasos

1. ✅ Configurar API keys en `backend/.env`
2. ✅ Iniciar backend: `cd backend && ./run_dev.sh`
3. ✅ Iniciar frontend: `cd frontend && ./run_dev.sh`
4. 🎯 Abrir http://localhost:5173
5. 🚀 ¡Comenzar a desarrollar!

---

**Versión**: 2.1.0
**Estado**: Setup Completo
**Fecha**: 2025-11-22

🎵 ¡Listo para comenzar el desarrollo!
