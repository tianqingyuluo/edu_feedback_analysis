<script setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {login} from '@/api/user.ts'

const router = useRouter()

import {useUserStore} from "@/store/userStore.js";
import {ElMessage} from "element-plus";

const userStore = useUserStore()

// 定义表单数据
const formData = ref({
  phone: '',
  password: ''
})

// 定义校验状态
const errors = ref({
  phone: '',
  password: ''
})

// 校验规则
const validateForm = () => {
  let isValid = true
  // 重置错误信息
  errors.value.phone = ''
  errors.value.password = ''
  
  // 校验手机号
  if (!formData.value.phone.trim()) {
    errors.value.phone = '请输入手机号'
    isValid = false
  } else if (!/^1[3-9]\d{9}$/.test(formData.value.phone.trim())) {
    errors.value.phone = '请输入正确的手机号'
    isValid = false
  }
  
  // 校验密码
  if (!formData.value.password) {
    errors.value.password = '请输入密码'
    isValid = false
  } else if (formData.value.password.length < 6) {
    errors.value.password = '密码至少6个字符'
    isValid = false
  }
  
  return isValid
}

// 登录处理函数
const handleLogin = async () => {
  if (validateForm()) {
    const res = await login(formData.value)
    userStore.setUserInfo(res.message)
    userStore.setToken(res.token)
    await router.push('/home')
    ElMessage.success('登录成功')
  } else {
    ElMessage.error('请修正表单错误后再提交')
  }
}
</script>

<template>
<div class="login-container">
  <div class="login-box">
    <h2 class="login-title">用户登录</h2>
    
    <!-- 手机号 -->
    <div class="form-item">
      <input
          type="text"
          placeholder="请输入手机号"
          class="login-input"
          v-model="formData.phone"
      />
      <div v-if="errors.phone" class="error-message">{{ errors.phone }}</div>
    </div>
    
    <!-- 密码 -->
    <div class="form-item">
      <input
          type="password"
          placeholder="请输入密码"
          class="login-input"
          v-model="formData.password"
      />
      <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
    </div>
    
    <!-- 登录按钮 -->
    <div class="form-item">
      <button class="login-button" @click="handleLogin">登录</button>
    </div>
  </div>
</div>
</template>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.login-box {
  width: 360px;
  padding: 40px 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.login-title {
  margin-bottom: 24px;
  text-align: center;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.form-item {
  margin-bottom: 20px;
}

.login-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.login-input:focus {
  border-color: #409eff;
}

.login-input.error {
  border-color: #f56c6c;
}

.login-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  color: #fff;
  background: #409eff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.login-button:hover {
  background: #66b1ff;
}

.login-button:active {
  background: #3a8ee6;
}

.error-message {
  font-size: 12px;
  color: #f56c6c;
  margin-top: 6px;
  padding-left: 12px;
  height: 18px;
  line-height: 18px;
}
</style>
