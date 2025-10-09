import request from '@/utils/request'
import type {KnowledgeBase} from "@/types/document.ts";

const BASE = '/documents'

/** 上传 */
export async function uploadDoc(file: File) {
    const fd = new FormData()
    fd.append('file', file)
    return request({
        url: `${BASE}/upload`,
        method: 'POST',
        data: fd,
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}

/** 分页列表 */
export async function listDoc(page = 1, pageSize = 20) {
    return request({
        url: BASE,
        method: 'GET',
        params: {page, page_size: pageSize}
    })
//     return {
//         "code": 0,
//         "message": "获取文档列表成功",
//         "data": {
//             "documents": [
//                 {
//                     "id": "1",
//                     "filename": "2025-教学反馈-期中问卷.pdf",
//                     "file_type": "pdf",
//                     "file_size": 1024_128,        // 1 MB 出头
//                     "status": "processed",
//                     "chunk_count": 42,
//                     "uploaded_at": "2025-06-10T14:23:44+08:00",
//                     "processed_at": "2025-06-10T14:25:01+08:00",
//                     "error_message": ""
//                 },
//                 {
//                     "id": "2",
//                     "filename": "课程改进建议-学生访谈.docx",
//                     "file_type": "docx",
//                     "file_size": 512_512,
//                     "status": "uploaded",
//                     "chunk_count": 0,
//                     "uploaded_at": "2025-06-11T09:12:33+08:00",
//                     "processed_at": null,
//                     "error_message": ""
//                 },
//                 {
//                     "id": "3",
//                     "filename": "成绩单-模板.csv",
//                     "file_type": "csv",
//                     "file_size": 64_789,
//                     "status": "error",
//                     "chunk_count": 0,
//                     "uploaded_at": "2025-06-11T11:05:12+08:00",
//                     "processed_at": null,
//                     "error_message": "CSV 列数不一致，解析失败"
//                 }
//             ],
//             "pagination": {
//                 "total": 33,
//                 "page": 1,
//                 "page_size": 20,
//                 "total_pages": 2
//             }
//         }
//     }
// }
}
/** 删除 */
export async function deleteDoc(id: string) {
    return request({
        url: `${BASE}/${id}`,
        method: 'DELETE'
    })
}
/** 获取所有知识库列表 */
export async function listKb() {
    const res = await request({
        url: '/knowledge-base',
        method: 'GET'
    })
    return res.data.knowledge_bases as KnowledgeBase[]

}

