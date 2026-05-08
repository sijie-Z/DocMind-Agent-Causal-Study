<template>
  <div class="landing min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors duration-500">
    <!-- Hero Section -->
    <header class="relative overflow-hidden">
      <!-- Background decoration -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-emerald-400/5 dark:bg-emerald-500/5 blur-3xl"></div>
        <div class="absolute -bottom-20 -left-20 w-72 h-72 rounded-full bg-blue-400/5 dark:bg-blue-500/5 blur-3xl"></div>
      </div>

      <nav class="relative z-10 max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-emerald-500/25">D</div>
          <span class="text-base font-semibold text-slate-900 dark:text-white tracking-tight">DocMind</span>
        </div>
        <div class="flex items-center gap-3">
          <button @click="goToLogin" class="text-sm text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors">Sign in</button>
          <button @click="goToRegister" class="px-4 py-2 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-sm font-medium hover:opacity-90 transition-opacity">Get started</button>
        </div>
      </nav>

      <div class="relative z-10 max-w-6xl mx-auto px-6 pt-16 pb-24 md:pt-24 md:pb-32 text-center">
        <div class="inline-flex items-center gap-2 rounded-full border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-900/30 px-3 py-1 text-xs text-emerald-600 dark:text-emerald-400 mb-6">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Agent-powered knowledge base
        </div>
        <h1 class="text-4xl md:text-6xl font-bold text-slate-900 dark:text-white tracking-tight leading-tight mb-6">
          Your documents,<br>
          <span class="bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">intelligent answers</span>
        </h1>
        <p class="text-lg text-slate-500 dark:text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload documents, build a knowledge base, and ask questions in natural language.
          The Agent searches, reasons, and cites sources — not just keywords.
        </p>
        <div class="flex flex-wrap justify-center gap-3">
          <button @click="goToRegister" class="px-6 py-3 rounded-xl bg-emerald-500 text-white font-semibold shadow-lg shadow-emerald-500/25 hover:bg-emerald-600 transition-colors">
            Start for free
          </button>
          <button @click="goToLogin" class="px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            Sign in
          </button>
        </div>
      </div>
    </header>

    <!-- How it works -->
    <section class="max-w-6xl mx-auto px-6 pb-20">
      <div class="text-center mb-12">
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-3">How it works</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400">From documents to answers in four steps</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div v-for="(step, i) in steps" :key="i" class="relative group">
          <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 hover:border-emerald-300 dark:hover:border-emerald-700 transition-colors">
            <div class="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4 group-hover:bg-emerald-50 dark:group-hover:bg-emerald-900/30 transition-colors">
              <span class="text-lg font-bold text-slate-400 dark:text-slate-500 group-hover:text-emerald-500 transition-colors">{{ i + 1 }}</span>
            </div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-2">{{ step.title }}</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{{ step.desc }}</p>
          </div>
          <div v-if="i < steps.length - 1" class="hidden md:block absolute top-1/2 -right-2 w-4 h-px bg-slate-200 dark:bg-slate-700"></div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="max-w-6xl mx-auto px-6 pb-20">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="feature in features" :key="feature.title" class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" :class="feature.iconBg">
            <span class="text-lg">{{ feature.icon }}</span>
          </div>
          <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-2">{{ feature.title }}</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{{ feature.desc }}</p>
        </div>
      </div>
    </section>

    <!-- Agent capability showcase -->
    <section class="max-w-6xl mx-auto px-6 pb-20">
      <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-gradient-to-br from-slate-50 to-white dark:from-slate-900 dark:to-slate-900/50 p-8 md:p-12">
        <div class="flex flex-col md:flex-row items-center gap-10">
          <div class="flex-1">
            <div class="inline-flex items-center gap-2 rounded-full border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-900/30 px-3 py-1 text-xs text-emerald-600 dark:text-emerald-400 mb-4">
              Agent Mode
            </div>
            <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-4">Autonomous reasoning with tools</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
              The Agent doesn't just search — it reasons. It breaks down complex questions, searches multiple times,
              analyzes documents, and composes answers with citations. You can watch its thinking process in real time.
            </p>
            <ul class="space-y-2">
              <li v-for="cap in agentCapabilities" :key="cap" class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <svg class="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ cap }}
              </li>
            </ul>
          </div>
          <div class="w-full md:w-96 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4 font-mono text-xs">
            <div class="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100 dark:border-slate-700">
              <div class="w-2.5 h-2.5 rounded-full bg-red-400"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-yellow-400"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-green-400"></div>
              <span class="ml-2 text-slate-400">Agent</span>
            </div>
            <div class="space-y-2">
              <div class="text-slate-500">> What is our refund policy?</div>
              <div class="flex items-center gap-1.5 text-blue-500">
                <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                Calling search_knowledge_base...
              </div>
              <div class="text-green-500">Found 3 documents (score: 0.89)</div>
              <div class="flex items-center gap-1.5 text-blue-500">
                <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                Calling summarize_document...
              </div>
              <div class="text-slate-600 dark:text-slate-300 border-t border-slate-100 dark:border-slate-700 pt-2 mt-2">
                Based on the company policy [1], refunds are processed within 7 business days...
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-slate-200 dark:border-slate-800 py-8">
      <div class="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded bg-emerald-500 flex items-center justify-center text-white text-xs font-bold">D</div>
          <span class="text-sm text-slate-500 dark:text-slate-400">DocMind</span>
        </div>
        <p class="text-xs text-slate-400 dark:text-slate-500">Enterprise RAG Knowledge Base System</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const goToLogin = () => router.push('/login')
const goToRegister = () => router.push('/register')

const steps = [
  { title: 'Upload', desc: 'Upload PDF, Word, Excel, or text files to the knowledge base.' },
  { title: 'Index', desc: 'Documents are parsed, chunked, and vectorized automatically.' },
  { title: 'Ask', desc: 'Ask questions in natural language. The Agent searches and reasons.' },
  { title: 'Answer', desc: 'Get cited answers with source references and confidence scores.' },
]

const features = [
  { icon: ' ', iconBg: 'bg-emerald-50 dark:bg-emerald-900/30', title: 'Hybrid Search', desc: 'Keyword + vector search with RRF fusion for maximum recall.' },
  { icon: ' ', iconBg: 'bg-blue-50 dark:bg-blue-900/30', title: 'Agent Reasoning', desc: 'Multi-step tool-calling loop. The agent plans, searches, and verifies.' },
  { icon: ' ', iconBg: 'bg-purple-50 dark:bg-purple-900/30', title: 'Enterprise Security', desc: 'JWT auth, RBAC, organization isolation, and audit logging.' },
]

const agentCapabilities = [
  'Multi-step reasoning with tool calling',
  'Hybrid retrieval (keyword + vector + RRF)',
  'Document summarization and analysis',
  'Source attribution with confidence scores',
  'Streaming responses with real-time progress',
]
</script>

<style scoped>
.landing {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
}
</style>
