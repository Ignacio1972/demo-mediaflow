"""
Chat assistant tool definitions for Claude tool_use.
"""

CHAT_TOOLS = [
    {
        "name": "generate_text_suggestions",
        "description": "Genera 2-3 sugerencias de texto para un anuncio de audio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "Qué se quiere anunciar"},
                "tone": {
                    "type": "string",
                    "enum": ["profesional", "entusiasta", "amigable", "urgente", "informativo"],
                    "description": "Tono del mensaje"
                },
                "duration": {"type": "integer", "description": "Duración objetivo en segundos (5-30)", "default": 10}
            },
            "required": ["context"]
        }
    },
    {
        "name": "generate_audio",
        "description": "Genera audio TTS a partir de un texto confirmado por el usuario.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto a convertir en audio"},
                "voice_id": {"type": "string", "description": "ID de la voz (si no se especifica, usa la default)"},
                "add_jingles": {"type": "boolean", "description": "Si agregar música de fondo", "default": False},
                "music_file": {"type": "string", "description": "Archivo de música de fondo (opcional)"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "list_voices",
        "description": "Lista las voces disponibles para generar audio.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "list_music_tracks",
        "description": "Lista las pistas de música de fondo disponibles.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "save_to_library",
        "description": "Guarda un audio generado en la biblioteca permanente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_id": {"type": "integer", "description": "ID del audio a guardar"},
                "display_name": {"type": "string", "description": "Nombre para la biblioteca (opcional)"},
                "category_id": {"type": "string", "description": "ID de categoría (opcional)"}
            },
            "required": ["audio_id"]
        }
    },
    {
        "name": "create_schedule",
        "description": "Programa un audio para reproducción automática.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_id": {"type": "integer", "description": "ID del audio"},
                "schedule_type": {
                    "type": "string",
                    "enum": ["interval", "specific", "once"],
                    "description": "interval=cada X tiempo, specific=horarios fijos, once=una vez"
                },
                "interval_minutes": {"type": "integer", "description": "Minutos entre repeticiones (tipo interval)"},
                "specific_times": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Horarios HH:MM (tipo specific). Ej: ['09:00', '12:00']"
                },
                "days_of_week": {
                    "type": "array", "items": {"type": "integer"},
                    "description": "Días 0-6 (lunes=0). Para tipo specific."
                },
                "start_date": {"type": "string", "description": "Fecha inicio ISO. Para tipo 'once', es la fecha/hora de ejecución."},
                "end_date": {"type": "string", "description": "Fecha fin ISO (opcional)"}
            },
            "required": ["audio_id", "schedule_type"]
        }
    },
    {
        "name": "list_schedules",
        "description": "Lista las programaciones activas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "active_only": {"type": "boolean", "description": "Solo activas", "default": True}
            },
            "required": []
        }
    },
    {
        "name": "list_categories",
        "description": "Lista las categorías disponibles para organizar audios.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "search_library",
        "description": "Busca audios guardados en la biblioteca.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto de búsqueda"},
                "category_id": {"type": "string", "description": "Filtrar por categoría"},
                "limit": {"type": "integer", "description": "Máximo resultados", "default": 10}
            },
            "required": []
        }
    },
    {
        "name": "send_to_radio",
        "description": "Envía un audio a la radio para reproducción inmediata.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_id": {"type": "integer", "description": "ID del audio"}
            },
            "required": ["audio_id"]
        }
    }
]
