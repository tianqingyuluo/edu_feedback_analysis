// request.js
import axios from 'axios';
import { ElMessage } from 'element-plus';
const baseURL = '/api';
const instance = axios.create({baseURL});
import router from "../router/index.js";
import {useUserStore} from "@/store/userStore.ts";

// 添加响应拦截器
instance.interceptors.response.use(
    result => {
        return Promise.resolve(result.data);
    },
    error => {
        // 处理错误情况
        let message = '未知错误';
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    message = error.response.data?.info ||'登录已过期，请重新登录';
                    router.push('/login');
                    break;
                case 403:
                    message = error.response.data?.info ||'拒绝访问';
                    break;
                case 404:
                    message = error.response.data?.info ||'请求地址错误';
                    break;
                case 500:
                    message = error.response.data?.info || '服务器故障' ;
                    break;
                default:
                    message = error.response.data?.info ||'网络错误';
            }
        } else {
            message = error.response.data?.info ||'网络连接异常';
        }
        ElMessage.error(message);
        return Promise.reject(error);
    }
);


instance.interceptors.request.use(
    config => {
        const userStore = useUserStore();
        if(userStore.token){
            config.headers.Authorization = `Bearer ${userStore.token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

export default instance;