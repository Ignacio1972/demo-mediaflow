# MediaFlow v2 - Design System

**Fecha**: 2025-12-23
**Estado**: Implementado
**Archivo de estilos**: `frontend/src/assets/main.css`

---

## Resumen Ejecutivo

Este documento describe el sistema de diseño de MediaFlow v2. Los estilos base se aplican **globalmente** a través de `main.css`, lo que significa que todos los componentes DaisyUI heredan automáticamente el nuevo look profesional.

### Implementación

- **Global (automático)**: Cards, botones, inputs, badges, modales, etc. ya tienen los estilos aplicados via CSS
- **Manual (por componente)**: Headers con iconos, subtítulos descriptivos, empty states decorativos

---

## Principios de Diseño

### 1. Menos es más
- Eliminar elementos decorativos innecesarios (emojis en títulos)
- Usar espacio en blanco generosamente
- Reducir la densidad visual

### 2. Jerarquía clara
- Títulos grandes y bold
- Subtítulos en gris claro
- Contenido con peso visual apropiado

### 3. Feedback visual
- Hover states claros y consistentes
- Transiciones suaves (200ms)
- Estados de loading elegantes

### 4. Consistencia
- Border-radius uniformes (`rounded-xl` para elementos, `rounded-2xl` para contenedores)
- Paleta de colores limitada usando variables de DaisyUI
- Espaciado basado en múltiplos de 4px

---

## Estilos Globales (Automáticos)

Estos estilos se aplican automáticamente a todos los componentes DaisyUI:

### Cards
```css
.card {
  @apply bg-base-100 border-2 border-base-300 rounded-2xl shadow-sm;
  @apply overflow-hidden transition-all duration-200;
}

.card:hover {
  @apply shadow-md;
}

.card-body {
  @apply p-6 gap-4;
}
```

### Botones
```css
.btn {
  @apply rounded-xl font-medium transition-all duration-200;
}

.btn-primary {
  @apply shadow-lg shadow-primary/25;
}

.btn-primary:hover {
  @apply shadow-xl shadow-primary/30;
}

.btn-ghost {
  @apply shadow-none hover:bg-base-200;
}
```

### Inputs y Selects
```css
.input,
.select,
.textarea {
  @apply bg-base-200/50 border-2 border-base-300 rounded-xl;
  @apply transition-all duration-200;
}

.input:focus,
.select:focus,
.textarea:focus {
  @apply bg-base-100 border-primary outline-none;
  @apply ring-2 ring-primary/20;
}
```

### Badges
```css
.badge {
  @apply font-medium rounded-full px-3 py-1;
}

.badge-primary {
  @apply bg-primary/10 text-primary border-0;
}

.badge-success {
  @apply bg-success/10 text-success border-0;
}
/* ... otros colores igual */
```

### Modales
```css
.modal-box {
  @apply bg-base-100 border-2 border-base-300/60 rounded-2xl;
  @apply p-6 max-w-lg shadow-2xl;
}
```

### Alerts
```css
.alert {
  @apply rounded-2xl border-2 p-4;
}

.alert-error {
  @apply bg-error/10 border-error/20 text-error;
}
/* ... otros tipos igual */
```

---

## Clases de Animación Disponibles

Estas clases están disponibles globalmente:

| Clase | Efecto | Uso |
|-------|--------|-----|
| `.fade-in` | Fade simple | Elementos que aparecen |
| `.fade-in-up` | Fade + slide up | Contenido principal |
| `.slide-in` | Slide desde izquierda | Paneles laterales |
| `.scale-in` | Scale up | Modales, dropdowns |
| `.item-enter` | Fade + slide + scale | Items de listas/grids |

### Animación escalonada para listas

```html
<div
  v-for="(item, index) in items"
  :key="item.id"
  :style="{ animationDelay: `${index * 50}ms` }"
  class="item-enter"
>
  <!-- contenido -->
</div>
```

---

## Utilidades Custom

### Sombras con color primario

```html
<div class="shadow-primary-sm">Sombra sutil</div>
<div class="shadow-primary-md">Sombra media</div>
<div class="shadow-primary-lg">Sombra pronunciada</div>
```

### Efecto glass

```html
<div class="glass-effect">
  Contenido con efecto glassmorphism
</div>
```

### Texto con gradiente

```html
<span class="text-gradient">Texto con gradiente</span>
```

---

## Patrones Manuales (Por Componente)

Estos patrones requieren implementación manual en cada componente:

### Page Header con Icono

```html
<div class="mb-10">
  <div class="flex items-center gap-3 mb-2">
    <div class="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-xl">
      <TruckIcon class="w-5 h-5 text-primary" />
    </div>
    <h1 class="text-3xl font-bold tracking-tight">Título de Página</h1>
  </div>
  <p class="text-base-content/50 ml-[52px]">
    Descripción o estadísticas de la página
  </p>
</div>
```

### Título con Subtítulo (dentro de cards)

```html
<div class="mb-6">
  <h2 class="text-xl font-bold tracking-tight">Título de Sección</h2>
  <p class="text-sm text-base-content/50 mt-1">
    Descripción breve de lo que hace esta sección
  </p>
</div>
```

### Empty State Decorativo

```html
<div class="flex flex-col items-center justify-center py-12">
  <!-- Contenedor decorativo -->
  <div class="relative mb-6">
    <div class="absolute -inset-4 bg-primary/5 rounded-full animate-pulse"></div>
    <div class="relative flex items-center justify-center w-20 h-20 bg-base-200 rounded-2xl">
      <DocumentTextIcon class="w-10 h-10 text-base-content/20" />
    </div>
  </div>

  <!-- Texto -->
  <h3 class="text-lg font-semibold mb-2">Sin resultados</h3>
  <p class="text-base-content/50 text-center text-sm max-w-xs">
    Descripción de qué hacer para llenar este espacio
  </p>

  <!-- CTA opcional -->
  <button class="btn btn-primary mt-6">
    <PlusIcon class="w-5 h-5" />
    Crear nuevo
  </button>
</div>
```

### Loading State con Texto

```html
<div class="flex flex-col items-center justify-center py-12">
  <span class="loading loading-spinner loading-lg text-primary"></span>
  <p class="text-sm text-base-content/50 mt-4">Cargando datos...</p>
</div>
```

### Card Grid con "Add" Card

```html
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
  <!-- Items -->
  <ItemCard v-for="item in items" :key="item.id" :item="item" />

  <!-- Add card -->
  <button class="group flex flex-col items-center justify-center
                 min-h-[180px] border-2 border-dashed border-base-300
                 rounded-2xl hover:border-primary hover:bg-primary/5
                 transition-all">
    <div class="flex items-center justify-center w-12 h-12
                bg-base-200 group-hover:bg-primary/10
                rounded-xl transition-colors mb-3">
      <PlusIcon class="w-6 h-6 text-base-content/40 group-hover:text-primary" />
    </div>
    <span class="text-sm text-base-content/50 group-hover:text-primary">
      Agregar
    </span>
  </button>
</div>
```

---

## Colores y Opacidades

### Texto

| Uso | Clase |
|-----|-------|
| Principal | `text-base-content` |
| Secundario | `text-base-content/60` |
| Hint/Descripción | `text-base-content/50` |
| Disabled | `text-base-content/40` |
| Placeholder | `placeholder:text-base-content/40` |

### Backgrounds Sutiles

```html
<div class="bg-primary/5">  <!-- Muy sutil -->
<div class="bg-primary/10"> <!-- Sutil -->
<div class="bg-base-200/50"> <!-- Semi-transparente -->
```

---

## Iconos

Usar **Heroicons** (ya instalado):

```typescript
import { TruckIcon, PlusIcon } from '@heroicons/vue/24/outline'
import { CheckCircleIcon } from '@heroicons/vue/24/solid'
```

| Contexto | Tamaño |
|----------|--------|
| Botones | `w-5 h-5` |
| Headers de página | `w-5 h-5` |
| Navegación | `w-6 h-6` |
| Empty states | `w-10 h-10` a `w-12 h-12` |

---

## Temas Soportados

Los estilos funcionan con todos los temas de MediaFlow:

| Tema | Características |
|------|-----------------|
| **mediaflow** | Oscuro con glow cyan |
| **cleanwhite** | Claro profesional |
| **nordic** | Claro minimalista |
| **nexus** | Claro con gradientes |
| **hrm** | Cálido caramelo |

Cada tema tiene ajustes específicos en `main.css` para optimizar la apariencia.

---

## Checklist para Nuevos Componentes

Al crear un nuevo componente, verificar:

- [ ] Header con icono decorativo (si es página principal)
- [ ] Títulos con subtítulos explicativos
- [ ] Empty state decorativo (no solo texto)
- [ ] Loading state con mensaje
- [ ] Usar Heroicons (no emojis)
- [ ] Animaciones de entrada para listas (`.item-enter`)

**Nota**: Cards, botones, inputs, badges, etc. ya tienen estilos aplicados automáticamente.

---

## Archivos Clave

| Archivo | Contenido |
|---------|-----------|
| `src/assets/main.css` | Estilos globales DS V2 |
| `tailwind.config.js` | Configuración de temas |
| `docs/DESIGN_SYSTEM_V2.md` | Este documento |

---

## Notas Técnicas

### Stack
- **Tailwind CSS 3.4** + **DaisyUI 4.4**
- No se requiere migración a Tailwind 4 / DaisyUI 5

### Performance
- Animaciones usan `transform` y `opacity` (GPU-accelerated)
- Transiciones de 200ms para respuesta inmediata
- Sin dependencias adicionales

### Compatibilidad
- Los estilos usan variables CSS de DaisyUI (`base-100`, `primary`, etc.)
- Funciona automáticamente con todos los temas
- Compatible con modo oscuro/claro

---

**Versión**: 2.0
**Última actualización**: 2025-12-23
