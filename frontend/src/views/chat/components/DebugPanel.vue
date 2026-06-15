<template>
  <div v-if="debugData" class="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
    <div class="px-4 py-2 flex items-center justify-between text-xs text-gray-500 border-b border-gray-200 dark:border-gray-700">
      <span class="font-medium">🔍 检索调试面板</span>
      <div class="flex items-center gap-2">
        <span class="text-gray-400">{{ debugData.elapsed_ms ? `${debugData.elapsed_ms}ms` : '' }}</span>
        <span v-if="debugData.strategy" class="px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
          {{ debugData.strategy }}
        </span>
        <span v-if="debugData.cache_hit" class="px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400">
          缓存命中({{ debugData.cache_type }})
        </span>
        <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="expanded = !expanded">
          {{ expanded ? '收起' : '展开' }}
        </button>
        <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="$emit('close')">✕</button>
      </div>
    </div>

    <div v-if="expanded" class="p-3 space-y-3 text-xs font-mono max-h-96 overflow-y-auto">
      <!-- Cache hit -->
      <div v-if="debugData.cache_hit" class="p-2 rounded bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800/40">
        ⚡ 缓存命中（{{ debugData.cache_type }}），跳过检索
      </div>

      <!-- Note -->
      <div v-if="debugData.note" class="p-2 rounded bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800/40">
        ⚠️ {{ debugData.note }}
      </div>

      <!-- Multi-stage: show per sub-query -->
      <template v-if="debugData.stages">
        <div v-for="(stage, sq) in debugData.stages" :key="sq" class="space-y-2">
          <div class="font-semibold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
            子查询: {{ sq }}
          </div>
          <DebugStage :debug-data="stage" />
        </div>
      </template>

      <!-- Single stage -->
      <DebugStage v-else :debug-data="debugData" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { RetrievalDebugData } from '@/types/chat'
import DebugStage from './DebugStage.vue'

defineProps<{
  debugData: RetrievalDebugData | null
}>()

defineEmits<{
  close: []
}>()

const expanded = ref(true)
</script>
