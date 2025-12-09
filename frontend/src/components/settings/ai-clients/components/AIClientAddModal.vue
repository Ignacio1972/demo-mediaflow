<template>
  <dialog class="modal modal-open">
    <div class="modal-box w-full max-w-lg">
      <h3 class="font-bold text-lg mb-4">
        Agregar Nuevo Cliente IA
      </h3>

      <form @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <!-- ID (optional) -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">ID (opcional)</span>
            </label>
            <input
              v-model="formData.id"
              type="text"
              class="input input-bordered"
              placeholder="mi_cliente (se genera automaticamente si se deja vacio)"
              pattern="^[a-z0-9_]*$"
            />
            <label class="label">
              <span class="label-text-alt">Solo letras minusculas, numeros y guion bajo</span>
            </label>
          </div>

          <!-- Name -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Nombre *</span>
            </label>
            <input
              v-model="formData.name"
              type="text"
              class="input input-bordered"
              placeholder="Mi Cliente"
              required
            />
          </div>

          <!-- Category -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Categoria</span>
            </label>
            <select v-model="formData.category" class="select select-bordered">
              <option value="general">General</option>
              <option value="supermercado">Supermercado</option>
              <option value="mall">Centro Comercial</option>
              <option value="retail">Retail</option>
              <option value="servicios">Servicios</option>
              <option value="otro">Otro</option>
            </select>
          </div>

          <!-- Context -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Contexto de IA *</span>
            </label>
            <textarea
              v-model="formData.context"
              class="textarea textarea-bordered h-32"
              placeholder="Describe el negocio, target, tono y estilo para los anuncios..."
              required
              minlength="10"
            ></textarea>
            <label class="label">
              <span class="label-text-alt">Minimo 10 caracteres</span>
              <span class="label-text-alt">{{ formData.context.length }} / 5000</span>
            </label>
          </div>
        </div>

        <!-- Actions -->
        <div class="modal-action">
          <button type="button" @click="close" class="btn btn-ghost">
            Cancelar
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="!isValid"
          >
            Crear Cliente
          </button>
        </div>
      </form>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="close">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import type { AIClient } from '@/composables/useAIClients'

const emit = defineEmits<{
  close: []
  create: [data: Partial<AIClient>]
}>()

const formData = reactive({
  id: '',
  name: '',
  category: 'general',
  context: ''
})

const isValid = computed(() => {
  return formData.name.trim().length > 0 && formData.context.trim().length >= 10
})

function handleSubmit() {
  if (!isValid.value) return

  const data: Partial<AIClient> = {
    name: formData.name.trim(),
    category: formData.category,
    context: formData.context.trim(),
    active: true
  }

  if (formData.id.trim()) {
    data.id = formData.id.trim()
  }

  emit('create', data)
  close()
}

function close() {
  emit('close')
}
</script>
