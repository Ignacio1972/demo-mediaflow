# White Label - Logo Switching

## Ubicación

**Archivo:** `frontend/src/components/common/NavigationHeader.vue`

El branding aparece en 2 lugares:
- Header principal (línea ~15)
- Sidebar (línea ~68)

## Opciones de Branding

### Opción 1: Solo Texto (Actual)

```vue
<span class="text-xl md:text-2xl font-semibold tracking-tight">
  <span style="color: #00adef">Media</span><span class="text-base-content">Flow</span>
</span>
```

- Color "Media": `#00adef`
- Color "Flow": se adapta al tema

### Opción 2: Logo de Cliente

```vue
<div class="flex flex-col items-center md:items-start">
  <img
    src="/images/{cliente}_logo.png"
    alt="{Cliente}"
    class="h-12 md:h-16 w-auto object-contain"
  />
  <span class="text-xs md:text-sm text-base-content/60 mt-1">
    Powered by <span style="color: #00adef">Media</span><span class="text-base-content">Flow</span>
  </span>
</div>
```

### Opción 3: Isotipo + Texto

```vue
<div class="flex flex-col items-center md:items-start">
  <img
    src="/images/solo logo.png"
    alt="MediaFlow"
    class="h-10 md:h-12 w-auto object-contain"
  />
  <span class="text-lg md:text-xl font-semibold tracking-tight mt-1">
    <span style="color: #00adef">Media</span><span class="text-base-content">Flow</span>
  </span>
</div>
```

## Logos Disponibles

Carpeta: `/frontend/public/images/`

| Archivo | Dimensiones | Uso |
|---------|-------------|-----|
| `solo logo.png` | 250 x 250 | Isotipo MediaFlow |
| `Mediaflow trans.png` | 160 x 100 | Logo completo (texto blanco) |
| `Cencosud_logo.svg.png` | 500 x 263 | Cliente: Cencosud |

## Estado Actual

- **Modo:** Solo texto
- **Colores:** "Media" #00adef / "Flow" base-content
- **Tagline:** No aplica

## Rebuild

Después de cambios, ejecutar:
```bash
cd /var/www/mediaflow-v2/frontend && npm run build
```
