import {defineStore} from "pinia";
import {ref} from "vue";

export const useUserStore = defineStore('userInfo', () => {
        const userInfo = ref();
        const token = ref();
        const setUserInfo = (newUserInfo) => {

            userInfo.value = newUserInfo;
        }
        const setToken = (newToken) => {

            token.value = newToken;
        }
        const removeUserInfo = () => {
            userInfo.value = null;
        }
        const removeToken = () => {
            token.value = null;
        }
        return {
            userInfo,
            setUserInfo,
            removeUserInfo,
            token,
            setToken,
            removeToken
        };
    },
    {
        persist: true
    }
);