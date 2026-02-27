# Experimento: Rediseño Visual inspirado en TailAdmin

**Branch**: `ui/design-tests`
**Estado**: Experimento / Prueba — EN PROGRESO
**Fecha inicio**: 2026-02-27

---

## IMPORTANTE — LEER ANTES DE HACER CUALQUIER COSA

1. Este es un **experimento en un branch aislado** (`ui/design-tests`).
2. El branch `main` **NO se toca bajo ninguna circunstancia**. No hacer merge, no hacer cherry-pick, no hacer push a main.
3. Todo el trabajo vive exclusivamente en `ui/design-tests`.
4. **Para volver al diseño original** basta con:
   ```bash
   git checkout main
   cd frontend && npm run build
   ```
   El branch experimental queda ahí pero no afecta nada. El sitio vuelve instantáneamente al diseño original.

---

## Objetivo

Replicar el estilo visual de [TailAdmin Vue](https://tailadmin.com/vue) en MediaFlow, **sin cambiar el stack técnico**. Seguimos usando Tailwind v3 + DaisyUI. Solo copiamos el "look" (colores, tipografía, spacing, shadows, layout tipo cards).

---

## Qué ya se implementó

### 1. Tipografía Outfit
- Font **Outfit** cargada desde Google Fonts en `index.html`
- Configurada como `font-sans` default en `tailwind.config.js`

### 2. Tema DaisyUI "tailadmin"
Nuevo tema en `tailwind.config.js`:
```
primary:      #465FFF
base-100:     #FFFFFF
base-200:     #F9FAFB
base-300:     #E4E7EC
base-content: #344054
success:      #12B76A
error:        #F04438
warning:      #F79009
info:         #0BA5EC
```
Es el tema por defecto. El theme switcher en el header ofrece: TailAdmin / Nexus / Dark.

### 3. Shadows custom
En `tailwind.config.js`:
```
shadow-theme-xs: 0px 1px 2px rgba(16,24,40,0.05)
shadow-theme-sm: 0px 1px 3px rgba(16,24,40,0.1), 0px 1px 2px rgba(16,24,40,0.06)
shadow-theme-md: 0px 4px 8px -2px rgba(16,24,40,0.1), 0px 2px 4px -2px rgba(16,24,40,0.06)
```

### 4. Layout tipo cards flotantes
Header y sidebar son cards con esquinas redondeadas y sombra sutil:

- **Header card**: `fixed top-4 right-4 lg:left-[18rem] h-20 bg-base-200 rounded-2xl shadow-theme-sm`
- **Sidebar card**: `fixed top-28 bottom-4 left-4 w-64 bg-base-200 rounded-2xl shadow-theme-sm`
- **Content area**: `pt-28 p-4 md:p-6 max-w-screen-2xl mx-auto`

### 5. Headers de páginas unificados
- Se eliminaron los `<h1>` internos de todas las páginas (eran redundantes con el AppHeader).
- El título de cada página se muestra exclusivamente en el AppHeader, tomado de `useLayout.ts`.
- Se removieron todos los `border-b`, `border-r`, `bg-base-200` de separadores horizontales en headers internos.

### 6. Archivos clave

**Creados:**
- `frontend/src/composables/useLayout.ts` — estado del sidebar + títulos de página
- `frontend/src/components/layout/AppSidebar.vue` — sidebar card
- `frontend/src/components/layout/AppHeader.vue` — header card

**Modificados:**
- `frontend/src/App.vue` — layout principal con cards
- `frontend/tailwind.config.js` — font Outfit, shadows, tema tailadmin
- `frontend/index.html` — Google Fonts, tema default
- ~22 páginas — removidos headers internos redundantes

**Eliminado:**
- `frontend/src/components/common/NavigationHeader.vue`

---

## Problemas conocidos / Pendientes

### Sidebar: posicionamiento y espacio superior

**Estado**: No resuelto

El sidebar card empieza en `top-28` (debajo del header card). Esto deja un espacio vacío en la esquina superior izquierda entre el borde superior de la página y el inicio del sidebar card. Se probaron varias soluciones:

1. **Sidebar en `top-4` con logo** — El logo ocupaba espacio y su sección inferior se veía cortada sin rounded corners.
2. **Sidebar en `top-4` sin logo** — El `pt-6` creaba una franja vacía visible en la parte superior del card.
3. **Sidebar en `top-28`** — Alinea el sidebar debajo del header card pero deja la esquina superior izquierda vacía.
4. **Header full-width + sidebar superpuesto** — El sidebar tapaba el header, resultado visual incorrecto.

**Opciones a explorar:**
- Que el header card se extienda al full-width y el sidebar NO sea un card (vuelva a ser flush con el borde izquierdo)
- Agregar el logo en el espacio vacío de la esquina superior izquierda como elemento independiente
- Usar un diseño donde sidebar y header compartan el borde superior como un solo card en L
- Reducir el gap entre header y sidebar (actualmente 1rem)

### Mobile drawer
- El drawer mobile conserva el diseño anterior (no card). Funciona pero no está actualizado al nuevo estilo.

---

## Referencia: Estructura TailAdmin (extraída del repo)

```
TailAdmin layout:
├── AdminLayout.vue    → div.min-h-screen > sidebar + content
├── AppSidebar.vue     → fixed, w-[290px], bg-white, border-r
├── AppHeader.vue      → sticky top-0, bg-white, border-b
└── Content            → p-4 md:p-6, max-w-2xl container
```

Fuente: https://github.com/TailAdmin/vue-tailwind-admin-dashboard

---

## Cómo probar

```bash
git checkout ui/design-tests
cd frontend && npm run dev
# Abrir http://localhost:5173
```

O en demo (si el branch está deployado):
```
https://demo.mediaflow.cl
```

## Cómo volver al diseño original

```bash
git checkout main
cd frontend && npm run build
# Listo — el sitio vuelve al diseño original inmediatamente
```

El branch `ui/design-tests` no se elimina, queda disponible para retomar el experimento en cualquier momento.
