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
import ChatContent from './ChatContent.vue'
import MessageInput from './MessageInput.vue'
import {onMounted, provide, readonly, ref} from 'vue'
import type {ChatMessage} from '@/types/Chat.ts'
import {useRoute} from "vue-router";
import ChatService from "@/api/chat.ts";
import {useChatQueueStore} from "@/store/ChatQueueStore.ts";

const messages = ref<ChatMessage[]>([])
const route = useRoute()
const taskId =ref<string>(route.params.reportId as string)
const currentId=ref<string>('')
provide('currentId', currentId)
provide('taskId', taskId)
provide('messages', messages)
const loading = ref(true)
provide('chatReady', readonly(loading))


onMounted(async () => {
  if (!taskId.value) return
  currentId.value =(await ChatService.getChatRoom(taskId.value)).id
  try {
    loading.value = true
    messages.value = await ChatService.getChatHistory(currentId.value)
  } catch (e) {
    console.error('拉历史失败', e)
  } finally {
    loading.value = false
  }
})

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