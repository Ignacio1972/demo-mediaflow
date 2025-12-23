# Sistema de Iconos - MediaFlow

## Estado Actual

### Componentes

| Archivo | Función |
|---------|---------|
| `shared/ui/DynamicIcon.vue` | Renderiza Heroicons por nombre o emojis legacy |
| `shared/ui/IconSelector.vue` | Grid de selección con 40 iconos predefinidos |
| `shared/ui/icons.ts` | Lista de iconos disponibles por categoría |

### Cómo funciona

```vue
<!-- Renderizar icono -->
<DynamicIcon name="Gift" class="w-6 h-6" />

<!-- Selector en formularios -->
<IconSelector v-model="selectedIcon" />
```

**Almacenamiento:** Campo `icon: String(50)` en modelo `Category`

**Valores posibles:**
- `"Gift"` → Heroicon
- `"🎄"` → Emoji (retrocompatibilidad)

### Limitaciones

- Solo 40 iconos Heroicons disponibles
- Sin búsqueda
- Iconos hardcodeados en `icons.ts`

---

## Propuesta: Iconify

### Qué es

Meta-librería con +200,000 iconos de +200 sets (MDI, Heroicons, Phosphor, etc.)

### Instalación

```bash
npm install @iconify/vue
```

### Cambios requeridos

**1. DynamicIcon.vue**

```vue
<script setup>
import { Icon } from '@iconify/vue'

const props = defineProps<{ name: string | null }>()

// Detectar emoji vs icono
const isEmoji = (str: string) => /[\u{1F300}-\u{1F9FF}]/u.test(str)
</script>

<template>
  <span v-if="name && isEmoji(name)">{{ name }}</span>
  <Icon v-else :icon="name || 'mdi:folder'" />
</template>
```

**2. IconSelector.vue**

```vue
<script setup>
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

const search = ref('')
const results = ref([])

// Buscar via API Iconify
async function searchIcons(query: string) {
  const res = await fetch(
    `https://api.iconify.design/search?query=${query}&limit=30`
  )
  results.value = await res.json()
}
</script>

<template>
  <input v-model="search" @input="searchIcons(search)" placeholder="Buscar..." />
  <div class="grid grid-cols-6 gap-2">
    <button v-for="icon in results" @click="emit('select', icon)">
      <Icon :icon="icon" class="w-6 h-6" />
    </button>
  </div>
</template>
```

**3. Base de datos**

Sin cambios. El campo `icon` ya es `String(50)`.

```
Antes:  icon = "Gift"         (Heroicon)
Después: icon = "mdi:gift"    (Iconify)
         icon = "🎄"          (emoji sigue funcionando)
```

### Arquitectura final

```
Usuario selecciona icono
         │
         ▼
┌─────────────────────────┐
│    IconSelector.vue     │
│  ┌───────────────────┐  │
│  │ 🔍 "gift"         │  │  ← Búsqueda
│  └───────────────────┘  │
│  [MDI] [Heroicons] [PH] │  ← Filtro por set
│  ┌──┬──┬──┬──┬──┬──┐   │
│  │🎁│📦│⭐│🔔│📅│..│   │  ← Resultados
│  └──┴──┴──┴──┴──┴──┘   │
└─────────────────────────┘
         │
         ▼ selecciona "mdi:gift"
         │
    PATCH /api/v1/campaigns/:id
    { icon: "mdi:gift" }
         │
         ▼
┌─────────────────────────┐
│   DynamicIcon.vue       │
│   <Icon icon="mdi:gift">│  ← Carga desde API Iconify
└─────────────────────────┘
```

### Complejidad estimada

| Tarea | Tiempo |
|-------|--------|
| Instalar @iconify/vue | 5 min |
| Actualizar DynamicIcon | 15 min |
| Nuevo IconSelector con búsqueda | 1-2 hrs |
| Testing | 30 min |
