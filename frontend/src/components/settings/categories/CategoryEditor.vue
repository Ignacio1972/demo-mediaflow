<template>
  <div class="category-editor min-h-screen bg-base-100">
    <SettingsNav />
    <div class="p-6">
      <div class="container mx-auto max-w-7xl">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <div class="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-xl">
              <FolderIcon class="w-5 h-5 text-primary" />
            </div>
            <h1 class="text-3xl font-bold tracking-tight">Category Editor</h1>
          </div>
          <p class="text-base-content/50 ml-13">
            Gestiona categorías para organizar tus mensajes en la biblioteca
          </p>
        </div>
        <button
          @click="showAddModal = true"
          class="btn btn-primary gap-2"
        >
          <PlusIcon class="w-5 h-5" />
          Nueva Categoría
        </button>
      </div>

      <!-- Toast Messages -->
      <div v-if="error" class="alert alert-error mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <div v-if="successMessage" class="alert alert-success mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ successMessage }}</span>
      </div>

      <!-- Main Content -->
      <div class="grid lg:grid-cols-3 gap-6">
        <!-- Left: Category List (1 column) -->
        <div class="lg:col-span-1">
          <CategoryList
            :categories="sortedCategories"
            :selected-category="selectedCategory"
            :is-loading="isLoading"
            @select="handleSelectCategory"
            @reorder="handleReorder"
          />
        </div>

        <!-- Right: Category Form (2 columns) -->
        <div class="lg:col-span-2">
          <CategoryForm
            v-if="selectedCategory"
            :category="selectedCategory"
            :is-saving="isSaving"
            @save="handleSaveCategory"
            @cancel="handleCancelEdit"
            @delete="handleDeleteCategory"
          />

          <!-- Empty State -->
          <div v-else class="card bg-base-100 shadow-xl">
            <div class="card-body items-center text-center py-16">
              <div class="text-6xl mb-4">👈</div>
              <h3 class="text-xl font-semibold text-base-content/70">
                Selecciona una categoría
              </h3>
              <p class="text-base-content/50 mt-2">
                Elige una categoría de la lista para editarla o crea una nueva
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Add Category Modal -->
      <CategoryAddModal
        v-if="showAddModal"
        :existing-ids="existingIds"
        @close="showAddModal = false"
        @create="handleCreateCategory"
      />

      <!-- Delete Confirmation Modal -->
      <dialog v-if="categoryToDelete" class="modal modal-open">
        <div class="modal-box">
          <h3 class="font-bold text-lg text-error">
            Confirmar Eliminación
          </h3>
          <p class="py-4">
            ¿Estás seguro de que quieres eliminar la categoría
            <strong>"{{ categoryToDelete.name }}"</strong>?
          </p>

          <div v-if="categoryToDelete.message_count && categoryToDelete.message_count > 0" class="alert alert-warning mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>
              Esta categoría tiene <strong>{{ categoryToDelete.message_count }}</strong> mensajes asociados.
              Los mensajes quedarán sin categoría.
            </span>
          </div>

          <div class="modal-action">
            <button
              class="btn btn-ghost"
              @click="categoryToDelete = null"
            >
              Cancelar
            </button>
            <button
              class="btn btn-error"
              @click="confirmDelete"
              :disabled="isSaving"
            >
              <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
              Eliminar
            </button>
          </div>
        </div>
        <form method="dialog" class="modal-backdrop">
          <button @click="categoryToDelete = null">close</button>
        </form>
      </dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { FolderIcon, PlusIcon } from '@heroicons/vue/24/outline'
import { useCategoryEditor, type Category, type CategoryUpdate } from './composables/useCategoryEditor'
import CategoryList from './components/CategoryList.vue'
import CategoryForm from './components/CategoryForm.vue'
import CategoryAddModal from './components/CategoryAddModal.vue'
import SettingsNav from '../SettingsNav.vue'

// Composable
const {
  categories,
  selectedCategory,
  isLoading,
  isSaving,
  error,
  successMessage,
  sortedCategories,
  loadCategories,
  selectCategory,
  createCategory,
  updateCategory,
  deleteCategory,
  reorderCategories,
} = useCategoryEditor()

// Local state
const showAddModal = ref(false)
const categoryToDelete = ref<Category | null>(null)

// Computed
const existingIds = computed(() => categories.value.map(c => c.id))

// Handlers
const handleSelectCategory = (category: Category) => {
  selectCategory(category)
}

const handleSaveCategory = async (updates: CategoryUpdate) => {
  if (!selectedCategory.value) return

  try {
    await updateCategory(selectedCategory.value.id, updates)
  } catch (e) {
    console.error('Failed to save category:', e)
  }
}

const handleCancelEdit = () => {
  // Reset to original values
  if (selectedCategory.value) {
    const category = categories.value.find(c => c.id === selectedCategory.value?.id)
    if (category) {
      selectCategory(category)
    }
  }
}

const handleDeleteCategory = (categoryId: string) => {
  const category = categories.value.find(c => c.id === categoryId)
  if (category) {
    categoryToDelete.value = category
  }
}

const confirmDelete = async () => {
  if (!categoryToDelete.value) return

  try {
    const hasMessages = (categoryToDelete.value.message_count || 0) > 0
    await deleteCategory(categoryToDelete.value.id, hasMessages)
    categoryToDelete.value = null
  } catch (e) {
    console.error('Failed to delete category:', e)
  }
}

const handleReorder = async (newOrder: string[]) => {
  try {
    await reorderCategories(newOrder)
  } catch (e) {
    console.error('Failed to reorder categories:', e)
  }
}

const handleCreateCategory = async (categoryData: any) => {
  try {
    const newCategory = await createCategory(categoryData)
    showAddModal.value = false
    if (newCategory) {
      selectCategory(newCategory)
    }
  } catch (e) {
    console.error('Failed to create category:', e)
  }
}

// Load categories on mount
onMounted(() => {
  loadCategories()
})
</script>
