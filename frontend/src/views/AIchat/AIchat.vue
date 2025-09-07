<template>
  <div class="chat-page h-full">
    <!-- 1. 监听新建事件 -->

    <section class="main">
      <ChatContent class="content" />
      <MessageInput class="input-bar" />
    </section>
  </div>
</template>

<script setup lang="ts">
import ChatHistory from './ChatHistory.vue'
import ChatContent from './ChatContent.vue'
import MessageInput from './MessageInput.vue'
import { provide, ref } from 'vue'
import type { Message} from './types'

const historyList = ref<HistoryItem[]>([{ id: '1', title: '新建对话 1' }])
const messages = ref<Message[]>([])
const currentId = ref('1')

provide('historyList', historyList)
provide('currentId', currentId)
provide('messages', messages)

provide('sendMessage', (content: string) => {
  messages.value.push({ id: Date.now().toString(), role: 'user', content })
  setTimeout(() => {
    messages.value.push({ id: Date.now() + 1 + '', role: 'assistant', content: 'AI：' + content })
  }, 600)
})

provide('selectSession', (id: string) => {
  currentId.value = id
  messages.value = []
})

/* 2. 新建会话逻辑 */
const onNewSession = () => {
  const id = Date.now().toString()
  historyList.value.unshift({ id, title: `新建对话 ${historyList.value.length + 1}` })
  currentId.value = id
  messages.value = []
}
</script>

<style scoped>
.chat-page {
  display: flex;
  background: #fff;
}
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.content {
  flex: 1;
  overflow-y: auto;
}
.input-bar {
  height: 90px;
}
</style>