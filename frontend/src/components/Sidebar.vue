<template>
  <div class="w-80 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200">
      <button
        @click="$emit('new-chat')"
        class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        <Plus :size="18" />
        New Chat
      </button>
    </div>

    <!-- Conversations List -->
    <div class="flex-1 overflow-y-auto p-3">
      <div v-if="conversations.length === 0" class="text-center py-8 text-gray-400">
        <MessageSquare :size="48" class="mx-auto mb-2 opacity-50" />
        <p class="text-sm">No conversations yet</p>
        <p class="text-xs mt-1">Start a new chat to begin</p>
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="conversation in conversations"
          :key="conversation.name"
          :class="[
            'group relative p-3 rounded-lg cursor-pointer transition-all',
            conversation.name === currentConversation?.name
              ? 'bg-blue-50 border-2 border-blue-200'
              : 'bg-white border border-gray-200 hover:border-blue-200 hover:shadow-sm'
          ]"
          @click="$emit('select-conversation', conversation)"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <MessageSquare :size="16" class="text-gray-400 flex-shrink-0" />
                <h3 class="text-sm font-medium text-gray-900 truncate">
                  {{ conversation.title || 'New Conversation' }}
                </h3>
              </div>
              
              <div class="flex items-center gap-2 text-xs text-gray-500">
                <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">
                  {{ conversation.ai_provider }}
                </span>
                <span>{{ formatDate(conversation.created_at || conversation.creation) }}</span>
              </div>
            </div>

            <!-- Delete Button -->
            <button
              @click.stop="$emit('delete-conversation', conversation.name)"
              class="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-50 rounded"
            >
              <Trash2 :size="16" class="text-red-500" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, MessageSquare, Trash2 } from 'lucide-vue-next'

defineProps({
  conversations: {
    type: Array,
    default: () => [],
  },
  currentConversation: {
    type: Object,
    default: null,
  },
})

defineEmits(['new-chat', 'select-conversation', 'delete-conversation'])

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return 'Today'
  } else if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else {
    return date.toLocaleDateString()
  }
}
</script>
