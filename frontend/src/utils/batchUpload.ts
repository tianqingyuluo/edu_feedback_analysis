import request from "@/utils/request.ts";
import {useDocStore} from "@/store/useDocStore.ts";

/**
 * 1. 批量上传 public/doc 下所有文件
 * 2. 返回已上传的 doc id 列表
 */
export async function uploadPublicDocDir(): Promise<string[]> {
    const DocStore = useDocStore();
    const modules = import.meta.glob<string>('/public/doc/**/*', {
        query: '?url',
        import: 'default'
    })
    const fileUrls = Object.values(modules)

    if (fileUrls.length === 0) {
        console.warn('public/doc 目录为空')
        return []
    }

    const ids: string[] = []

    for (const urlGen of Object.values(modules)) {
        const url = await urlGen()
        const res = await fetch(url)
        const blob = await res.blob()
        const file = new File([blob], url.split('/').pop()!, { type: blob.type })
        const id = await DocStore.addDoc(file)
        ids.push(id)
    }
    return ids
}
/** 创建默认知识库 */
export async function createDefaultKb() {
    return request.post(`/knowledge-base`, {
        name: '默认知识库',
        description: '自动初始化'
    })
}

/** 初始化向量索引 */
export async function initKbVector(kbId: string, docIds: string[]) {
    return request.post(`/knowledge-base/${kbId}/initialize`, {
        document_ids: docIds
    })
}