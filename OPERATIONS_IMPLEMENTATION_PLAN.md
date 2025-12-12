# Plan de Implementación: Sección "Operaciones"

**Fecha**: 2025-12-12
**Versión**: 1.0
**Estado**: Planificación

---

## 1. Resumen Ejecutivo

Nueva sección **"Operaciones"** para MediaFlow v2 que contendrá plantillas TTS especializadas. La primera plantilla será para **vehículos mal estacionados**.

### Objetivo Principal
Crear un sistema de plantillas con normalización automática de texto para garantizar pronunciación correcta de:
- **Letras** (patentes): `ABC` → `A. B. C.`
- **Números**: `123` → `uno dos tres`

---

## 2. Arquitectura Propuesta

### 2.1 Estructura de Directorios

```
frontend/src/
├── components/
│   └── operations/                    # Nueva sección (igual que settings/, library/)
│       ├── Operations.vue             # Componente principal (container)
│       ├── OperationsNav.vue          # Navegación interna (subsecciones)
│       ├── vehicles/                  # Plantilla: Vehículos mal estacionados
│       │   ├── VehicleAnnouncement.vue
│       │   ├── components/
│       │   │   ├── VehicleForm.vue           # Formulario (marca, color, patente)
│       │   │   ├── PatentInput.vue           # Input especializado para patentes
│       │   │   ├── PreviewText.vue           # Vista previa del texto normalizado
│       │   │   └── AudioPlayer.vue           # Reproductor del TTS generado
│       │   └── composables/
│       │       └── useVehicleAnnouncement.ts # Lógica y estado
│       └── [futuras-plantillas]/      # Espacio para más plantillas

backend/app/
├── api/v1/endpoints/
│   └── operations/                    # Nuevo módulo (igual que settings/)
│       ├── __init__.py                # Router aggregator
│       └── vehicles.py                # Endpoints de vehículos
├── schemas/
│   └── operations.py                  # Pydantic models (nuevo archivo)
└── services/
    └── text/                          # Nuevo servicio de normalización
        └── normalizer.py              # Normalización de texto para TTS
```

### 2.2 Rutas Propuestas

| Ruta Frontend | Componente | Descripción |
|---------------|------------|-------------|
| `/operations` | Operations.vue | Redirect a primera subsección |
| `/operations/vehicles` | VehicleAnnouncement.vue | Plantilla vehículos |

| Endpoint Backend | Método | Descripción |
|------------------|--------|-------------|
| `/api/v1/operations/vehicles/generate` | POST | Generar anuncio de vehículo |
| `/api/v1/operations/vehicles/preview` | POST | Preview de texto normalizado |
| `/api/v1/operations/templates` | GET | Listar plantillas disponibles |

---

## 3. Normalización de Texto (Español Chileno)

### 3.1 Reglas de Normalización

```python
# Letras → separadas con puntos
"BBCL" → "B. B. C. L."

# Números → palabras
"45" → "cuarenta y cinco"
"123" → "uno dos tres"  # Patentes: dígito por dígito

# Patente completa
"BBCL-45" → "B. B. C. L. cuarenta y cinco"
"BBCL 45" → "B. B. C. L. cuarenta y cinco"

# Formatos de patente chilena soportados:
# - Antiguo: "AA 1234" → "A. A. mil doscientos treinta y cuatro" o "uno dos tres cuatro"
# - Nuevo: "BBCL-45" → "B. B. C. L. cuarenta y cinco"
```

### 3.2 Servicio de Normalización

```python
# backend/app/services/text/normalizer.py

class TextNormalizer:
    """Normaliza texto para pronunciación TTS en español chileno"""

    def normalize_letters(self, text: str) -> str:
        """ABC → A. B. C."""

    def normalize_number(self, number: str, mode: str = "words") -> str:
        """
        mode="words": 45 → cuarenta y cinco
        mode="digits": 45 → cuatro cinco
        """

    def normalize_plate(self, plate: str) -> str:
        """BBCL-45 → B. B. C. L. cuarenta y cinco"""

    def normalize_vehicle_announcement(
        self,
        marca: str,
        color: str,
        patente: str,
        template: str = "default"
    ) -> str:
        """Genera texto completo normalizado para TTS"""
```

### 3.3 Diccionario Números (Español Chileno)

```python
NUMEROS = {
    0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro",
    5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve",
    10: "diez", 11: "once", 12: "doce", 13: "trece", 14: "catorce",
    15: "quince", 16: "dieciséis", 17: "diecisiete", 18: "dieciocho",
    19: "diecinueve", 20: "veinte", 21: "veintiuno", # ...
    30: "treinta", 40: "cuarenta", 50: "cincuenta",
    60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa",
    100: "cien", # ...
}
```

---

## 4. Componentes Frontend

### 4.1 Operations.vue (Container Principal)

```vue
<template>
  <div class="operations min-h-screen bg-base-100">
    <OperationsNav />
    <div class="p-6">
      <router-view />
    </div>
  </div>
</template>
```

### 4.2 VehicleForm.vue

**Campos del formulario:**

| Campo | Tipo | Validación | Ejemplo |
|-------|------|------------|---------|
| Marca | text/select | Required, min 2 chars | "Toyota", "Chevrolet" |
| Color | text/select | Required | "rojo", "azul", "blanco" |
| Patente | text | Required, formato chileno | "BBCL-45", "AA 1234" |
| Voz | select | Required | Lista de voces activas |
| Música | select | Optional | Lista de tracks |

**Marcas predefinidas (sugerencias):**
- Toyota, Chevrolet, Nissan, Hyundai, Kia, Mazda, Suzuki, Ford, Volkswagen, etc.

**Colores predefinidos:**
- Rojo, Azul, Blanco, Negro, Gris, Plata, Verde, Amarillo, etc.

### 4.3 PatentInput.vue (Input Especializado)

```vue
<!-- Input con validación visual y normalización en tiempo real -->
<template>
  <div class="form-control">
    <label class="label">
      <span class="label-text">Patente del vehículo</span>
    </label>
    <input
      v-model="plate"
      type="text"
      placeholder="BBCL-45"
      class="input input-bordered"
      :class="{ 'input-error': !isValid, 'input-success': isValid }"
      @input="normalize"
    />
    <label class="label">
      <span class="label-text-alt text-base-content/60">
        Se pronunciará: {{ normalizedPreview }}
      </span>
    </label>
  </div>
</template>
```

### 4.4 PreviewText.vue

Muestra el texto completo que se enviará al TTS:

```
"Atención. El vehículo Toyota, color rojo, patente B. B. C. L.
cuarenta y cinco, se encuentra mal estacionado.
Por favor, retírelo de inmediato."
```

---

## 5. Backend: Endpoints

### 5.1 Schema Pydantic

```python
# backend/app/schemas/operations.py

class VehicleAnnouncementRequest(BaseModel):
    marca: str = Field(..., min_length=2, max_length=50)
    color: str = Field(..., min_length=2, max_length=30)
    patente: str = Field(..., min_length=4, max_length=10)
    voice_id: str = Field(...)
    music_file: Optional[str] = None
    template: str = Field("default", description="Plantilla de mensaje")

class VehicleAnnouncementResponse(BaseModel):
    success: bool
    original_text: str           # Texto sin normalizar
    normalized_text: str         # Texto normalizado para TTS
    audio_url: str
    filename: str
    duration: Optional[float]
    error: Optional[str] = None

class TextPreviewRequest(BaseModel):
    marca: str
    color: str
    patente: str
    template: str = "default"

class TextPreviewResponse(BaseModel):
    original: str
    normalized: str
```

### 5.2 Endpoint Principal

```python
# backend/app/api/v1/endpoints/operations/vehicles.py

@router.post("/generate", response_model=VehicleAnnouncementResponse)
async def generate_vehicle_announcement(
    request: VehicleAnnouncementRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Genera anuncio TTS para vehículo mal estacionado:
    1. Normaliza texto (letras, números)
    2. Genera TTS con ElevenLabs
    3. Mezcla con música (opcional)
    4. Retorna audio URL
    """
```

---

## 6. Plantillas de Mensaje

### 6.1 Plantilla Default

```python
TEMPLATES = {
    "default": """Atención. El vehículo {marca}, color {color},
patente {patente}, se encuentra mal estacionado.
Por favor, retírelo de inmediato.""",

    "formal": """Estimados usuarios. Se solicita al propietario
del vehículo {marca}, color {color}, patente {patente},
que por favor retire su vehículo del área.""",

    "urgente": """Atención urgente. El vehículo {marca},
color {color}, patente {patente}, está bloqueando el acceso.
Retírelo inmediatamente por favor.""",
}
```

### 6.2 Expansión Futura

La arquitectura permite agregar más plantillas:
- `lost_child`: Niño perdido
- `promotion`: Promociones
- `closing`: Anuncio de cierre
- `emergency`: Emergencias

---

## 7. Integración con Sistema Existente

### 7.1 Router Principal (api.py)

```python
# Agregar en backend/app/api/v1/api.py

from app.api.v1.endpoints.operations import router as operations_router

api_router.include_router(
    operations_router,
    prefix="/operations",
    tags=["operations"]
)
```

### 7.2 Router Frontend (router/index.ts)

```typescript
// Agregar en frontend/src/router/index.ts

{
  path: '/operations',
  name: 'operations',
  redirect: '/operations/vehicles',
  children: [
    {
      path: 'vehicles',
      name: 'operations-vehicles',
      component: () => import('@/components/operations/vehicles/VehicleAnnouncement.vue'),
    },
    // Futuras plantillas aquí
  ],
}
```

### 7.3 Header Navigation

**NOTA: La incorporación del enlace "Operaciones" en el header debe hacerse manualmente.**

Archivo a modificar: `frontend/src/components/common/NavigationHeader.vue`

Agregar después del enlace de Settings:

```vue
<!-- Operations Link -->
<router-link
  to="/operations"
  class="nav-link tooltip"
  :class="{ 'active': isActive('/operations') }"
  data-tooltip="Operaciones"
>
  <MegaphoneIcon class="h-6 w-6" />
</router-link>
```

Importar el ícono:
```typescript
import { MegaphoneIcon } from '@heroicons/vue/24/outline'
```

---

## 8. Flujo de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│                    OPERACIONES                               │
├─────────────────────────────────────────────────────────────┤
│  [Vehículos] [Niños Perdidos] [Promociones]  ← Nav interna  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │ FORMULARIO      │  │ VISTA PREVIA                     │ │
│  │                 │  │                                  │ │
│  │ Marca: [Toyota] │  │ "Atención. El vehículo Toyota,   │ │
│  │ Color: [Rojo  ] │  │  color rojo, patente             │ │
│  │ Patente: [BBCL] │  │  B. B. C. L. cuarenta y cinco,   │ │
│  │                 │  │  se encuentra mal estacionado.   │ │
│  │ Voz: [Juan C.] │  │  Por favor, retírelo..."         │ │
│  │ Música: [Beat ] │  │                                  │ │
│  │                 │  │ ┌────────────────────────────┐   │ │
│  │ [Generar Audio] │  │ │ ▶ 00:00 ━━━━━━━━━━ 00:15  │   │ │
│  │                 │  │ └────────────────────────────┘   │ │
│  └─────────────────┘  └──────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Elementos DaisyUI a Utilizar

| Elemento | Uso |
|----------|-----|
| `card` | Contenedores de formulario y preview |
| `form-control` | Grupos de inputs |
| `input`, `input-bordered` | Campos de texto |
| `select` | Dropdowns (marca, color, voz) |
| `btn`, `btn-primary` | Botón generar |
| `alert` | Mensajes de error/éxito |
| `loading` | Spinner durante generación |
| `tabs` | Navegación entre plantillas |
| `badge` | Indicadores de estado |

---

## 10. Archivos a Crear

### Frontend (7 archivos)

| Archivo | Líneas Est. | Descripción |
|---------|-------------|-------------|
| `components/operations/Operations.vue` | ~30 | Container principal |
| `components/operations/OperationsNav.vue` | ~60 | Navegación interna |
| `components/operations/vehicles/VehicleAnnouncement.vue` | ~150 | Página principal |
| `components/operations/vehicles/components/VehicleForm.vue` | ~180 | Formulario |
| `components/operations/vehicles/components/PreviewText.vue` | ~80 | Vista previa |
| `components/operations/vehicles/components/AudioPlayer.vue` | ~100 | Reproductor |
| `components/operations/vehicles/composables/useVehicleAnnouncement.ts` | ~200 | Lógica |

### Backend (4 archivos)

| Archivo | Líneas Est. | Descripción |
|---------|-------------|-------------|
| `api/v1/endpoints/operations/__init__.py` | ~20 | Router aggregator |
| `api/v1/endpoints/operations/vehicles.py` | ~150 | Endpoints |
| `schemas/operations.py` | ~60 | Pydantic models |
| `services/text/normalizer.py` | ~150 | Normalización |

---

## 11. Archivos a Modificar

| Archivo | Cambio |
|--------|--------|
| `backend/app/api/v1/api.py` | Agregar router de operations |
| `frontend/src/router/index.ts` | Agregar rutas de operations |
| `frontend/src/components/common/NavigationHeader.vue` | **MANUAL**: Agregar enlace |

---

## 12. Orden de Implementación

### Fase 1: Backend Base
1. `services/text/normalizer.py` - Normalización de texto
2. `schemas/operations.py` - Schemas Pydantic
3. `api/v1/endpoints/operations/` - Endpoints

### Fase 2: Frontend Base
4. `operations/Operations.vue` - Container
5. `operations/OperationsNav.vue` - Navegación
6. Router actualizado

### Fase 3: Plantilla Vehículos
7. `vehicles/composables/useVehicleAnnouncement.ts` - Lógica
8. `vehicles/components/` - Componentes UI
9. `vehicles/VehicleAnnouncement.vue` - Página

### Fase 4: Integración
10. Pruebas de normalización
11. Pruebas de generación TTS
12. **MANUAL**: Agregar enlace en header

---

## 13. Testing

### Test de Normalización

```python
def test_normalize_plate():
    normalizer = TextNormalizer()

    assert normalizer.normalize_plate("BBCL-45") == "B. B. C. L. cuarenta y cinco"
    assert normalizer.normalize_plate("AA 1234") == "A. A. uno dos tres cuatro"
    assert normalizer.normalize_letters("XYZ") == "X. Y. Z."
    assert normalizer.normalize_number("99") == "noventa y nueve"
```

### Test E2E

```typescript
// Frontend: Verificar que el texto normalizado se muestra correctamente
// y que el audio se genera sin errores
```

---

## 14. Consideraciones Finales

### Ventajas de esta arquitectura:
- **Modular**: Cada plantilla es independiente
- **Reutilizable**: El normalizador sirve para futuras plantillas
- **Consistente**: Sigue el patrón establecido en settings/
- **Escalable**: Fácil agregar más plantillas en operations/

### Dependencias:
- ElevenLabs API (ya integrada)
- Voces configuradas en el sistema
- Música de fondo (opcional, ya integrada)

---

**Versión**: 1.0
**Autor**: Claude AI
**Fecha**: 2025-12-12
