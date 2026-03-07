<script setup lang="ts">
import { ref } from 'vue'
import { Send } from 'lucide-vue-next'
import { useChat } from '@/composables/useChat'

const props = defineProps<{ disabled: boolean }>()
const { sendMessage } = useChat()
const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

async function handleSend() {
  if (!inputText.value.trim() || props.disabled) return
  const text = inputText.value
  inputText.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  await sendMessage(text)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function autoResize(e: Event) {
  const target = e.target as HTMLTextAreaElement
  target.style.height = 'auto'
  target.style.height = Math.min(target.scrollHeight, 120) + 'px'
}
</script>

<template>
  <div class="border-t border-base-300 px-4 py-3">
    <div class="flex items-end gap-2">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        @keydown="handleKeydown"
        @input="autoResize"
        :disabled="disabled"
        placeholder="Escribe un mensaje..."
        rows="1"
        class="textarea textarea-bordered flex-1 resize-none leading-5
               min-h-[40px] max-h-[120px] focus:outline-none focus:border-primary"
      />
      <button
        @click="handleSend"
        :disabled="!inputText.trim() || disabled"
        class="btn btn-primary btn-sm h-10 w-10 p-0 flex-shrink-0"
      >
        <Send class="w-4 h-4" />
      </button>
    </div>
    <p class="text-[10px] text-base-content/30 mt-1 text-center">
      Enter para enviar, Shift+Enter para nueva linea
    </p>
  </div>
</template>
