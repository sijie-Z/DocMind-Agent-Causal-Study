<template>
  <div class="flex h-full w-full bg-gray-50 dark:bg-gray-950 overflow-hidden">
    <div class="flex-1 flex flex-col h-full max-w-4xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-emerald-500/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h1 class="text-base font-semibold text-gray-900 dark:text-white">Agent Mode</h1>
            <p class="text-xs text-gray-500 dark:text-gray-400">ReAct reasoning with tool calling</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <n-tag v-if="toolCount > 0" size="small" type="success">{{ toolCount }} tools</n-tag>
          <n-button size="small" @click="clearMessages">Clear</n-button>
        </div>
      </div>

      <!-- Messages -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center">
          <div class="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">DocMind Agent</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 max-w-md">
            I can search your knowledge base, analyze documents, and use tools to answer complex questions. Ask me anything.
          </p>
          <div class="mt-6 grid grid-cols-2 gap-2 max-w-md">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              @click="sendMessage(suggestion)"
              class="text-left px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 text-xs text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>

        <template v-for="(msg, idx) in messages" :key="idx">
          <!-- User message -->
          <div v-if="msg.role === 'user'" class="flex justify-end">
            <div class="max-w-[80%] px-4 py-2.5 rounded-2xl rounded-br-md bg-emerald-500 text-white text-sm">
              {{ msg.content }}
            </div>
          </div>

          <!-- Agent events -->
          <div v-else class="space-y-2">
            <!-- Tool calls -->
            <template v-for="(event, eIdx) in msg.events" :key="eIdx">
              <div v-if="event.type === 'tool_call'" class="flex items-start gap-2">
                <div class="flex-shrink-0 w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center mt-0.5">
                  <svg class="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-xs font-medium text-blue-600 dark:text-blue-400">{{ event.tool_name }}</span>
                    <n-tag size="tiny" :bordered="false" type="info">iteration {{ event.iteration }}</n-tag>
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 rounded-lg px-3 py-2 font-mono">
                    {{ formatToolArgs(event.tool_args) }}
                  </div>
                </div>
              </div>

              <div v-else-if="event.type === 'tool_result'" class="flex items-start gap-2 ml-4">
                <div class="flex-shrink-0 w-5 h-5 rounded bg-green-500/10 flex items-center justify-center mt-0.5">
                  <svg class="w-3 h-3 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="text-xs text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800/50 rounded-lg px-3 py-2 whitespace-pre-wrap"
                    :class="{ 'max-h-40 overflow-y-auto': !expandedEvents[eIdx] }">
                    {{ expandedEvents[eIdx] ? event.content : truncateResult(event.content) }}
                  </div>
                  <button
                    v-if="isResultLong(event.content)"
                    @click="toggleExpand(eIdx)"
                    class="mt-1 text-xs text-blue-500 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                  >
                    {{ expandedEvents[eIdx] ? '收起' : '展开' }}
                  </button>
                </div>
              </div>

              <div v-else-if="event.type === 'error'" class="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-50 dark:bg-red-900/20 text-xs text-red-600 dark:text-red-400">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ event.content }}
              </div>
            </template>

            <!-- Final answer -->
            <div v-if="msg.content" class="flex items-start gap-2">
              <div class="flex-shrink-0 w-7 h-7 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <svg class="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div class="flex-1 prose prose-sm dark:prose-invert max-w-none">
                <Markdown :content="msg.content" />
              </div>
            </div>

            <!-- Loading indicator -->
            <div v-if="msg.loading" class="flex items-center gap-2 text-xs text-gray-400">
              <div class="flex gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style="animation-delay: 300ms"></span>
              </div>
              <span v-if="msg.currentTool">Calling {{ msg.currentTool }}...</span>
              <span v-else>Thinking...</span>
            </div>
          </div>
        </template>
      </div>

      <!-- Input -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-800">
        <div class="flex gap-2">
          <input
            v-model="inputMessage"
            @keydown.enter.exact.prevent="sendMessage()"
            placeholder="Ask the agent anything..."
            class="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition-all"
          />
          <button
            @click="sendMessage()"
            :disabled="!inputMessage.trim() || isLoading"
            class="px-4 py-2.5 rounded-xl bg-emerald-500 text-white text-sm font-medium hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed } from 'vue'
import { NTag, NButton } from 'naive-ui'
import Markdown from '@/components/common/Markdown.vue'
import { agentApi } from '@/api/agent'

interface AgentEvent {
  type: 'tool_call' | 'tool_result' | 'chunk' | 'error' | 'done'
  content: string
  tool_name: string
  tool_args: Record<string, any>
  iteration: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  events: AgentEvent[]
  loading: boolean
  currentTool: string
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const toolCount = ref(0)
const messagesContainer = ref<HTMLElement>()
const expandedEvents = ref<Record<number, boolean>>({})

const suggestions = [
  'Search for company policies',
  'What documents are in the knowledge base?',
  'Summarize all uploaded files',
  'Extract key topics from recent docs',
]

const formatToolArgs = (args: Record<string, any>) => {
  if (!args || Object.keys(args).length === 0) return '(no args)'
  return Object.entries(args)
    .map(([k, v]) => `${k}=${typeof v === 'string' ? `"${v.slice(0, 50)}"` : v}`)
    .join(', ')
}

const truncateResult = (text: string) => {
  if (!text) return ''
  return text.length > 300 ? text.slice(0, 300) + '...' : text
}

const isResultLong = (text: string) => !!text && text.length > 300

const toggleExpand = (eventKey: number) => {
  expandedEvents.value[eventKey] = !expandedEvents.value[eventKey]
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const clearMessages = () => {
  messages.value = []
  toolCount.value = 0
  expandedEvents.value = {}
}

const sendMessage = async (text?: string) => {
  const query = text || inputMessage.value.trim()
  if (!query || isLoading.value) return

  inputMessage.value = ''

  // Add user message
  messages.value.push({
    role: 'user',
    content: query,
    events: [],
    loading: false,
    currentTool: '',
  })

  // Add assistant placeholder
  const assistantIdx = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    events: [],
    loading: true,
    currentTool: '',
  })

  isLoading.value = true
  scrollToBottom()

  try {
    await agentApi.chat(query, (event: AgentEvent) => {
      const msg = messages.value[assistantIdx]
      if (!msg) return

      if (event.type === 'tool_call') {
        msg.events.push(event)
        msg.currentTool = event.tool_name
        toolCount.value++
      } else if (event.type === 'tool_result') {
        msg.events.push(event)
        msg.currentTool = ''
      } else if (event.type === 'chunk') {
        msg.content += event.content
      } else if (event.type === 'error') {
        msg.events.push(event)
        msg.loading = false
      } else if (event.type === 'done') {
        msg.loading = false
      }
      scrollToBottom()
    })
  } catch (e: unknown) {
    const errorMsg = e instanceof Error ? e.message : String(e)
    const msg = messages.value[assistantIdx]
    if (msg) {
      msg.content = `Error: ${errorMsg || 'Failed to connect to agent'}`
      msg.loading = false
    }
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  // Check for available tools
  agentApi.listTools().then(res => {
    if (res.data) toolCount.value = res.data.length
  }).catch(() => {})
})
</script>
