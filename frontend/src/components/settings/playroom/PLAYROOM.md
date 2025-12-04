# Automatic Playroom

**Status**: Experimental Zone
**Purpose**: Safe testing environment for UI experiments
**Independence**: 100% isolated from production Automatic Mode

---

## Overview

El **Automatic Playroom** es un clon completo del módulo Automatic Mode creado específicamente para experimentar con nuevas interfaces sin afectar el sistema principal.

### Características

- ✅ **100% Independiente**: Tiene sus propios endpoints, componentes y lógica
- ✅ **Fácil de eliminar**: No afecta ningún otro módulo del sistema
- ✅ **Funcionalidad completa**: Incluye todas las capacidades de Automatic Mode
- ✅ **Identificación clara**: Todos los archivos generados tienen prefijo `playroom_`

---

## Arquitectura

### Backend

```
backend/app/api/v1/endpoints/settings/
├── automatic.py         # Modo Automatic original
└── playroom.py          # Playroom experimental (CLON)
```

**Endpoints del Playroom**:
- `GET /api/v1/settings/playroom/config` - Configuración
- `POST /api/v1/settings/playroom/generate` - Generación de jingles

### Frontend

```
frontend/src/components/settings/
├── automatic/           # Modo Automatic original
│   ├── AutomaticMode.vue
│   ├── components/
│   └── composables/
│
└── playroom/            # Playroom experimental (CLON)
    ├── PlayroomMode.vue
    ├── components/      # Copiados de automatic
    └── composables/
        └── usePlayroomMode.ts
```

**Ruta**: `/settings/playroom`

---

## Diferencias con Automatic Mode

### Visual
- Color primario: **Secondary** (en vez de Primary)
- Icono: 🎮 (en vez de 🎙️)
- Título: "Playroom Experimental"
- Banner informativo explicando que es zona de pruebas

### Técnico
- Endpoints propios (`/playroom/*`)
- Composable independiente (`usePlayroomMode.ts`)
- Archivos generados con prefijo `playroom_*`
- Display names con prefijo `[PLAYROOM]`
- Logs con prefijo `[PLAYROOM]`

---

## Cómo usar el Playroom

1. Navega a **Settings → Playroom**
2. La interfaz es idéntica a Automatic Mode
3. Todos los cambios que hagas aquí NO afectan el modo automático
4. Los archivos generados se identifican con `playroom_` en el nombre

### Identificación de archivos generados

```bash
# Archivos del Automatic Mode
auto_20251204_123456_juan_carlos_abc123.mp3

# Archivos del Playroom
playroom_20251204_123456_juan_carlos_xyz789.mp3
```

---

## Cómo eliminar el Playroom

Si decides que ya no necesitas el Playroom, es muy fácil eliminarlo sin afectar el resto del sistema:

### 1. Backend

```bash
# Eliminar endpoint del playroom
rm backend/app/api/v1/endpoints/settings/playroom.py

# Editar settings/__init__.py y eliminar estas líneas:
# from app.api.v1.endpoints.settings.playroom import router as playroom_router
# router.include_router(playroom_router)
```

### 2. Frontend

```bash
# Eliminar directorio completo del playroom
rm -rf frontend/src/components/settings/playroom/

# Editar router/index.ts y eliminar:
# {
#   path: 'playroom',
#   name: 'settings-playroom',
#   component: () => import('@/components/settings/playroom/PlayroomMode.vue'),
# }

# Editar SettingsNav.vue y eliminar:
# - Import de BeakerIcon
# - El <router-link> del Playroom
# - Los estilos .playroom-link
```

### 3. Archivos generados (opcional)

```bash
# Eliminar todos los archivos generados por el playroom
cd backend/storage/audio
rm playroom_*.mp3

# O filtrarlos en la librería con el prefijo [PLAYROOM]
```

### 4. Verificar

```bash
# Backend
cd backend
source venv/bin/activate
python -c "from app.main import app; print('Backend OK')"

# Frontend
cd frontend
npm run build
```

---

## Casos de uso

### ✅ Ideal para:

1. **Probar nuevas interfaces** - Experimenta con carruseles, cards, etc.
2. **Testing de UX mobile** - Adapta la interfaz para mobile sin romper desktop
3. **Nuevos flujos de trabajo** - Prueba diferentes formas de seleccionar voces
4. **A/B testing interno** - Compara dos versiones lado a lado

### ❌ NO usar para:

1. Producción - Este es un entorno experimental
2. Características que deban ir al Automatic Mode principal
3. Funcionalidad que afecte otros módulos

---

## Próximos experimentos sugeridos

### 1. Interfaz Mobile-First

```typescript
// Agregar en PlayroomMode.vue
const isMobile = ref(window.innerWidth < 768)

// Crear un carrusel de voces con fotos
<VoiceCarousel
  v-if="isMobile"
  :voices="activeVoices"
  @select="selectedVoiceId = $event"
/>
```

### 2. Perfiles por Voz

```typescript
// Crear profiles en usePlayroomMode.ts
const voiceProfiles = {
  mario: {
    name: 'Mario',
    photo: '/profiles/mario.jpg',
    categories: ['operational', 'alerts'],
    messages: ['Auto mal estacionado', 'Niño perdido']
  },
  francisca: {
    name: 'Francisca',
    photo: '/profiles/francisca.jpg',
    categories: ['celebrations'],
    messages: ['Día del Niño', 'Navidad']
  },
  juan_carlos: {
    name: 'Juan Carlos',
    photo: '/profiles/juan-carlos.jpg',
    categories: ['promotions'],
    messages: ['Ofertas', 'Promociones']
  }
}
```

### 3. Carrusel de Fotografías

```vue
<template>
  <div class="carousel carousel-center w-full">
    <div
      v-for="profile in voiceProfiles"
      :key="profile.name"
      class="carousel-item w-full"
    >
      <img
        :src="profile.photo"
        @click="selectProfile(profile)"
        class="rounded-box cursor-pointer"
      />
    </div>
  </div>
</template>
```

---

## Notas importantes

1. **No hay sincronización**: Cambios en Automatic Mode NO se reflejan en Playroom y viceversa
2. **Mismo backend de datos**: Ambos usan las mismas voces, música y configuraciones
3. **Archivos separados**: Fácil de identificar y limpiar
4. **Testing seguro**: Puedes romper el Playroom sin afectar nada más

---

## Mantenimiento

- **No requiere mantenimiento**: Es un clon estático
- **Actualizar si es necesario**: Si Automatic Mode cambia, Playroom NO se actualiza automáticamente
- **Sincronizar manualmente**: Copia los cambios que quieras del Automatic Mode

---

**Versión**: 1.0
**Creado**: 2025-12-04
**Base**: Automatic Mode v2.1
