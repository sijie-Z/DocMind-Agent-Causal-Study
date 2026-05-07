import request from '@/utils/request'
import { useUserStore } from '@/stores/user'
import type { ChatMessage } from '@/types/chat'
import type { ApiResponse } from '@/types/common'

// 发送消息
export function sendMessage(data: { message: string; conversationId?: number }) {
  const orgId = useUserStore().currentOrgId || 1
  return request.post<ApiResponse<{
    response: string
    sources: any[]
  }>>('/chat/completions', {
    messages: [
        { role: 'user', content: data.message }
    ],
    organization_id: orgId,
    stream: true
  })
}

// 获取对话消息详情
export function getConversationMessages(conversationId: string) {
  return request.get<ApiResponse<{
    id: string
    title: string
    messages: ChatMessage[]
    created_at: string
  }>>(`/chat/conversations/${conversationId}`)
}

// 解除文档绑定
export function unbindConversationDocs(conversationId: string) {
  return request.post<ApiResponse>(`/chat/conversations/${conversationId}/unbind-docs`)
}

// 消息反馈 (点赞/点踩)
export function updateMessageFeedback(messageId: string | number, feedback: number, note?: string) {
  return request.post<ApiResponse>(`/chat/messages/${messageId}/feedback`, {
    feedback,
    note
  })
}

// 清空会话消息
export function clearConversationMessages(conversationId: string) {
  return request.delete<ApiResponse>(`/chat/conversations/${conversationId}/clear`)
}
