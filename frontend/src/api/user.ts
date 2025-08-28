import request from '../utils/request';
export const login = (dataForm) => {
    return request({
        url: '/auth/login',
        method: 'post',
        data: dataForm
    });
}