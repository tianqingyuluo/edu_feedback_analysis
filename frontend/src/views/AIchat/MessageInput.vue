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
import {ref, inject, type Ref, reactive, onMounted, watch} from 'vue'
import { Textarea } from '@/components/ui/textarea'
import ChatService from '@/api/chat'
import type { ChatMessage } from '@/types/Chat.ts'
import {useDocStore} from "@/store/useDocStore.ts";
import {useChatQueueStore} from "@/store/ChatQueueStore.ts";

const text = ref('')
const messages = inject<Ref<ChatMessage[]>>('messages')!
const currentId = inject<string>('currentId')!

const handleSend = async (externalContent?: string) => {
  console.log(externalContent)
  const q = externalContent ?? text.value.trim()
  if (!q) return
  if (!externalContent) text.value = ''
  const DocStore = useDocStore()
  console.log(DocStore.currentKb)
  /* 用户消息 */
  const userMsg: ChatMessage = {
    id: Date.now().toString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    chatid: currentId,
    role: 'user',
    content: q
  }
  messages.value.push(userMsg)

  /* 空助手消息 */
  const aiMsg = reactive<ChatMessage>({
    id: (Date.now() + 1).toString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    chatid: currentId,
    role: 'assistant',
    content: ''
  })
  messages.value.push(aiMsg)

  /* 流式追加 */
  console.log('DocStore', DocStore.currentKb)
  console.log('currentId',currentId.value)
  await ChatService.send(currentId.value,DocStore.currentKb.id ,q, (token, done) => {
    if (done) return
    aiMsg.content += token
  })
}
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
const chatQueue = useChatQueueStore()
const chatReady = inject<Ref<boolean>>('chatReady')!

watch(chatReady, async ready => {
  // 只要变成 false（代表初始化完成）就发
  if (ready) return               // 还在 loading，跳过
  if (!chatQueue.pendingContent) return

  await handleSend(chatQueue.pendingContent)
  chatQueue.clearPending()
})
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