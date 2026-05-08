<template>
  <div class="h-full overflow-y-auto p-6 lg:p-8 bg-gray-50 dark:bg-gray-950">
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-2">
        <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
          <n-icon size="28" class="text-emerald-500"><HelpCircleOutline /></n-icon>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Help Center</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">Everything you need to get started with DocMind</p>
        </div>
      </div>

      <!-- Quick Start -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700 bg-gradient-to-r from-emerald-50 to-transparent dark:from-emerald-900/10">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <n-icon class="text-emerald-500"><RocketOutline /></n-icon>
            Quick Start Guide
          </h2>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="(step, i) in quickStart" :key="i" class="flex gap-4 p-4 rounded-xl bg-gray-50 dark:bg-gray-700/30 hover:bg-emerald-50 dark:hover:bg-emerald-900/10 transition-colors">
              <div class="flex-shrink-0 w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                <span class="text-lg font-bold text-emerald-600 dark:text-emerald-400">{{ i + 1 }}</span>
              </div>
              <div>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-1">{{ step.title }}</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Features -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <n-icon class="text-blue-500"><GridOutline /></n-icon>
            Core Features
          </h2>
        </div>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="feature in features" :key="feature.title" class="flex gap-3 p-3 rounded-xl border border-gray-100 dark:border-gray-700">
            <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" :class="feature.bg">
              <span class="text-base">{{ feature.icon }}</span>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white">{{ feature.title }}</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ feature.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- FAQ -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <n-icon class="text-purple-500"><ChatbubblesOutline /></n-icon>
            FAQ
          </h2>
        </div>
        <div class="p-6">
          <n-collapse>
            <n-collapse-item v-for="faq in faqs" :key="faq.name" :title="faq.q" :name="faq.name">
              <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{{ faq.a }}</p>
            </n-collapse-item>
          </n-collapse>
        </div>
      </div>

      <!-- Keyboard Shortcuts -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <n-icon class="text-orange-500"><KeyOutline /></n-icon>
            Keyboard Shortcuts
          </h2>
        </div>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div v-for="shortcut in shortcuts" :key="shortcut.key" class="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/30">
            <span class="text-sm text-gray-700 dark:text-gray-300">{{ shortcut.desc }}</span>
            <kbd class="px-2 py-1 text-xs font-mono bg-gray-200 dark:bg-gray-600 rounded text-gray-700 dark:text-gray-200">{{ shortcut.key }}</kbd>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NCollapse, NCollapseItem, NIcon } from 'naive-ui'
import {
  HelpCircleOutline, RocketOutline, GridOutline, ChatbubblesOutline, KeyOutline
} from '@vicons/ionicons5'

const quickStart = [
  { title: 'Upload Documents', desc: 'Go to Knowledge Base and upload PDF, Word, Excel, or text files. They are automatically parsed and indexed.' },
  { title: 'Ask Questions', desc: 'Open Chat and ask questions in natural language. The system searches your knowledge base and generates cited answers.' },
  { title: 'Use Agent Mode', desc: 'For complex questions, use Agent Mode. It reasons step-by-step, calls multiple tools, and composes comprehensive answers.' },
  { title: 'Review & Improve', desc: 'Check source citations, give feedback on answers, and upload more documents to improve knowledge coverage.' },
]

const features = [
  { icon: ' ', bg: 'bg-emerald-50 dark:bg-emerald-900/30', title: 'Hybrid Search', desc: 'Keyword + vector search with RRF fusion for maximum recall accuracy.' },
  { icon: ' ', bg: 'bg-blue-50 dark:bg-blue-900/30', title: 'Agent Reasoning', desc: 'Multi-step tool-calling loop that plans, searches, and verifies answers.' },
  { icon: ' ', bg: 'bg-purple-50 dark:bg-purple-900/30', title: 'Source Citations', desc: 'Every answer includes [n] citations linking back to source documents.' },
  { icon: ' ', bg: 'bg-orange-50 dark:bg-orange-900/30', title: 'Multi-format Support', desc: 'PDF, Word, Excel, PowerPoint, and plain text document parsing.' },
]

const faqs = [
  { name: 'q1', q: 'Why does the answer not match my document?', a: 'Ensure your question is specific and the document contains relevant content. Check the Knowledge Base page to verify document status is "indexed". Try rephrasing your question with keywords from the document.' },
  { name: 'q2', q: 'Why is my document stuck in "processing" status?', a: 'Large documents may take longer to parse. Wait a few minutes and refresh. If the status shows "failed", click "Rebuild Index" in the Knowledge Base to retry.' },
  { name: 'q3', q: 'What is Agent Mode and how is it different from Chat?', a: 'Agent Mode uses an autonomous reasoning loop with tool calling. It can search multiple times, analyze documents, and compose answers step-by-step. Regular Chat does single-pass retrieval and generation.' },
  { name: 'q4', q: 'How does the guest account work?', a: 'The guest account (guest / 123456) provides full access to chat, knowledge base, and agent features. Admin features like user management and audit logs require an admin account.' },
]

const shortcuts = [
  { key: 'Ctrl+K', desc: 'Focus global search' },
  { key: 'Enter', desc: 'Send message in chat' },
  { key: 'Shift+Enter', desc: 'New line in chat input' },
]
</script>
