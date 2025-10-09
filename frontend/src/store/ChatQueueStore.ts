// stores/chatQueue.ts
import {defineStore} from "pinia";
import {ref} from "vue";

export const useChatQueueStore = defineStore('chatQueue', () => {
    const pendingContent = ref<string | null>(null)
    const fromChart      = ref<string | null>(null) // 记号，可选

    function setPending(content: string, chart?: string) {
        pendingContent.value = content
        fromChart.value      = chart ?? null
    }
    function clearPending() {
        pendingContent.value = null
        fromChart.value      = null
    }
    return { pendingContent, fromChart, setPending, clearPending }
})