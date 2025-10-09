import type { AxiosProgressEvent } from 'axios'
import request from '@/utils/request'   // 你的 axios 实例
type OnMessage = (chunk: string, done: boolean) => void

export class Streamer {
    static async post(
        path: string,                       // 传相对路径即可  /chat/stream
        body: Record<string, any>,
        onMessage: OnMessage
    ): Promise<void> {
        let buf = ''

        /* 监听下载进度，这里会多次回调 */
        const onDownloadProgress = (e: AxiosProgressEvent) => {
            if (!e.event.target) return
            const xhr = e.event.target as XMLHttpRequest
            /* responseText 拿到当前已收到的文本 */
            const text: string = xhr.responseText || ''
            const newChunk = text.substring(buf.length) // 只处理新增部分
            buf = text

            /* 跟之前一样按 \n\n 切行 */
            const lines = newChunk.split('\n\n')
            for (const line of lines) {
                const trim = line.trim()
                if (trim.startsWith('data:')) {
                    const payload = trim.slice(5).trim()
                    if (payload === '[DONE]') { onMessage('', true); return }
                    onMessage(payload, false)
                }
            }
        }

        await request({
            url: path,
            method: 'POST',
            data: body,
            responseType: 'text',
            onDownloadProgress
        })
    }
}