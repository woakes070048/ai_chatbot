<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <Sidebar
      :conversations="conversations"
      :current-conversation="currentConversation"
      @new-chat="handleNewChat"
      @select-conversation="handleSelectConversation"
      @delete-conversation="handleDeleteConversation"
    />

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <ChatHeader
        :conversation="currentConversation"
        :ai-provider="selectedProvider"
        @change-provider="handleChangeProvider"
      />

      <!-- Messages Area -->
      <div
        ref="messagesContainer"
        class="flex-1 overflow-y-auto px-4 py-6 space-y-4"
      >
        <ChatMessage
          v-for="message in messages"
          :key="message.name"
          :message="message"
        />
        
        <div v-if="isLoading" class="flex justify-start">
          <div class="bg-white rounded-2xl px-6 py-4 shadow-sm border border-gray-200 max-w-3xl">
            <TypingIndicator />
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <ChatInput
        :disabled="isLoading || !currentConversation"
        @send="handleSendMessage"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import ChatHeader from '../components/ChatHeader.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'
import TypingIndicator from '../components/TypingIndicator.vue'
import { chatAPI } from '../utils/api'

const conversations = ref([])
const currentConversation = ref(null)
const messages = ref([])
const isLoading = ref(false)
const selectedProvider = ref('OpenAI')
const messagesContainer = ref(null)

onMounted(async () => {
  await loadConversations()
  // Auto-create first conversation if none exist
  if (conversations.value.length === 0) {
    await handleNewChat()
  }
})

const loadConversations = async () => {
  try {
    const response = await chatAPI.getConversations()
    if (response.success) {
      conversations.value = response.conversations
    }
  } catch (error) {
    console.error('Error loading conversations:', error)
  }
}

const handleNewChat = async () => {
  try {
    const response = await chatAPI.createConversation(
      'New Chat',
      selectedProvider.value
    )
    if (response.success) {
      await loadConversations()
      // Find the newly created conversation in the list
      const newConv = conversations.value.find(c => c.name === response.conversation_id)
      if (newConv) {
        currentConversation.value = newConv
        messages.value = []
      } else {
        // Fallback: use the data from response
        currentConversation.value = response.data || {
          name: response.conversation_id,
          title: 'New Chat',
          ai_provider: selectedProvider.value
        }
        messages.value = []
      }
    }
  } catch (error) {
    console.error('Error creating conversation:', error)
  }
}

const handleSelectConversation = async (conversation) => {
  currentConversation.value = conversation
  await loadMessages(conversation.name)
}

const loadMessages = async (conversationId) => {
  try {
    const response = await chatAPI.getConversationMessages(conversationId)
    if (response.success) {
      messages.value = response.messages
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('Error loading messages:', error)
  }
}

const handleSendMessage = async (content) => {
  if (!currentConversation.value || !content.trim()) return

  // Add user message optimistically
  const userMessage = {
    role: 'user',
    content: content,
    timestamp: new Date().toISOString(),
  }
  messages.value.push(userMessage)
  await nextTick()
  scrollToBottom()

  isLoading.value = true

  try {
    const response = await chatAPI.sendMessage(
      currentConversation.value.name,
      content
    )

    if (response.success) {
      // Add assistant message
      messages.value.push({
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        tokens_used: response.tokens_used,
      })
      
      // Reload to get saved messages
      await loadMessages(currentConversation.value.name)
      await loadConversations()
    }
  } catch (error) {
    console.error('Error sending message:', error)
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const handleDeleteConversation = async (conversationId) => {
  try {
    const response = await chatAPI.deleteConversation(conversationId)
    if (response.success) {
      await loadConversations()
      if (currentConversation.value?.name === conversationId) {
        currentConversation.value = null
        messages.value = []
      }
    }
  } catch (error) {
    console.error('Error deleting conversation:', error)
  }
}

const handleChangeProvider = (provider) => {
  selectedProvider.value = provider
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Auto-scroll on new messages
watch(messages, () => {
  nextTick(() => scrollToBottom())
}, { deep: true })
</script>
