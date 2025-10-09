<template>
  <!-- 数据块区域（仅当有 comment 或 chart 时显示） -->
  <template v-if="hasDataBlocks">
    <div v-if="commentText" class="data-block comment-block">{{ commentText }}</div>
    <div v-if="chartText" class="data-block chart-block">{{ chartText }}</div>
  </template>

  <!-- 用户真正说的话（纯文本） -->
  <div class="user-bubble">
    {{ pureText || '[空]' }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ content: string }>()

interface ParsedSegment { type: 'text' | 'comment' | 'chart'; innerContent: string }

/* --------- 下面复用你已有的 parseContent，略 --------- */
const COMMENT_START = 'comment:<<<<<'
const CHART_START = 'chart:<<<<<'
const END_MARKER = '>>>>>>'
const ELLIPSIS = '…'
const MAX_LEN = 50

function parseContent(full: string): ParsedSegment[] {
  const segs: ParsedSegment[] = []
  let i = 0
  while (i < full.length) {
    const rest = full.slice(i)
    const cIdx = rest.indexOf(COMMENT_START)
    const hIdx = rest.indexOf(CHART_START)
    let pick: 'comment' | 'chart' | 'none' = 'none'
    let pickIdx = -1
    if (cIdx !== -1 && (hIdx === -1 || cIdx < hIdx)) {
      pick = 'comment'; pickIdx = cIdx
    } else if (hIdx !== -1) {
      pick = 'chart'; pickIdx = hIdx
    }
    if (pickIdx > 0) { // 前面有纯文本
      segs.push({ type: 'text', innerContent: rest.slice(0, pickIdx) })
    }
    if (pick !== 'none') {
      const startMark = pick === 'comment' ? COMMENT_START : CHART_START
      const contentStart = i + pickIdx + startMark.length
      const endPos = full.indexOf(END_MARKER, contentStart)
      if (endPos === -1) { // 没闭合，当纯文本
        segs.push({ type: 'text', innerContent: rest.slice(pickIdx) }); break
      }
      segs.push({ type: pick, innerContent: full.slice(contentStart, endPos) })
      i = endPos + END_MARKER.length
    } else { // 再无标记
      segs.push({ type: 'text', innerContent: rest }); break
    }
  }
  return segs
}

const segments = computed(() => parseContent(props.content))

/* --------- 三个计算属性 --------- */
const hasDataBlocks = computed(() =>
    segments.value.some(s => s.type === 'comment' || s.type === 'chart')
)

const commentText = computed(() => {
  const c = segments.value.find(s => s.type === 'comment')?.innerContent
  return c && c.length > MAX_LEN ? c.slice(0, MAX_LEN) + ELLIPSIS : c || ''
})

const chartText = computed(() => {
  const c = segments.value.find(s => s.type === 'chart')?.innerContent
  return c && c.length > MAX_LEN ? c.slice(0, MAX_LEN) + ELLIPSIS : c || ''
})

const pureText = computed(() =>
    segments.value.filter(s => s.type === 'text').map(s => s.innerContent).join('')
)
</script>

<style scoped>
/* 灰色单行数据块 */
.data-block {
  align-self: flex-end;   /* 和用户气泡同侧 */
  max-width: 60%;
  min-height: 20px;
  padding: 4px 10px;
  margin-bottom: 4px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: #f3f4f6;
  color: #9ca3af;
}
.comment-block { border-left: 3px solid #60a5fa; }
.chart-block   { border-left: 3px solid #34d399; }

/* 用户正常气泡 */
.user-bubble {
  align-self: flex-end;
  max-width: 60%;
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.45;
  font-size: 15px;
  word-break: break-word;
  background: #0969da;
  color: #fff;
}
</style>