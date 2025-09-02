import request from '../utils/request';


// 上传Excel文件
export const uploadExcel = (dataForm: FormData) => {
    return request({
        url: '/upload',
        method: 'post',
        data: dataForm,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
}

// 获取上传历史记录，分页
export const getUploadHistory = (page: number, size: number) => {
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