# Guía de Migración: Tailwind CSS 4 + DaisyUI 5

**Proyecto**: MediaFlow v2.1
**Fecha**: 2025-12-23
**Branch recomendado**: `upgrade/tailwind4-daisyui5`

---

## Resumen Ejecutivo

| Aspecto | Actual | Objetivo |
|---------|--------|----------|
| Tailwind CSS | 3.4.0 | 4.x |
| DaisyUI | 4.4.0 | 5.x |
| Archivos afectados | ~45 | - |
| Tiempo estimado | 1-2 días | - |

---

## Pre-requisitos

- Node.js 20 o superior (requerido por Tailwind 4)
- Git (para trabajar en branch separado)

```bash
# Verificar versión de Node
node --version  # Debe ser >= 20.x
```

---

## Fase 1: Preparación (15 min)

### 1.1 Crear branch de trabajo

```bash
cd /var/www/mediaflow-v2
git checkout experiment/nuevo-diseno
git checkout -b upgrade/tailwind4-daisyui5
```

### 1.2 Backup de archivos críticos

```bash
cd frontend
cp package.json package.json.backup
cp tailwind.config.js tailwind.config.js.backup
cp postcss.config.js postcss.config.js.backup
cp src/assets/main.css src/assets/main.css.backup
```

---

## Fase 2: Migración Automática de Tailwind (30 min)

### 2.1 Preparar tailwind.config.js para la herramienta

Temporalmente, comenta la configuración de DaisyUI:

```js
// tailwind.config.js - TEMPORAL
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    // require('daisyui'),  // <-- COMENTAR TEMPORALMENTE
  ],
  // daisyui: { ... }  // <-- COMENTAR TEMPORALMENTE
}
```

### 2.2 Ejecutar herramienta de upgrade

```bash
npx @tailwindcss/upgrade
```

La herramienta automáticamente:
- Actualiza `package.json` con nuevas dependencias
- Convierte `tailwind.config.js` a configuración CSS
- Actualiza `postcss.config.js` o migra a Vite plugin
- Cambia `@tailwind` directives a `@import`

### 2.3 Instalar plugin de Vite (recomendado)

```bash
npm install tailwindcss @tailwindcss/vite
```

### 2.4 Actualizar vite.config.ts

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),  // <-- AGREGAR
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
      '/storage': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:3001',
        ws: true,
      },
    },
  },
})
```

### 2.5 Eliminar postcss.config.js (opcional)

Con el plugin de Vite, ya no necesitas PostCSS config separado:

```bash
rm postcss.config.js
```

---

## Fase 3: Instalar DaisyUI 5 (15 min)

### 3.1 Instalar DaisyUI 5

```bash
npm install -D daisyui@latest
```

### 3.2 Actualizar main.css

Reemplazar el contenido inicial de `src/assets/main.css`:

```css
/* ============================================
   TAILWIND + DAISYUI IMPORTS
   ============================================ */
@import "tailwindcss";

@plugin "daisyui" {
  themes: mediaflow --default, cleanwhite, nordic, nexus, hrm,
          light, dark, cupcake, bumblebee, emerald, corporate,
          synthwave, retro, cyberpunk, valentine, halloween,
          garden, forest, aqua, lofi, pastel, fantasy,
          wireframe, black, luxury, dracula, cmyk, autumn,
          business, acid, lemonade, night, coffee, winter,
          dim, nord, sunset;
}

/* ============================================
   CUSTOM THEMES (migrados de tailwind.config.js)
   ============================================ */

/* TEMA: mediaflow (Dark tech style) */
@plugin "daisyui/theme" {
  name: "mediaflow";
  default: true;
  color-scheme: dark;
  --color-primary: oklch(70% 0.15 190);
  --color-primary-content: oklch(98% 0.01 190);
  --color-secondary: oklch(70% 0.15 190);
  --color-secondary-content: oklch(98% 0.01 190);
  --color-accent: oklch(65% 0.12 170);
  --color-accent-content: oklch(98% 0.01 170);
  --color-neutral: oklch(25% 0.02 250);
  --color-neutral-content: oklch(90% 0.01 250);
  --color-base-100: oklch(15% 0.02 250);
  --color-base-200: oklch(25% 0.02 250);
  --color-base-300: oklch(35% 0.02 250);
  --color-base-content: oklch(90% 0.01 250);
  --color-info: oklch(60% 0.2 250);
  --color-info-content: oklch(98% 0.01 250);
  --color-success: oklch(65% 0.2 160);
  --color-success-content: oklch(98% 0.01 160);
  --color-warning: oklch(75% 0.15 85);
  --color-warning-content: oklch(20% 0.05 85);
  --color-error: oklch(60% 0.2 25);
  --color-error-content: oklch(98% 0.01 25);
}

/* TEMA: cleanwhite (Professional light) */
@plugin "daisyui/theme" {
  name: "cleanwhite";
  color-scheme: light;
  --color-primary: oklch(70% 0.15 190);
  --color-primary-content: oklch(98% 0.01 190);
  --color-secondary: oklch(70% 0.15 190);
  --color-secondary-content: oklch(98% 0.01 190);
  --color-accent: oklch(60% 0.15 195);
  --color-accent-content: oklch(98% 0.01 195);
  --color-neutral: oklch(30% 0.02 220);
  --color-neutral-content: oklch(98% 0.01 220);
  --color-base-100: oklch(100% 0 0);
  --color-base-200: oklch(98% 0.005 250);
  --color-base-300: oklch(92% 0.01 250);
  --color-base-content: oklch(30% 0.02 220);
  --color-info: oklch(60% 0.18 230);
  --color-info-content: oklch(98% 0.01 230);
  --color-success: oklch(55% 0.18 160);
  --color-success-content: oklch(98% 0.01 160);
  --color-warning: oklch(70% 0.15 70);
  --color-warning-content: oklch(20% 0.05 70);
  --color-error: oklch(55% 0.2 25);
  --color-error-content: oklch(98% 0.01 25);
}

/* TEMA: nordic (Scandinavian minimal) */
@plugin "daisyui/theme" {
  name: "nordic";
  color-scheme: light;
  --color-primary: oklch(70% 0.15 190);
  --color-primary-content: oklch(98% 0.01 190);
  --color-secondary: oklch(75% 0.12 190);
  --color-secondary-content: oklch(98% 0.01 190);
  --color-accent: oklch(65% 0.12 170);
  --color-accent-content: oklch(98% 0.01 170);
  --color-neutral: oklch(50% 0.02 250);
  --color-neutral-content: oklch(98% 0.01 250);
  --color-base-100: oklch(96% 0.005 250);
  --color-base-200: oklch(92% 0.01 250);
  --color-base-300: oklch(85% 0.01 250);
  --color-base-content: oklch(40% 0.02 250);
  --color-info: oklch(55% 0.18 230);
  --color-info-content: oklch(98% 0.01 230);
  --color-success: oklch(60% 0.18 145);
  --color-success-content: oklch(98% 0.01 145);
  --color-warning: oklch(65% 0.15 85);
  --color-warning-content: oklch(20% 0.05 85);
  --color-error: oklch(55% 0.2 25);
  --color-error-content: oklch(98% 0.01 25);
}

/* TEMA: nexus (Modern dashboard style) */
@plugin "daisyui/theme" {
  name: "nexus";
  color-scheme: light;
  --color-primary: oklch(60% 0.2 260);
  --color-primary-content: oklch(98% 0.01 260);
  --color-secondary: oklch(55% 0.2 280);
  --color-secondary-content: oklch(98% 0.01 280);
  --color-accent: oklch(60% 0.2 300);
  --color-accent-content: oklch(98% 0.01 300);
  --color-neutral: oklch(30% 0.02 220);
  --color-neutral-content: oklch(98% 0.01 220);
  --color-base-100: oklch(100% 0 0);
  --color-base-200: oklch(98% 0.002 220);
  --color-base-300: oklch(93% 0.005 220);
  --color-base-content: oklch(30% 0.02 220);
  --color-info: oklch(65% 0.18 230);
  --color-info-content: oklch(98% 0.01 230);
  --color-success: oklch(65% 0.2 160);
  --color-success-content: oklch(98% 0.01 160);
  --color-warning: oklch(75% 0.15 85);
  --color-warning-content: oklch(98% 0.01 85);
  --color-error: oklch(60% 0.2 25);
  --color-error-content: oklch(98% 0.01 25);
  --radius-selector: 0.5rem;
  --radius-field: 0.5rem;
  --radius-box: 0.75rem;
  --border: 1px;
}

/* TEMA: hrm (Caramellatte style) */
@plugin "daisyui/theme" {
  name: "hrm";
  color-scheme: light;
  --color-primary: oklch(0% 0 0);
  --color-primary-content: oklch(100% 0 0);
  --color-secondary: oklch(30% 0.05 50);
  --color-secondary-content: oklch(85% 0.03 70);
  --color-accent: oklch(55% 0.12 30);
  --color-accent-content: oklch(98% 0.01 30);
  --color-neutral: oklch(45% 0.08 50);
  --color-neutral-content: oklch(98% 0.01 50);
  --color-base-100: oklch(98% 0.015 80);
  --color-base-200: oklch(94% 0.025 70);
  --color-base-300: oklch(88% 0.04 65);
  --color-base-content: oklch(45% 0.08 50);
  --color-info: oklch(55% 0.2 260);
  --color-info-content: oklch(98% 0.01 260);
  --color-success: oklch(55% 0.18 160);
  --color-success-content: oklch(98% 0.01 160);
  --color-warning: oklch(80% 0.15 90);
  --color-warning-content: oklch(30% 0.08 70);
  --color-error: oklch(55% 0.2 25);
  --color-error-content: oklch(98% 0.01 25);
  --radius-selector: 2rem;
  --radius-field: 2rem;
  --radius-box: 1rem;
  --border: 2px;
}

/* ============================================
   REST OF YOUR CUSTOM CSS BELOW
   (keep your existing custom styles)
   ============================================ */
```

---

## Fase 4: Cambios en Clases de Tailwind (1 hora)

### 4.1 Renombrar utilidades (buscar y reemplazar)

Ejecutar estos comandos en la carpeta `frontend/src`:

```bash
# shadow-sm → shadow-xs (solo los que estaban solos)
# shadow → shadow-sm (solo los que estaban solos, sin sufijo)
# Nota: Revisar manualmente, la herramienta de upgrade debería manejar esto

# outline-none → outline-hidden
grep -rl "outline-none" --include="*.vue" --include="*.css" . | xargs sed -i 's/outline-none/outline-hidden/g'

# ring (solo) → ring-3
# Nota: Solo si usas ring sin número, revisar manualmente
```

### 4.2 Verificar cambios automáticos

La herramienta `@tailwindcss/upgrade` debería haber manejado:
- `@tailwind base/components/utilities` → `@import "tailwindcss"`
- Renombrado de utilidades deprecadas
- Actualización de sintaxis de variables

---

## Fase 5: Cambios en Clases de DaisyUI (2-3 horas)

### 5.1 Clases eliminadas (IMPORTANTE)

**Estas clases ya NO son necesarias** porque el estilo es default:

| Clase v4 (eliminar) | v5 (no necesita clase) |
|---------------------|------------------------|
| `input-bordered` | `input` (border es default) |
| `select-bordered` | `select` (border es default) |
| `textarea-bordered` | `textarea` (border es default) |
| `file-input-bordered` | `file-input` (border es default) |

```bash
# Ejecutar en frontend/src
grep -rl "input-bordered" --include="*.vue" . | xargs sed -i 's/input-bordered//g'
grep -rl "select-bordered" --include="*.vue" . | xargs sed -i 's/select-bordered//g'
grep -rl "textarea-bordered" --include="*.vue" . | xargs sed -i 's/textarea-bordered//g'
grep -rl "file-input-bordered" --include="*.vue" . | xargs sed -i 's/file-input-bordered//g'

# Limpiar espacios dobles resultantes
grep -rl '  ' --include="*.vue" . | xargs sed -i 's/  / /g'
```

### 5.2 Clases renombradas

| v4 | v5 |
|----|-----|
| `card-bordered` | `card-border` |
| `tabs-bordered` | `tabs-border` |
| `tabs-lifted` | `tabs-lift` |
| `tabs-boxed` | `tabs-box` |

```bash
grep -rl "card-bordered" --include="*.vue" . | xargs sed -i 's/card-bordered/card-border/g'
grep -rl "tabs-bordered" --include="*.vue" . | xargs sed -i 's/tabs-bordered/tabs-border/g'
grep -rl "tabs-lifted" --include="*.vue" . | xargs sed -i 's/tabs-lifted/tabs-lift/g'
grep -rl "tabs-boxed" --include="*.vue" . | xargs sed -i 's/tabs-boxed/tabs-box/g'
```

### 5.3 Clases de menú renombradas

| v4 | v5 |
|----|-----|
| `<li class="active">` (en menu) | `<li class="menu-active">` |
| `<li class="disabled">` (en menu) | `<li class="menu-disabled">` |
| `<li class="focus">` (en menu) | `<li class="menu-focus">` |

**Nota**: Revisar manualmente ya que `active` y `disabled` pueden usarse en otros contextos.

### 5.4 form-control y label-text ELIMINADOS

Este es el cambio más significativo. Hay **~268 ocurrencias** en el proyecto.

**Antes (v4):**
```html
<label class="form-control w-full">
  <div class="label">
    <span class="label-text">Nombre</span>
  </div>
  <input type="text" class="input input-bordered" />
</label>
```

**Después (v5):**
```html
<fieldset class="fieldset">
  <label class="label" for="nombre">Nombre</label>
  <input id="nombre" type="text" class="input" />
</fieldset>
```

**Archivos que requieren cambios manuales:**

```
frontend/src/components/campaigns/steps/StepGenerate.vue
frontend/src/components/campaigns/modals/NewCampaignModal.vue
frontend/src/components/dashboard/MessageGenerator.vue
frontend/src/components/dashboard/AISuggestions.vue
frontend/src/components/operations/vehicles/components/VehicleForm.vue
frontend/src/components/settings/templates/components/TemplateForm.vue
frontend/src/components/settings/templates/components/TemplateAddModal.vue
frontend/src/components/settings/voices/components/VoiceEditor.vue
frontend/src/components/settings/voices/components/VoiceAddModal.vue
frontend/src/components/settings/ai-clients/components/AIClientEditor.vue
frontend/src/components/settings/ai-clients/components/AIClientAddModal.vue
frontend/src/components/settings/categories/components/CategoryForm.vue
frontend/src/components/settings/categories/components/CategoryAddModal.vue
frontend/src/components/settings/music/components/MusicEditor.vue
frontend/src/components/settings/music/components/MusicUpload.vue
frontend/src/components/settings/automatic/AutomaticMode.vue
frontend/src/components/settings/playroom/components/*.vue
frontend/src/components/library/modals/ScheduleModal.vue
frontend/src/components/library/modals/UploadModal.vue
frontend/src/components/library/components/LibraryFilters.vue
```

**Estrategia recomendada:**
1. Opción A: Migrar a `<fieldset class="fieldset">` (recomendado, mejor accesibilidad)
2. Opción B: Crear clases custom temporales que repliquen el comportamiento antiguo

### 5.5 Table hover class

| v4 | v5 |
|----|-----|
| `<tr class="hover">` | `<tr class="hover:bg-base-300">` |

---

## Fase 6: Actualizar CSS Custom (1 hora)

### 6.1 Migrar estilos de main.css

El resto de tu archivo `main.css` (scrollbar, typography, animations, theme-specific styles) debería seguir funcionando. Sin embargo, verifica:

1. **`@apply` sigue funcionando** igual en Tailwind 4
2. **Clases de DaisyUI** actualizadas (ej: `input-bordered` ya no existe)
3. **Variables CSS** - DaisyUI 5 usa `oklch()` en lugar de hex

### 6.2 Revisar theme-specific styles

Los estilos específicos por tema (`[data-theme="hrm"]`, etc.) necesitan actualización si usan clases DaisyUI renombradas.

---

## Fase 7: Eliminar tailwind.config.js (10 min)

Una vez migrado todo a CSS, puedes eliminar el archivo de configuración JS:

```bash
rm tailwind.config.js
rm tailwind.config.js.backup  # después de verificar que todo funciona
```

**Nota**: Si necesitas mantener configuración JS por alguna razón, puedes cargarla con:
```css
@config "../../tailwind.config.js";
```

---

## Fase 8: Testing (2-3 horas)

### 8.1 Iniciar servidor de desarrollo

```bash
npm run dev
```

### 8.2 Checklist de verificación

- [ ] Dashboard carga correctamente
- [ ] Formularios se ven correctamente (inputs, selects, textareas)
- [ ] Botones tienen estilos correctos
- [ ] Cards se muestran bien
- [ ] Modales funcionan
- [ ] Tablas tienen hover correcto
- [ ] Navegación/menús funcionan
- [ ] Todos los temas cargan (mediaflow, cleanwhite, nordic, nexus, hrm)
- [ ] ThemeSelector funciona
- [ ] Animaciones funcionan
- [ ] Scrollbar custom funciona

### 8.3 Build de producción

```bash
npm run build
```

Verificar que no hay errores de compilación.

---

## Fase 9: Commit y Merge (15 min)

### 9.1 Commit cambios

```bash
git add .
git commit -m "upgrade: Migrate to Tailwind CSS 4 + DaisyUI 5

- Update Tailwind CSS 3.4 → 4.x
- Update DaisyUI 4.4 → 5.x
- Migrate tailwind.config.js to CSS-based config
- Update deprecated class names
- Migrate form-control to fieldset pattern
- Update theme definitions to oklch format

🤖 Generated with Claude Code"
```

### 9.2 Merge a rama principal (cuando esté listo)

```bash
git checkout experiment/nuevo-diseno
git merge upgrade/tailwind4-daisyui5
```

---

## Troubleshooting

### Error: "Cannot find module '@tailwindcss/vite'"

```bash
npm install @tailwindcss/vite
```

### Estilos no se aplican

1. Verificar que `@import "tailwindcss"` está al inicio de main.css
2. Verificar que `@plugin "daisyui"` está después del import
3. Limpiar cache: `rm -rf node_modules/.vite && npm run dev`

### Colores se ven diferentes

DaisyUI 5 usa `oklch()` en lugar de hex. Los colores pueden verse ligeramente diferentes. Ajustar valores en los temas custom si es necesario.

### Formularios se ven rotos

Revisar que todas las clases `input-bordered`, `select-bordered`, etc. fueron removidas (no reemplazadas).

---

## Referencias

- [Tailwind CSS v4 Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [DaisyUI 5 Upgrade Guide](https://daisyui.com/docs/upgrade/)
- [DaisyUI 5 Release Notes](https://daisyui.com/docs/v5/)
- [Tailwind CSS Vite Plugin](https://tailwindcss.com/docs/installation/using-vite)
- [DaisyUI Themes](https://daisyui.com/docs/themes/)
- [DaisyUI Config](https://daisyui.com/docs/config/)
