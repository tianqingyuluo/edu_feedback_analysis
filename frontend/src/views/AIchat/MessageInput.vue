<template>
  <div class="send-wrap">
    <Textarea
        v-model="text"
        placeholder="输入消息（Enter 发送，Shift+Enter 换行）"
        @keydown="onKeydown"
        rows="2"
    />
    <button class="send-btn" @click="handleSend">发送</button>
  </div>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import { Textarea } from '@/components/ui/textarea'

const text = ref('')
const sendMessage = inject<(content: string) => void>('sendMessage')!

const handleSend = () => {
  const v = text.value.trim()
  if (!v) return
  sendMessage(v)
  text.value = ''
}

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<style scoped>
.send-wrap {
  display: flex;
  align-items: flex-end;
  padding: 12px 16px;
  gap: 8px;
  background: #fff;
  border-top: 1px solid #e5e5e5;
}
.send-btn {
  height: 36px;
  padding: 0 16px;
  background: #0969da;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}
.send-btn:hover {
  background: #0550ae;
}
</style>