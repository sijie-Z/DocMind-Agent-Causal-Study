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
    expect(store.messages).toEqual([])
    expect(store.isLoading).toBe(false)
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

  it('addMessage appends to messages', () => {
    const store = useChatStore()
    const msg = { id: '1', content: 'hello', messageType: 'user' as const, conversationId: '1', createdAt: '' }
    store.addMessage(msg)
    expect(store.messages).toHaveLength(1)
    expect(store.messages[0].content).toBe('hello')
  })

  it('updateMessage merges updates at the given index', () => {
    const store = useChatStore()
    store.addMessage({ id: '1', content: 'old', messageType: 'user' as const, conversationId: '1', createdAt: '' })
    store.updateMessage(0, { content: 'new' })
    expect(store.messages[0].content).toBe('new')
    expect(store.messages[0].id).toBe('1')
  })

  it('updateMessage ignores invalid index', () => {
    const store = useChatStore()
    store.addMessage({ id: '1', content: 'hello', messageType: 'user' as const, conversationId: '1', createdAt: '' })
    store.updateMessage(99, { content: 'nope' })
    expect(store.messages[0].content).toBe('hello')
  })

  it('clearMessages empties the messages array', () => {
    const store = useChatStore()
    store.addMessage({ id: '1', content: 'a', messageType: 'user' as const, conversationId: '1', createdAt: '' })
    store.addMessage({ id: '2', content: 'b', messageType: 'assistant' as const, conversationId: '1', createdAt: '' })
    store.clearMessages()
    expect(store.messages).toEqual([])
  })

  it('setLoading toggles the loading state', () => {
    const store = useChatStore()
    store.setLoading(true)
    expect(store.isLoading).toBe(true)
    store.setLoading(false)
    expect(store.isLoading).toBe(false)
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
