export interface ChatMessage {
  id?: string | number
  content: string
  messageType: 'user' | 'assistant'
  conversationId: string | number
  createdAt?: string
  sources?: KnowledgeSource[]
  files?: AttachedFile[]
  feedback?: number
  feedbackNote?: string
  isCached?: boolean
  thinking?: string
}

export interface AttachedFile {
  name: string
  status: 'uploading' | 'parsing' | 'indexing' | 'done' | 'error'
  id?: string
  errorMsg?: string
  _originalFile?: File
  _errorExpanded?: boolean
  progress?: number
  statusDetail?: string
  parsedContent?: string
}

export interface Conversation {
  id: string | number
  title: string
  userId: number
  createdAt: string
  updatedAt: string
  messageCount?: number
  settings?: {
    bound_document_ids?: string[]
  }
}

export interface KnowledgeSource {
  fileId: number
  filename: string
  relevanceScore: number
  snippet?: string
  content?: string
  chunkIndex: number
  hasKeyword?: boolean
  hasVector?: boolean
  rewriteHits?: number
  freshFactor?: number
}

export interface RetrievalDebugData {
  strategy?: string
  query?: string
  cache_hit?: boolean
  cache_type?: string
  keyword_top?: DebugHit[]
  vector_top?: DebugHit[]
  rrf_result?: DebugHit[]
  rerank_result?: DebugHit[]
  rerank_reorder?: { id: string; filename: string }[]
  total_results?: number
  elapsed_ms?: number
  note?: string
  stages?: Record<string, RetrievalDebugData>
  /** The actual context content sent to the LLM */
  final_context?: FinalContextItem[]
}

export interface FinalContextItem {
  rank: number
  filename: string
  score: number
  content: string
}

export interface DebugHit {
  id: string
  filename: string
  score: number
  keyword_rank?: number | null
  vector_rank?: number | null
  keyword_score?: number | null
  vector_score?: number | null
  rewrite_hits?: number
  has_keyword?: boolean
  has_vector?: boolean
  snippet?: string
}
