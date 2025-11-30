import { ref, computed } from 'vue'

export function useSelection() {
  const selectionMode = ref(false)
  const selectedIds = ref<Set<number>>(new Set())

  const selectedCount = computed(() => selectedIds.value.size)
  const hasSelection = computed(() => selectedIds.value.size > 0)

  function toggleSelectionMode() {
    selectionMode.value = !selectionMode.value
    if (!selectionMode.value) {
      clearSelection()
    }
  }

  function enableSelectionMode() {
    selectionMode.value = true
  }

  function disableSelectionMode() {
    selectionMode.value = false
    clearSelection()
  }

  function toggleSelect(id: number) {
    const newSet = new Set(selectedIds.value)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    selectedIds.value = newSet
  }

  function select(id: number) {
    if (!selectedIds.value.has(id)) {
      const newSet = new Set(selectedIds.value)
      newSet.add(id)
      selectedIds.value = newSet
    }
  }

  function deselect(id: number) {
    if (selectedIds.value.has(id)) {
      const newSet = new Set(selectedIds.value)
      newSet.delete(id)
      selectedIds.value = newSet
    }
  }

  function selectAll(ids: number[]) {
    selectedIds.value = new Set(ids)
  }

  function selectMultiple(ids: number[]) {
    const newSet = new Set(selectedIds.value)
    ids.forEach(id => newSet.add(id))
    selectedIds.value = newSet
  }

  function clearSelection() {
    selectedIds.value = new Set()
  }

  function isSelected(id: number): boolean {
    return selectedIds.value.has(id)
  }

  function getSelectedArray(): number[] {
    return Array.from(selectedIds.value)
  }

  return {
    selectionMode,
    selectedIds,
    selectedCount,
    hasSelection,
    toggleSelectionMode,
    enableSelectionMode,
    disableSelectionMode,
    toggleSelect,
    select,
    deselect,
    selectAll,
    selectMultiple,
    clearSelection,
    isSelected,
    getSelectedArray
  }
}
