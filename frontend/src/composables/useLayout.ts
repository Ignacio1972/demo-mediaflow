import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const pageTitles: Record<string, string> = {
  '/campaigns': 'Campañas',
  '/library': 'Librería',
  '/dashboard': 'Crear',
  '/calendar': 'Calendario',
  '/music': 'Música',
  '/operations': 'Operaciones',
  '/shortcuts': 'Shortcuts',
  '/playroom': 'Playroom',
  '/settings': 'Configuración',
  '/recent': 'Recientes',
  '/landing': 'Inicio',
  '/chat': 'Asistente',
}

// Shared sidebar state (module-level so it's shared across components)
const isSidebarOpen = ref(false)
const isSidebarVisible = ref(false)

export function useLayout() {
  const route = useRoute()

  const pageTitle = computed(() => {
    // Check exact match first, then prefix match
    if (pageTitles[route.path]) return pageTitles[route.path]
    // Campaign detail
    if (route.path.startsWith('/campaigns/')) return 'Campañas'
    // Operations sub-pages
    if (route.path.startsWith('/operations/')) return 'Operaciones'
    // Settings sub-pages
    if (route.path.startsWith('/settings/')) return 'Configuración'
    // Fallback: find longest matching prefix
    const match = Object.keys(pageTitles)
      .filter(p => route.path.startsWith(p))
      .sort((a, b) => b.length - a.length)[0]
    return match ? pageTitles[match] : 'MediaFlow'
  })

  const openSidebar = () => {
    isSidebarOpen.value = true
    document.body.style.overflow = 'hidden'
    requestAnimationFrame(() => {
      isSidebarVisible.value = true
    })
  }

  const closeSidebar = () => {
    isSidebarVisible.value = false
    setTimeout(() => {
      isSidebarOpen.value = false
      document.body.style.overflow = ''
    }, 300)
  }

  // Close on route change
  watch(() => route.path, () => {
    if (isSidebarOpen.value) closeSidebar()
  })

  // Close on Escape
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isSidebarOpen.value) closeSidebar()
  }

  onMounted(() => document.addEventListener('keydown', handleEscape))
  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
    document.body.style.overflow = ''
  })

  return {
    pageTitle,
    isSidebarOpen,
    isSidebarVisible,
    openSidebar,
    closeSidebar,
  }
}
