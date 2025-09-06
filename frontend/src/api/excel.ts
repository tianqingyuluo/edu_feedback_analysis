import request from '../utils/request';
import type {UploadHistoryResp} from "@/types/analysis.ts";


// 上传Excel文件
export const uploadExcel = (dataForm: FormData) => {
    return request({
        url: '/upload/',
        method: 'post',
        data: dataForm,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
}

// 获取上传历史记录，分页
export const getUploadHistory = (page: number, size: number):Promise<UploadHistoryResp> => {
    return request({
        url: `/upload/history/${page}/${size}`,
        method: 'get'
    });
}

///upload/{id}
export const deleteExcelById = (id: number) => {
    return request({
        url: `/upload/${id}`,
        method: 'delete'
    });
}