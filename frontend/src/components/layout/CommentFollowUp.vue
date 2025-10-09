<script setup lang="ts">
/* 一个完整的“评论 + 追问输入框”区块
 * 使用示例：
 * <CommentFollowUp
 *     :comment="comments.academic_maturity_by_grade_aggregator"
 *     :chart="metricGroups"/>
 */
import { ref, toRaw, inject } from 'vue'
import { Button } from '@/components/ui/button'
import MarkdownBubble from '@/components/layout/MarkdownBubble.vue'
import { useChatQueueStore } from '@/store/ChatQueueStore'

/* ---------- props ---------- */
interface Props {
  comment: string                       // 评论文本
  chart?: any[] | any
  placeholder?: string                  // 输入框占位
  sourceTag?: string                    // 来源标记
}
const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入追问内容...',
  sourceTag: '学业成熟度跨年级对比'
})

/* ---------- 依赖 ---------- */
const chatQueue = useChatQueueStore()
const openChatDialog = inject<() => void>('openChatDialog')!

/* ---------- 内部状态 ---------- */
const followUpText = ref('')

function buildChartPart(): string {
  return anyToFlatString(props.chart)
}
function anyToFlatString(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return value
  if (typeof value !== 'object') return String(value)

  // 数组
  if (Array.isArray(value)) {
    return value.map(anyToFlatString).join(',')
  }

  // 普通对象（包括类实例，只要它是对象）
  const obj = value as Record<string, unknown>
  return Object.keys(obj)
      .sort() // 保证字段顺序稳定
      .map(k => anyToFlatString(obj[k]))
      .join(',')
}
function handleSend() {
  const q = followUpText.value.trim()
  if (!q) return
  const chartPart = `chart:<<<<<${buildChartPart()}>>>>>>`
  const content = `comment:<<<<<${props.comment}>>>>>>\n${chartPart}\n\n${q}`
  chatQueue.setPending(content, props.sourceTag)
  openChatDialog()
  followUpText.value = ''
}
</script>

<template>
  <div class="bg-white rounded-lg shadow p-4">
    <MarkdownBubble :content="comment" />
    <div class="flex items-center gap-2 mt-3">
      <input
          v-model="followUpText"
          :placeholder="placeholder"
          class="flex-1 border border-gray-300 rounded px-3 py-2"
          @keyup.enter="handleSend"
      />
      <Button @click="handleSend">追问</Button>
    </div>
  </div>
</template>