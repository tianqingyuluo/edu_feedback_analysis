import type { ChatMessage } from '@/types/Chat'
import ChatService from '@/api/chat'
import { reactive } from 'vue'

export async function chatSend(
    currentId: string,
    kbId: string,
    content: string,
    messages: ChatMessage[]
) {
    const userMsg: ChatMessage = {
        id: Date.now().toString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        chatid: currentId,
        role: 'user',
        content
    }
    messages.push(userMsg)

    const aiMsg = reactive<ChatMessage>({
        id: (Date.now() + 1).toString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        chatid: currentId,
        role: 'assistant',
        content: ''
    })
    messages.push(aiMsg)

    await ChatService.send(currentId, kbId, content, (tok, done) => {
        if (done) return
        aiMsg.content += tok
    })
}