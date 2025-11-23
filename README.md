# 🎵 MediaFlow v2.1 - Modern TTS System

Sistema moderno de Text-to-Speech (TTS) con integración de IA para generar mensajes de audio profesionales.

## ✨ Características Principales

- 🤖 **Sugerencias con IA**: Claude AI genera múltiples variaciones de mensajes
- 🎙️ **Síntesis de Voz**: Integración con ElevenLabs para voces naturales
- 🎵 **Mezcla de Audio**: Añade música de fondo automáticamente
- 📚 **Biblioteca de Audio**: Gestiona y organiza tus mensajes generados
- 🎨 **Interfaz Moderna**: Dashboard intuitivo con Vue 3 y Tailwind CSS
- ⚡ **Arquitectura Asíncrona**: FastAPI backend de alto rendimiento

## 🛠️ Stack Tecnológico

### Frontend
- **Vue 3** + TypeScript
- **Tailwind CSS** + DaisyUI
- **Pinia** para state management
- **Vite** como build tool

### Backend
- **Python 3.10** + FastAPI
- **SQLAlchemy** ORM
- **Alembic** para migraciones
- **Anthropic Claude** para IA
- **ElevenLabs** para TTS
- **FFmpeg** para procesamiento de audio

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.10+
- Node.js 18+
- FFmpeg instalado
- Cuentas en:
  - [Anthropic](https://www.anthropic.com/) (Claude API)
  - [ElevenLabs](https://elevenlabs.io/) (TTS API)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/Ignacio1972/demo-mediaflow.git
cd demo-mediaflow
```

2. **Configurar Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus API keys
```

4. **Inicializar base de datos**
```bash
alembic upgrade head
python app/db/seed_voices.py
```

5. **Configurar Frontend**
```bash
cd ../frontend
npm install
```

### Ejecutar en Desarrollo

**Terminal 1 - Backend:**
```bash
cd backend
./run_dev.sh
# O manualmente: uvicorn app.main:app --reload --port 3001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
./run_dev.sh
# O manualmente: npm run dev
```

Accede a: http://localhost:5173

## 📁 Estructura del Proyecto

```
mediaflow-v2/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoints de la API
│   │   ├── models/          # Modelos de base de datos
│   │   ├── schemas/         # Esquemas Pydantic
│   │   ├── services/        # Lógica de negocio
│   │   └── main.py          # Punto de entrada
│   ├── storage/
│   │   ├── audio/           # Archivos de audio generados
│   │   └── music/           # Música de fondo
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/      # Componentes Vue
    │   ├── stores/          # Estado global (Pinia)
    │   ├── router/          # Rutas
    │   └── types/           # Tipos TypeScript
    └── package.json
```

## 🎯 Uso

1. **Generar con IA**: Describe qué necesitas anunciar
2. **Seleccionar Opciones**: Elige música y voz
3. **Generar Audio**: Crea el mensaje TTS
4. **Gestionar**: Accede a tu biblioteca de audios

## 📝 Variables de Entorno

```env
# Backend (.env)
ELEVENLABS_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-20250514
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado. Todos los derechos reservados.

## 🙏 Agradecimientos

- **Claude AI** por las sugerencias inteligentes
- **ElevenLabs** por la síntesis de voz de alta calidad
- **FFmpeg** por el procesamiento de audio

---

**Desarrollado con ❤️ usando Claude Code**
