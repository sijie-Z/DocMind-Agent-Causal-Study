import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useChatStore } from '../chat'

vi.mock('@/api/chat', () => ({
  unbindConversationDocs: vi.fn().mockResolvedValue({ data: { success: true } }),
}))

describe('useChatStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('has correct initial state', () => {
    const store = useChatStore()
    expect(store.conversations).toEqual([])
    expect(store.currentConversation).toBeNull()
  })

  it('setCurrentConversation sets the conversation', () => {
    const store = useChatStore()
    const conv = { id: '1', title: 'Test', userId: 1, createdAt: '', updatedAt: '' }
    store.setCurrentConversation(conv)
    expect(store.currentConversation).toEqual(conv)
  })

  it('setCurrentConversation(null) clears the conversation', () => {
    const store = useChatStore()
    store.setCurrentConversation({ id: '1', title: 'Test', userId: 1, createdAt: '', updatedAt: '' })
    store.setCurrentConversation(null)
    expect(store.currentConversation).toBeNull()
  })

  it('unbindDocuments clears bound_document_ids', async () => {
    const store = useChatStore()
    store.setCurrentConversation({
      id: '1', title: 'Test', userId: 1, createdAt: '', updatedAt: '',
      settings: { bound_document_ids: ['doc1', 'doc2'] }
    })
    await store.unbindDocuments()
    expect(store.currentConversation!.settings!.bound_document_ids).toEqual([])
  })
})
