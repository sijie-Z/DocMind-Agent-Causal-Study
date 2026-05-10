import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Conversation } from '@/types/chat'
import { unbindConversationDocs } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)

  // 方法
  const setCurrentConversation = (conversation: Conversation | null) => {
    currentConversation.value = conversation
  }

  const unbindDocuments = async () => {
    if (currentConversation.value?.id) {
      await unbindConversationDocs(currentConversation.value.id.toString())
      if (currentConversation.value.settings) {
        currentConversation.value.settings.bound_document_ids = []
      }
    }
  }

  return {
    // 状态
    conversations,
    currentConversation,

    // 方法
    setCurrentConversation,
    unbindDocuments
  }
})
