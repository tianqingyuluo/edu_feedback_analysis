<template>
  <main class="content" ref="box">
    <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['bubble', msg.role]"
    >
      {{ msg.content }}
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject, nextTick, ref, watch } from 'vue'
import type { Message } from './types'

const messages = inject<Message[]>('messages')!
const box = ref<HTMLElement>()

watch(
    messages,
    () => nextTick(() => {
      box.value && (box.value.scrollTop = box.value.scrollHeight)
    }),
    { deep: true, flush: 'post' }
)
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