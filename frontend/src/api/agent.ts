import request from '@/utils/request'
import type { ApiResponse } from '@/types/common'
import { getToken } from '@/utils/auth'

interface AgentEvent {
  type: 'tool_call' | 'tool_result' | 'chunk' | 'error' | 'done'
  content: string
  tool_name: string
  tool_args: Record<string, any>
  iteration: number
}

interface ToolInfo {
  name: string
  description: string
  tags: string[]
  parameters: Record<string, any>
}

interface SkillInfo {
  id: string
  name: string
  description: string
  success_rate: number
  trigger_patterns: string[]
}

export const agentApi = {
  /** Stream agent chat via SSE */
  async chat(
    query: string,
    onEvent: (event: AgentEvent) => void,
    options?: { enableTools?: boolean; model?: string },
  ): Promise<void> {
    const token = getToken()
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'

    const response = await fetch(`${baseUrl}/agent/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        query,
        enable_tools: options?.enableTools ?? true,
        model: options?.model ?? 'deepseek-chat',
      }),
    })

    if (!response.ok) {
      throw new Error(`Agent request failed: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data: ')) continue
        const data = trimmed.slice(6)
        if (data === '[DONE]') return

        try {
          const event: AgentEvent = JSON.parse(data)
          onEvent(event)
        } catch {
          // Skip malformed events
        }
      }
    }
  },

  /** List available agent tools */
  listTools(): Promise<ApiResponse<ToolInfo[]>> {
    return request.get('/agent/tools')
  },

  /** List learned skills */
  listSkills(): Promise<ApiResponse<SkillInfo[]>> {
    return request.get('/agent/skills')
  },
}
