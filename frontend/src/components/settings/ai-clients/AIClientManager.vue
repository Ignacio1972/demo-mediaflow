<template>
  <div class="ai-client-manager min-h-screen bg-base-100">
    <SettingsNav />
    <div class="p-6">
      <div class="container mx-auto max-w-7xl">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 class="text-3xl font-bold text-primary">
              Clientes
            </h1>
            <p class="text-sm text-base-content/60 mt-1">
              Gestiona clientes y contextos de IA para generacion de anuncios
            </p>
          </div>
          <button
            @click="showAddModal = true"
            class="btn btn-primary"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Agregar Cliente
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
          <!-- Left: Client List (1 column) -->
          <div class="lg:col-span-1">
            <AIClientList
              :clients="clients"
              :selected-client="selectedClient"
              :is-loading="isLoading"
              @select="handleSelectClient"
            />
          </div>

          <!-- Right: Client Editor (2 columns) -->
          <div class="lg:col-span-2">
            <AIClientEditor
              v-if="selectedClient"
              :client="selectedClient"
              :is-saving="isSaving"
              @save="handleSaveClient"
              @cancel="handleCancelEdit"
              @delete="handleDeleteClient"
              @set-default="handleSetDefault"
            />

            <!-- Empty State -->
            <div v-else class="card bg-base-100 shadow-xl">
              <div class="card-body items-center text-center py-16">
                <div class="text-6xl mb-4">👈</div>
                <h3 class="text-xl font-semibold text-base-content/70">
                  Selecciona un cliente
                </h3>
                <p class="text-base-content/50 mt-2">
                  Elige un cliente de la lista para ver y editar su configuracion
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Add Client Modal -->
        <AIClientAddModal
          v-if="showAddModal"
          @close="showAddModal = false"
          @create="handleCreateClient"
        />

        <!-- Delete Confirmation Modal -->
        <dialog v-if="clientToDelete" class="modal modal-open">
          <div class="modal-box">
            <h3 class="font-bold text-lg text-error">
              Confirmar Eliminacion
            </h3>
            <p class="py-4">
              Estas seguro de que quieres eliminar el cliente
              <strong>{{ clientToDelete.name }}</strong>?
            </p>
            <p class="text-sm text-base-content/60">
              Esta accion no se puede deshacer.
            </p>
            <div class="modal-action">
              <button @click="clientToDelete = null" class="btn btn-ghost">
                Cancelar
              </button>
              <button @click="confirmDelete" class="btn btn-error">
                Eliminar
              </button>
            </div>
          </div>
          <form method="dialog" class="modal-backdrop">
            <button @click="clientToDelete = null">close</button>
          </form>
        </dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SettingsNav from '../SettingsNav.vue'
import AIClientList from './components/AIClientList.vue'
import AIClientEditor from './components/AIClientEditor.vue'
import AIClientAddModal from './components/AIClientAddModal.vue'
import { useAIClientManager } from './composables/useAIClientManager'
import type { AIClient } from '@/composables/useAIClients'

const {
  clients,
  selectedClient,
  isLoading,
  isSaving,
  error,
  successMessage,
  loadClients,
  selectClient,
  createClient,
  updateClient,
  deleteClient,
  setActiveClient
} = useAIClientManager()

// Local state
const showAddModal = ref(false)
const clientToDelete = ref<AIClient | null>(null)

// Handlers
function handleSelectClient(client: AIClient) {
  selectClient(client)
}

async function handleSaveClient(updates: Partial<AIClient>) {
  if (!selectedClient.value) return
  try {
    await updateClient(selectedClient.value.id, updates)
  } catch (e) {
    console.error('Failed to save client:', e)
  }
}

function handleCancelEdit() {
  // Reset is handled in the editor component
}

function handleDeleteClient(clientId: string) {
  const client = clients.value.find(c => c.id === clientId)
  if (client) {
    clientToDelete.value = client
  }
}

async function confirmDelete() {
  if (!clientToDelete.value) return
  await deleteClient(clientToDelete.value.id)
  clientToDelete.value = null
}

async function handleSetDefault(clientId: string) {
  await setActiveClient(clientId)
}

async function handleCreateClient(data: Partial<AIClient>) {
  try {
    const newClient = await createClient(data)
    if (newClient) {
      selectClient(newClient)
    }
    showAddModal.value = false
  } catch (e) {
    console.error('Failed to create client:', e)
  }
}

onMounted(() => {
  loadClients()
})
</script>
