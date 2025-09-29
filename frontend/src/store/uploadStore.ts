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
                analyzedList.value.push({
                    dataid: dataId,
                    taskid: task.taskid,
                    status: TaskStatus.PENDING,
                    progress:0
                });
                console.log(task)
                const itemIdx = items.value.findIndex(it => it.id === dataId)
                if (itemIdx === -1) return

                /* 初始状态 */
                items.value[itemIdx].status = '等待中'
                items.value[itemIdx].progress = 0

                // 假进度条相关变量
                const startTime = Date.now()
                const totalDuration = 4 * 60 * 1000 // 5分钟
                let fakeProgress = 0

                const poll = setInterval(async () => {
                    try {
                        const st = await AnalysisService.getStatus(task.taskid)

                        // 计算假进度（5分钟内从0到99%）
                        const elapsed = Date.now() - startTime
                        fakeProgress = Math.min(99, Math.floor((elapsed / totalDuration) * 100))

                        if (st.status === 'PROCESSING'){
                            items.value[itemIdx].status='分析中'
                            items.value[itemIdx].progress = fakeProgress; // 使用假进度
                        }

                        // 找到 analyzedList 中对应的项进行更新
                        const currentAnalyzedItem = analyzedList.value.find(a => a.dataid === dataId);
                        if (currentAnalyzedItem) {
                            currentAnalyzedItem.status = st.status;
                            currentAnalyzedItem.progress = fakeProgress; // 使用假进度
                        }

                        if (st.status === 'COMPLETED') {
                            clearInterval(poll)
                            if (items.value[itemIdx]) {
                                items.value[itemIdx].status = '已分析'
                                items.value[itemIdx].progress = 100 // 完成时设为100
                            }
                            if (currentAnalyzedItem) {
                                currentAnalyzedItem.status = TaskStatus.COMPLETED;
                                currentAnalyzedItem.progress = 100; // 完成时设为100
                            }
                            return
                        }

                        if (st.status === 'FAILED') {
                            clearInterval(poll)
                            if (items.value[itemIdx]) {
                                items.value[itemIdx].status = '分析失败'
                                items.value[itemIdx].progress = 0
                            }
                            if (currentAnalyzedItem) {
                                currentAnalyzedItem.status = TaskStatus.FAILED;
                                currentAnalyzedItem.progress = 0;
                            }
                            return
                        }
                    } catch (pollError) {
                        // 轮询过程中发生错误
                        clearInterval(poll)
                        if (items.value[itemIdx]) {
                            items.value[itemIdx].status = '分析失败'
                            items.value[itemIdx].progress = 0
                        }
                        const currentAnalyzedItem = analyzedList.value.find(a => a.dataid === dataId);
                        if (currentAnalyzedItem) {
                            currentAnalyzedItem.status = TaskStatus.FAILED;
                            currentAnalyzedItem.progress = 0;
                        }
                        console.error(`轮询任务 ${task.taskid} 失败`, pollError)
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
    return { items, total, page, size, loading, error, fetchPage, changePage,analyzedList,startAnalyze,getTaskIdByDataId,clear }},
    {
        persist: true
    })