# Dashboard Mobile Overflow - Análisis y Solución

**Fecha**: 2025-12-23
**Problema**: El Dashboard se ve correctamente por unos segundos en móvil, pero después se vuelve demasiado ancho, causando scroll horizontal.

---

## Descripción del Problema

El Dashboard de MediaFlow presenta un comportamiento peculiar en dispositivos móviles:

1. **Estado inicial**: La página carga correctamente y se ve bien formateada
2. **Después de 2-3 segundos**: El layout se "rompe" y la página se vuelve más ancha que el viewport
3. **Síntomas visibles**: Aparece scroll horizontal, los elementos se ven apretados o desbordados

### ¿Por qué ocurre después de unos segundos?

El problema está directamente relacionado con la **carga asíncrona de datos**. Cuando el componente se monta, está vacío y el CSS funciona correctamente. Pero cuando los datos llegan de la API, el contenido dinámico causa overflow.

---

## Componentes Afectados

```
Dashboard.vue
├── AISuggestionsV2.vue (o AISuggestions.vue según toggle)
├── MessageGenerator.vue
│   └── Carga: voces, pistas de música
├── AudioPreview.vue
└── RecentMessages.vue
    └── Carga: mensajes recientes
```

### Datos que se cargan asíncronamente:

| Componente | Función | Datos |
|------------|---------|-------|
| `MessageGenerator` | `onMounted` | `audioStore.loadVoices()` |
| `MessageGenerator` | `onMounted` | `audioStore.loadMusicTracks()` |
| `RecentMessages` | `onMounted` | `audioStore.loadRecentMessages()` |
| `AISuggestions` | `onMounted` | Cliente AI activo |

---

## Causa Raíz: `min-width: auto` en Flexbox/Grid

### El problema clásico de CSS

En Flexbox y CSS Grid, los elementos hijos tienen por defecto:

```css
min-width: auto;
```

Esto significa que un elemento **no puede encogerse más pequeño que su contenido**. Cuando el contenido es más ancho que el espacio disponible, el contenedor se expande en lugar de activar overflow o truncar el contenido.

### Ejemplo del problema:

```html
<!-- Dashboard.vue -->
<div class="grid lg:grid-cols-5 gap-6">
  <div class="lg:col-span-3 space-y-6">  <!-- ❌ Sin min-w-0 -->
    <!-- Contenido que puede ser muy ancho -->
  </div>
</div>
```

Cuando el contenido interno (voces, mensajes, etc.) se carga, el `div` con `col-span-3` se expande más allá de su espacio asignado porque `min-width: auto` lo permite.

### La solución:

```html
<div class="lg:col-span-3 space-y-6 min-w-0">  <!-- ✅ Con min-w-0 -->
```

La clase `min-w-0` de Tailwind establece `min-width: 0`, permitiendo que el elemento se encoja correctamente.

---

## Problemas Específicos Encontrados

### 1. Grid children sin `min-w-0`

**Archivo**: `Dashboard.vue`

```html
<!-- Línea 17 - Columna izquierda -->
<div class="lg:col-span-3 space-y-6">

<!-- Línea 33 - Columna derecha -->
<div class="lg:col-span-2">
```

**Problema**: Ambos hijos del grid pueden expandirse indefinidamente.

**Solución**:
```html
<div class="lg:col-span-3 space-y-6 min-w-0">
<div class="lg:col-span-2 min-w-0">
```

---

### 2. Contenedor de avatares de voz

**Archivo**: `MessageGenerator.vue`

```html
<!-- Línea 23 -->
<div class="flex-1 flex items-center gap-2 overflow-x-auto pb-2 sm:pb-0">
```

**Problema**: Tiene `overflow-x-auto` pero no funciona porque `flex-1` sin `min-w-0` no permite que el contenedor se encoja. Cuando hay muchas voces, el contenedor se expande en lugar de activar el scroll horizontal.

**Solución**:
```html
<div class="flex-1 min-w-0 flex items-center gap-2 overflow-x-auto pb-2 sm:pb-0">
```

---

### 3. Contenedor de mensajes recientes

**Archivo**: `RecentMessages.vue`

```html
<!-- Línea 24 -->
<div v-else class="messages-container flex-1 overflow-y-auto overflow-x-hidden pr-1">
```

**Problema**: `flex-1` sin `min-w-0`.

**Solución**:
```html
<div v-else class="messages-container flex-1 min-w-0 overflow-y-auto overflow-x-hidden pr-1">
```

---

### 4. voice_id sin truncate

**Archivo**: `RecentMessages.vue`

```html
<!-- Línea 45 -->
<span>{{ message.voice_id }}</span>
```

**Problema**: Si el `voice_id` es largo (ej: `"juan_carlos_profesional_extended_v2"`), puede causar overflow.

**Solución**:
```html
<span class="truncate max-w-[100px]">{{ message.voice_id }}</span>
```

O usar el nombre de la voz en lugar del ID:
```html
<span class="truncate">{{ getVoiceName(message.voice_id) }}</span>
```

---

### 5. Animaciones translateX

**Archivo**: `RecentMessages.vue`

```javascript
// Líneas 206-208
messageEl.style.transform = 'translateX(100%)'

// Líneas 249-251
messageEl.style.transform = 'translateX(-100%)'
```

**Problema**: Cuando un mensaje se guarda/elimina con animación slide-out, el elemento se mueve fuera del viewport y puede causar scroll horizontal temporal.

**Solución**: Asegurarse de que el contenedor padre tenga `overflow-hidden`:
```html
<div class="messages-container ... overflow-hidden">
```

Nota: Ya existe `overflow-x-hidden`, pero podría no ser suficiente si el padre también tiene overflow issues.

---

### 6. Toast notifications

**Archivo**: `RecentMessages.vue`

```html
<!-- Línea 109 -->
<div class="toast toast-end toast-bottom z-50">
```

**Problema potencial**: Los toasts de DaisyUI usan `position: fixed` y podrían causar overflow en algunos navegadores móviles.

**Solución**: Mover el toast fuera del componente o asegurarse de que no afecte el layout:
```html
<Teleport to="body">
  <div class="toast toast-end toast-bottom z-50">
    ...
  </div>
</Teleport>
```

---

## Resumen de Cambios Requeridos

### Dashboard.vue
```diff
- <div class="lg:col-span-3 space-y-6">
+ <div class="lg:col-span-3 space-y-6 min-w-0">

- <div class="lg:col-span-2">
+ <div class="lg:col-span-2 min-w-0">
```

### MessageGenerator.vue
```diff
- <div class="flex-1 flex items-center gap-2 overflow-x-auto pb-2 sm:pb-0">
+ <div class="flex-1 min-w-0 flex items-center gap-2 overflow-x-auto pb-2 sm:pb-0">
```

### RecentMessages.vue
```diff
- <div v-else class="messages-container flex-1 overflow-y-auto overflow-x-hidden pr-1">
+ <div v-else class="messages-container flex-1 min-w-0 overflow-y-auto overflow-x-hidden pr-1">

- <span>{{ message.voice_id }}</span>
+ <span class="truncate max-w-[80px] sm:max-w-[100px]">{{ message.voice_id }}</span>
```

---

## Regla General para Prevenir Este Problema

Siempre que uses `flex-1`, `flex-grow`, o seas hijo de un grid/flex container con contenido dinámico, agrega `min-w-0`:

```html
<!-- ❌ Propenso a overflow -->
<div class="flex-1">
  {{ dynamicContent }}
</div>

<!-- ✅ Seguro -->
<div class="flex-1 min-w-0">
  {{ dynamicContent }}
</div>
```

---

## Nota sobre el Toggle "Nuevo Diseño"

El Dashboard tiene un toggle que cambia entre `AISuggestionsV2` y `AISuggestions`. Ambos componentes pueden tener diferentes niveles de padding y contenido, lo que puede hacer que el problema de overflow sea más o menos visible dependiendo de cuál esté activo.

Los mismos principios de `min-w-0` aplican a ambos componentes.

---

## Referencias

- [CSS Tricks: Flexbox and Truncated Text](https://css-tricks.com/flexbox-truncated-text/)
- [MDN: min-width](https://developer.mozilla.org/en-US/docs/Web/CSS/min-width)
- [Tailwind CSS: min-w-0](https://tailwindcss.com/docs/min-width)
