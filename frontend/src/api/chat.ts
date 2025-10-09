import request from "@/utils/request.ts";
import type * as T from "@/types/Chat.ts";
import type {getChatRoomHistory} from "@/types/Chat.ts";
import {Streamer} from "@/utils/Streamer.ts";

class ChatService {
    static async getChatRoom(task_id: string) {
        const res = await request({ url: `/chat/${task_id}`, method: 'get' }) as T.getChatRoomResp;
        return res;
    }
    static async getChatHistory(chat_id: string) {
        const res = await request({ url: `/chat/history/${chat_id}`, method: 'get' }) as T.getChatRoomHistory;
        return res;
    }
    static async send(chat_id: string,kb_id: string, question: string, onToken: (token: string, done: boolean) => void): Promise<void> {
        const params = new URLSearchParams()
        if (kb_id !== undefined) params.append('kb_id', String(kb_id))

        // 2. 拼完整 URL：path + query
        const url = `chat/send/${chat_id}${params.toString() ? '?' + params.toString() : ''}`

        // 3. 走流式
        await Streamer.post(url, { question },(chunk, done) => onToken(chunk, done))
    }
}
export default ChatService;