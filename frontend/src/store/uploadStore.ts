import {defineStore} from 'pinia'
import {getUploadHistory} from '@/api/excel.ts'
import {ref} from 'vue'
import {type AnalysisInit, type HistoryItem, TaskStatus, type UploadHistoryResp} from "@/types/analysis.ts";
import AnalysisService from "@/api/analysis.ts";

interface UploadItem extends HistoryItem {
    status?: '已分析' | '分析中' | '未分析' | '分析失败' | '等待中'
    progress?: number          // 0-100
}
export const statusToCN = (s: TaskStatus | undefined): string => {
    switch (s) {
        case TaskStatus.PENDING:    return '等待中'
        case TaskStatus.PROCESSING: return '分析中'
        case TaskStatus.COMPLETED:  return '已分析'
        case TaskStatus.FAILED:     return '分析失败'
        default:                    return '未分析'   // 找不到、未开始都归这里
    }
}
export const useUploadStore = defineStore('upload', () => {
    const items   = ref<UploadItem[]>([])
    const total   = ref(0)
    const page    = ref(1)
    const size    = ref(10)
    const loading = ref(false)
    const error   = ref<string | null>(null)
    const analyzedList = ref<AnalysisInit[]>([])
    /* 拉一页数据 */
    async function fetchPage(p = page.value, s = size.value) {
        loading.value = true
        error.value   = null
        try {
            /* 1. 一次性拉已分析集合（存起来） */
            analyzedList.value = await AnalysisService.getAnalysis()
            /* 2. 上传列表 */
            const { message } = (await getUploadHistory(p, s)) as UploadHistoryResp
            const rawList = message.items
            /* 3. 本地拼状态 */
            items.value = rawList.map(it => ({
                 ...it,
                 status: statusToCN(
                    analyzedList.value.find(a => a.dataid === String(it.id))?.status
                 )
            })) as UploadItem[]

            total.value = message.total
            page.value  = message.page
            size.value  = message.size
        }catch {

            /* ===== 兜底：带状态的假数据 ===== */
            const mockTotal = 33
            const start = (p - 1) * s
            const remaining = Math.max(0, Math.min(s, mockTotal - start))
            const rawMock: HistoryItem[] = Array.from({ length: remaining }, (_, i) => ({
                id: String( start + i + 1),
                filename: `test_file_${start + i + 1}.csv`,
                size: Math.floor(Math.random() * 1024 * 1024),
                uploaded_at: new Date(Date.now() - (start + i + 1) * 3600_000).toISOString()
            }))

            /* 3. 本地拼随机状态 */
            items.value = rawMock.map(it => ({
                ...it,
                status: (['已分析', '分析中', '未分析','分析失败','等待中'] as const)[
                    Math.floor(Math.random() * 5)
                    ]
            })) as UploadItem[]
            analyzedList.value = rawMock.map((it, idx) => ({
                taskid: `fake-task-${it.id}`,
                dataid: String(it.id),
                status: TaskStatus.COMPLETED,
                progress: 100,
            }))
            total.value = mockTotal
            page.value  = p
            size.value  = s
        } finally {
            loading.value = false
        }
    }

    /* 改变分页 */
    function changePage(p: number) {
        fetchPage(p, size.value)
    }

    function clear() {
        items.value   = []
        total.value   = 0
        page.value    = 1
        size.value    = 10
        loading.value = false
        error.value   = null
    }
        async function startAnalyze(dataId: string) {
        try{
            /* 1. 发起任务 */
            const task = await AnalysisService.startAnalysis({ dataid: dataId })
            /* 2. 把状态先置为“分析中” */
            const idx = items.value.findIndex(it => it.id === dataId)
            if (idx === -1) return

            /* 初始状态 */
            items.value[idx].status = '等待中'
            items.value[idx].progress = 0

            const poll = setInterval(async () => {
                try {
                    const st = await AnalysisService.getStatus(task.taskid)
                    /* 实时进度 */
                    items.value[idx].progress = st.progress ?? 0

                    if (st.status === 'COMPLETED') {
                        clearInterval(poll)
                        items.value[idx].status = '已分析'
                        items.value[idx].progress = 100
                        return
                    }
                    if (st.status === 'FAILED') {
                        clearInterval(poll)
                        items.value[idx].status = '分析失败'
                        items.value[idx].progress = 0
                        return
                    }
                } catch {
                    clearInterval(poll)
                    items.value[idx].status = '分析失败'
                    items.value[idx].progress = 0
                }
            }, 1000)

            return task.taskid
        }catch (e: unknown) {
            /* 404/500/网络错误 统一走这里 */
            const idx = items.value.findIndex(it => it.id === dataId)
            if (idx !== -1) items.value[idx].status = '分析失败'
            console.error('启动分析失败', e)
        }
        }
        const getTaskIdByDataId = (dataId: string): string | undefined =>
            analyzedList.value.find(a => a.dataid === dataId)?.taskid
    return { items, total, page, size, loading, error, fetchPage, changePage,analyzedList,startAnalyze,getTaskIdByDataId }},
    {
        persist: true
    })