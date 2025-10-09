<template>
  <main class="content" ref="box">
    <component
        v-for="msg in messages"
        :key="msg.id"
        :is="msg.role === 'assistant' ? MarkdownBubble : UserTextBubble"
        :class="['bubble', msg.role]"
        :content="msg.content"
    >
    </component>
  </main>
</template>

<script setup lang="ts">
import { inject, ref, onMounted, onBeforeUnmount } from 'vue'
import type { ChatMessage } from '@/types/Chat.ts'
import MarkdownBubble from "@/components/layout/MarkdownBubble.vue";
import UserTextBubble from "@/views/UserTextBubble.vue";

const messages = inject<ChatMessage[]>('messages')!
const box = ref<HTMLElement>()

let ro: ResizeObserver | null = null

onMounted(() => {
  ro = new ResizeObserver(() => {
    // 高度变化 → 说明新消息渲染完成
    if (box.value) box.value.scrollTop = box.value.scrollHeight
  })
  if (box.value) ro.observe(box.value)
})

onBeforeUnmount(() => ro?.disconnect())
</script>

<style scoped>
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #fafafa;
}
.bubble {
  max-width: 60%;
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.45;
  font-size: 15px;
  word-break: break-word;
}
.bubble.user {
  align-self: flex-end;
  background: #0969da;
  color: #fff;
}
.bubble.assistant {
  align-self: flex-start;
  background: #fff;
  border: 1px solid #e5e5e5;
}
</style>