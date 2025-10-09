import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import {deleteDoc, listDoc, listKb, uploadDoc} from '@/api/document'
import type {DocItem, KnowledgeBase} from '@/types/document'
import {ElMessage} from "element-plus";
import {createDefaultKb, initKbVector, uploadPublicDocDir} from "@/utils/batchUpload.ts";
import request from "@/utils/request.ts";

export const useDocStore = defineStore('doc', () => {
    /* 状态 */
    const docs      = ref<DocItem[]>([])
    const total     = ref(0)
    const page      = ref(1)
    const pageSize  = ref(20)
    const loading   = ref(false)
    const error     = ref('')
    const knowledgeBases = ref<KnowledgeBase[]>([])
    const currentKb = ref<KnowledgeBase | null>(null)

    /* getter */
    const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

    /* 拉列表 */
    async function fetchDocs() {
        if (docs.value.length === 0) await fetchAllDocs()
        const start = (page.value - 1) * pageSize.value
        return docs.value.slice(start, start + pageSize.value)
    }


/* 上传 */
    async function addDoc(file: File) {
        const res = await uploadDoc(file)
        await fetchAllDocs()
        processDoc(res.data.id)
        return res.data.id
    }

    /* 分段拉完所有文档 */
    async function fetchAllDocs(pageSizePerReq = 20) {
        loading.value = true
        error.value   = ''
        docs.value    = []
        total.value   = 0
        page.value    = 1

        try {
            let pageNum = 1
            let hasMore = true

            while (hasMore) {
                // 单次请求
                const res = await listDoc(pageNum, pageSizePerReq)
                const { documents, pagination } = res.data

                docs.value.push(...documents)          // 合并到总数组
                total.value = pagination.total         // 后端总条数

                // 判断有没有下一页
                hasMore = documents.length === pageSizePerReq &&
                    docs.value.length < total.value

                pageNum++
            }
        } catch (e: any) {
            error.value = e.message || '获取列表失败'
        } finally {
            loading.value = false
        }
    }
    /* 删除 */
    async function removeDoc(id: string) {
        await deleteDoc(id)               // 先调后端
        const idx = docs.value.findIndex(d => d.id === id)
        if (idx > -1) docs.value.splice(idx, 1) // 本地剔除
        total.value--
    }

    /* 换页 */
    function changePage(p: number) {
        page.value = p
    }

    async function initKnowledgeBase() {
        const kbs = await listKb()
        console.log('kbs',kbs)
        knowledgeBases.value = kbs

        if (kbs.length === 0) {
            // ① 批量上传 public/doc
            const docIds = await uploadPublicDocDir()
            if (docIds.length === 0) {
                ElMessage.warning('public/doc 目录为空，无法自动创建知识库')
                return { ready: false }
            }

            // ② 创建默认知识库
            const { data: kbData } = await createDefaultKb()
            const kbId = kbData.data.id

            // ③ 初始化向量索引
            await initKbVector(kbId, docIds)

            // ④ 重新拉一次知识库状态
            knowledgeBases.value = await listKb()
            currentKb.value = knowledgeBases.value[0]
            return { ready: true, kb: currentKb.value }
        }

        // 已有知识库
        currentKb.value = kbs[0]
        console.log(currentKb.value)

        await initKbVector(
            currentKb.value.id,
            docs.value.map(d => d.id)
        )
        return { ready: kbs[0].status === 'ready', kb: currentKb.value }
    }
    async function processDoc(id: string) {
        try {
            const res = await request.post(`/documents/${id}/process`)
            const idx = docs.value.findIndex(d => d.id === id)
            console.log(idx)
            if (idx !== -1) {
                docs.value[idx].status        = 'processed'
                docs.value[idx].processed_at  = new Date().toISOString()
                docs.value[idx].chunk_count   = res.data.chunk_count ?? 0
            }

            ElMessage.success('文档处理完成')
            return res.data
        } catch (e: any) {
            // 失败时置 error
            const idx = docs.value.findIndex(d => d.id === id)
            if (idx !== -1) {
                docs.value[idx].status = 'error'
                docs.value[idx].error_message = e.message || '处理失败'
            }
            ElMessage.error('处理失败：' + e.message)
            throw e
        }
    }


return {
docs,
total,
page,
pageSize,
loading,
error,
totalPages,
fetchDocs,
addDoc,
removeDoc,
changePage,
initKnowledgeBase,
currentKb,
}
})