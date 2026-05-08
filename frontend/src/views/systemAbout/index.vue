<template>
  <div class="h-full overflow-y-auto p-6 lg:p-8 bg-gray-50 dark:bg-gray-950">
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-2">
        <div class="w-12 h-12 rounded-2xl bg-emerald-500 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-emerald-500/25">D</div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">DocMind</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">Enterprise RAG Knowledge Base System</p>
        </div>
        <div class="ml-auto">
          <n-tag type="success" round size="small">v2.0.0</n-tag>
        </div>
      </div>

      <!-- System Info -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">System Information</h2>
        </div>
        <div class="p-6">
          <n-descriptions :column="1" bordered label-placement="left" class="rounded-xl overflow-hidden">
            <n-descriptions-item label="Product">DocMind — Enterprise RAG Knowledge Base</n-descriptions-item>
            <n-descriptions-item label="Architecture">RAG (Retrieval-Augmented Generation) with Agent</n-descriptions-item>
            <n-descriptions-item label="Backend">FastAPI + SQLAlchemy(async) + MySQL 8 + Redis + Elasticsearch 8 + Kafka + MinIO</n-descriptions-item>
            <n-descriptions-item label="Frontend">Vue 3 + TypeScript + Vite + Naive UI + Pinia</n-descriptions-item>
            <n-descriptions-item label="AI Engine">DeepSeek API + OpenAI-compatible Embedding + LangChain</n-descriptions-item>
            <n-descriptions-item label="Agent System">ReAct loop with tool registry, context engine, and skill learning</n-descriptions-item>
            <n-descriptions-item label="Security">JWT + RBAC + Organization-level multi-tenancy</n-descriptions-item>
          </n-descriptions>
        </div>
      </div>

      <!-- Architecture Highlights -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">Architecture Highlights</h2>
        </div>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="item in highlights" :key="item.title" class="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/30">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">{{ item.title }}</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">{{ item.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Data Flow -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">Data Flow</h2>
        </div>
        <div class="p-6">
          <div class="flex flex-wrap items-center gap-2 text-sm">
            <span v-for="(step, i) in dataFlow" :key="i" class="flex items-center gap-2">
              <span class="px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 font-medium text-xs">{{ step }}</span>
              <span v-if="i < dataFlow.length - 1" class="text-gray-300 dark:text-gray-600">&rarr;</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center py-4">
        <p class="text-xs text-gray-400 dark:text-gray-500">
          Built with FastAPI, Vue 3, Elasticsearch, and DeepSeek LLM
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NDescriptions, NDescriptionsItem, NTag } from 'naive-ui'

const highlights = [
  { title: 'Hybrid Retrieval', desc: 'Combines BM25 keyword search with vector semantic search using Reciprocal Rank Fusion (RRF) for maximum recall.' },
  { title: 'Agent Architecture', desc: 'ReAct-style autonomous loop inspired by hermes-agent. Self-registering tools, context compression, and skill learning.' },
  { title: 'Semantic Caching', desc: 'Embedding-based answer cache eliminates redundant LLM calls for similar queries, reducing latency and cost.' },
  { title: 'Circuit Breaker', desc: 'Fault tolerance for external services (LLM, ES, DB). Automatic fallback prevents cascading failures.' },
  { title: 'Multi-tenant RBAC', desc: 'Organization-level data isolation with role-based access control. Supports fine-grained permission management.' },
  { title: 'Real-time Streaming', desc: 'WebSocket and SSE dual-mode streaming for chat responses. Real-time notification push via dedicated WS channel.' },
]

const dataFlow = [
  'Upload',
  'MinIO + DB',
  'Kafka',
  'Worker',
  'Parse & Chunk',
  'Embedding',
  'Elasticsearch',
  'User Query',
  'Hybrid Search',
  'Rerank',
  'DeepSeek LLM',
  'Stream Response',
]
</script>
