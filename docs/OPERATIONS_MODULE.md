# Modulo Operaciones - Documentacion Tecnica

**Creado**: 2025-12-12
**Version**: 1.0
**Autor**: Claude AI

---

## 1. Vision General

El modulo **Operaciones** es una seccion del menu principal de MediaFlow v2 que contiene plantillas TTS especializadas para casos de uso operacionales. La primera plantilla implementada es **Vehiculos Mal Estacionados**.

### Proposito Principal

Generar anuncios de audio con **normalizacion automatica de texto** para garantizar pronunciacion correcta de:
- **Letras** (patentes): `BBCL` → `B. B. C. L.`
- **Numeros**: `45` → `cuarenta y cinco`

---

## 2. Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Vue 3)                            │
│  /operations/vehicles                                           │
├─────────────────────────────────────────────────────────────────┤
│  VehicleAnnouncement.vue                                        │
│  ├── VehicleForm.vue        (formulario)                        │
│  ├── PreviewText.vue        (vista previa normalizada)          │
│  └── AudioResult.vue        (reproductor + acciones)            │
│                                                                 │
│  useVehicleAnnouncement.ts  (estado + logica)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│  /api/v1/operations/vehicles/*                                  │
├─────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                     │
│  ├── GET  /options        → Opciones del formulario             │
│  ├── GET  /templates      → Plantillas disponibles              │
│  ├── POST /validate-plate → Validar patente                     │
│  ├── POST /preview        → Vista previa texto normalizado      │
│  └── POST /generate       → Generar audio TTS                   │
├─────────────────────────────────────────────────────────────────┤
│  Services:                                                      │
│  ├── TextNormalizer       → Normalizacion de texto              │
│  ├── VoiceManager         → Generacion TTS (ElevenLabs)         │
│  └── JingleService        → Mezcla con musica                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Estructura de Archivos

### 3.1 Backend

```
backend/app/
├── api/v1/endpoints/operations/
│   ├── __init__.py              # Router aggregator
│   └── vehicles.py              # Endpoints de vehiculos (230 lineas)
│
├── schemas/
│   └── operations.py            # Pydantic models (130 lineas)
│
└── services/text/
    ├── __init__.py              # Exports
    └── normalizer.py            # TextNormalizer (280 lineas)
```

### 3.2 Frontend

```
frontend/src/components/operations/
├── Operations.vue               # Container principal
├── OperationsNav.vue            # Navegacion interna (tabs)
│
└── vehicles/
    ├── VehicleAnnouncement.vue  # Pagina principal
    │
    ├── components/
    │   ├── VehicleForm.vue      # Formulario de entrada
    │   ├── PreviewText.vue      # Vista previa del texto
    │   └── AudioResult.vue      # Reproductor + botones
    │
    └── composables/
        └── useVehicleAnnouncement.ts  # Estado y logica (320 lineas)
```

---

## 4. Flujo de Datos

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Usuario     │     │  Frontend    │     │  Backend     │
│  ingresa     │────▶│  valida      │────▶│  normaliza   │
│  datos       │     │  en tiempo   │     │  texto       │
└──────────────┘     │  real        │     └──────┬───────┘
                     └──────────────┘            │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Usuario     │     │  Frontend    │     │  ElevenLabs  │
│  escucha     │◀────│  reproduce   │◀────│  genera      │
│  audio       │     │  audio       │     │  TTS         │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Flujo Detallado

1. **Usuario completa formulario** → marca, color, patente, voz, musica
2. **Frontend valida en tiempo real** → patente se valida con debounce (300ms)
3. **Preview automatico** → cada cambio dispara preview (500ms debounce)
4. **Usuario genera audio** → POST `/generate`
5. **Backend normaliza texto** → TextNormalizer procesa patente
6. **ElevenLabs genera TTS** → Con settings de la voz seleccionada
7. **Mezcla con musica** (opcional) → JingleService
8. **Guarda en BD** → AudioMessage
9. **Retorna audio URL** → Frontend reproduce automaticamente

---

## 5. Servicio de Normalizacion

### 5.1 Ubicacion
`backend/app/services/text/normalizer.py`

### 5.2 Clase Principal: TextNormalizer

```python
class TextNormalizer:
    """Normaliza texto para pronunciacion TTS en espanol chileno"""

    def normalize_letters(self, text: str) -> str:
        """ABC → A. B. C."""

    def number_to_words(self, n: int) -> str:
        """45 → cuarenta y cinco"""

    def normalize_number(self, number_str: str, mode: str) -> str:
        """
        mode="words": 45 → cuarenta y cinco
        mode="digits": 45 → cuatro cinco
        """

    def normalize_plate(self, plate: str, number_mode: str) -> str:
        """BBCL-45 → B. B. C. L. cuarenta y cinco"""

    def validate_plate_format(self, plate: str) -> dict:
        """Valida formato de patente chilena"""

    def normalize_vehicle_announcement(
        self, marca, color, patente, template, number_mode
    ) -> dict:
        """Genera texto completo normalizado"""
```

### 5.3 Formatos de Patente Soportados

| Formato | Ejemplo | Pronunciacion |
|---------|---------|---------------|
| Nuevo (2007+) | BBCL-45 | B. B. C. L. cuarenta y cinco |
| Antiguo | AA-1234 | A. A. mil doscientos treinta y cuatro |
| Personalizado | ABC123 | A. B. C. uno dos tres |

### 5.4 Plantillas de Mensaje

```python
VEHICLE_TEMPLATES = {
    "default": "Atencion. El vehiculo {marca}, color {color}, "
               "patente {patente}, se encuentra mal estacionado...",
    "formal": "Estimados usuarios. Se solicita al propietario...",
    "urgente": "Atencion urgente. El vehiculo {marca}...",
    "amable": "Estimado cliente. Le informamos que su vehiculo..."
}
```

---

## 6. API Endpoints

### 6.1 GET `/api/v1/operations/vehicles/options`

Retorna opciones para el formulario.

**Response:**
```json
{
  "brands": [{"id": "toyota", "name": "Toyota"}, ...],
  "colors": [{"id": "rojo", "name": "Rojo", "hex_color": "#FF0000"}, ...],
  "templates": [{"id": "default", "name": "Estandar", "description": "..."}]
}
```

### 6.2 POST `/api/v1/operations/vehicles/validate-plate`

Valida formato de patente.

**Request:**
```json
{"patente": "BBCL-45"}
```

**Response:**
```json
{
  "valid": true,
  "format": "new",
  "letters": "BBCL",
  "numbers": "45",
  "pronunciation": "B. B. C. L. cuarenta y cinco"
}
```

### 6.3 POST `/api/v1/operations/vehicles/preview`

Vista previa del texto normalizado.

**Request:**
```json
{
  "marca": "Toyota",
  "color": "rojo",
  "patente": "BBCL-45",
  "template": "default",
  "number_mode": "words"
}
```

**Response:**
```json
{
  "original": "...patente BBCL-45...",
  "normalized": "...patente B. B. C. L. cuarenta y cinco...",
  "plate_info": {...},
  "components": {...}
}
```

### 6.4 POST `/api/v1/operations/vehicles/generate`

Genera audio TTS.

**Request:**
```json
{
  "marca": "Toyota",
  "color": "rojo",
  "patente": "BBCL-45",
  "voice_id": "juan_carlos",
  "music_file": "cool_beat.mp3",
  "template": "default",
  "number_mode": "words"
}
```

**Response:**
```json
{
  "success": true,
  "original_text": "...",
  "normalized_text": "...",
  "audio_url": "/storage/audio/vehicle_20251212_123456_BBCL45_juan_carlos.mp3",
  "audio_id": 123,
  "filename": "vehicle_...",
  "duration": 15.5,
  "voice_id": "juan_carlos",
  "voice_name": "Juan Carlos",
  "template_used": "default",
  "plate_info": {...}
}
```

---

## 7. Componentes Frontend

### 7.1 useVehicleAnnouncement.ts (Composable)

Estado reactivo centralizado para toda la funcionalidad.

```typescript
// Estado del formulario
marca, color, patente, voiceId, musicFile, template, numberMode

// Datos cargados
brands, colors, templates, voices, musicTracks

// Preview y validacion
previewText, plateValidation

// Audio generado
generatedAudio

// Estados de carga
loadingOptions, loadingPreview, loadingGenerate, loadingVoices, loadingMusic

// Error
error

// Acciones
initialize()           // Carga inicial de datos
loadOptions()          // Carga marcas, colores, plantillas
loadVoices()           // Carga voces activas
loadMusicTracks()      // Carga pistas de musica
validatePlate()        // Valida patente (con debounce)
previewNormalizedText() // Preview (con debounce)
generateAnnouncement() // Genera audio
resetForm()            // Reinicia formulario
```

### 7.2 Watchers Automaticos

```typescript
// Validacion de patente en tiempo real (300ms debounce)
watch(patente, () => validatePlate())

// Preview automatico al cambiar campos (500ms debounce)
watch([marca, color, patente, template, numberMode], () => previewNormalizedText())
```

---

## 8. Consideraciones Importantes

### 8.1 Normalizacion de Numeros

El sistema soporta dos modos:
- **words**: `45` → `cuarenta y cinco` (mas natural para numeros pequenos)
- **digits**: `45` → `cuatro cinco` (mejor para patentes largas)

### 8.2 Tildes y Caracteres Especiales

El normalizador **NO usa tildes** en las plantillas para evitar problemas de encoding con algunos sistemas TTS:
- `Atencion` en lugar de `Atención`
- `vehiculo` en lugar de `vehículo`

### 8.3 Singleton del Normalizador

```python
# Uso recomendado
from app.services.text import text_normalizer

result = text_normalizer.normalize_plate("BBCL-45")
```

### 8.4 API Client (Frontend)

El `apiClient` ya extrae `response.data`, por lo tanto:
```typescript
// CORRECTO
const response = await apiClient.get<Voice[]>('/api/v1/audio/voices')
voices.value = response.filter(v => v.active)

// INCORRECTO (doble .data)
voices.value = response.data.filter(v => v.active)
```

---

## 9. Extension del Modulo

### 9.1 Agregar Nueva Plantilla de Operaciones

1. **Backend**: Crear nuevo archivo en `endpoints/operations/`
2. **Backend**: Agregar al router en `endpoints/operations/__init__.py`
3. **Frontend**: Crear directorio en `components/operations/[nueva-plantilla]/`
4. **Frontend**: Agregar ruta en `router/index.ts`
5. **Frontend**: Agregar tab en `OperationsNav.vue`

### 9.2 Estructura para Nueva Plantilla

```
operations/
├── vehicles/          # Existente
└── lost-child/        # Nueva plantilla
    ├── LostChildAnnouncement.vue
    ├── components/
    │   ├── ChildForm.vue
    │   ├── PreviewText.vue
    │   └── AudioResult.vue
    └── composables/
        └── useLostChildAnnouncement.ts
```

### 9.3 Agregar Nuevo Idioma al Normalizador

El diccionario de numeros esta en `normalizer.py`:
```python
UNITS = {0: "cero", 1: "uno", ...}
TENS = {30: "treinta", ...}
HUNDREDS = {100: "cien", ...}
```

Para otro idioma, crear una clase derivada o configuracion por idioma.

---

## 10. Testing

### 10.1 Test del Normalizador (Python)

```python
from app.services.text import text_normalizer

# Test basico
assert text_normalizer.normalize_letters("BBCL") == "B. B. C. L."
assert text_normalizer.number_to_words(45) == "cuarenta y cinco"
assert text_normalizer.normalize_plate("BBCL-45") == "B. B. C. L. cuarenta y cinco"

# Test plantilla
result = text_normalizer.normalize_vehicle_announcement(
    marca="Toyota", color="rojo", patente="BBCL-45"
)
assert "B. B. C. L." in result["normalized"]
```

### 10.2 Verificacion Manual

```bash
# Backend
cd /var/www/mediaflow-v2/backend
source venv/bin/activate
python -c "from app.services.text import text_normalizer; print(text_normalizer.normalize_plate('BBCL-45'))"

# Frontend
cd /var/www/mediaflow-v2/frontend
npm run build
```

---

## 11. Dependencias

### Backend
- FastAPI (framework)
- SQLAlchemy (ORM)
- Pydantic (validacion)
- pydub (audio processing)

### Frontend
- Vue 3 + Composition API
- TypeScript
- DaisyUI (UI components)
- Heroicons (iconos)

---

## 12. Archivos Clave para Modificaciones

| Tarea | Archivo |
|-------|---------|
| Agregar marca/color | `vehicles.py` (COMMON_BRANDS, COMMON_COLORS) |
| Nueva plantilla de mensaje | `normalizer.py` (VEHICLE_TEMPLATES) |
| Cambiar validacion de patente | `normalizer.py` (validate_plate_format) |
| Modificar UI del formulario | `VehicleForm.vue` |
| Cambiar logica de preview | `useVehicleAnnouncement.ts` |
| Agregar endpoint | `vehicles.py` + `operations.py` (schema) |

---

**Fin de la documentacion**
