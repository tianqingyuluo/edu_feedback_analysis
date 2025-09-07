<template>
  <div id="app" class="w-full px-4 py-8">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      <span class="ml-3 text-gray-600">加载中...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      <p>加载失败: {{ error }}</p>
      <button
          @click="loadUsers"
          class="mt-2 bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm"
      >
        重试
      </button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!users ||users.length===0" class="bg-white rounded-lg shadow p-8 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900">暂无人员数据</h3>
      <p class="mt-1 text-gray-500">还没有添加任何人员，请点击下方按钮添加。</p>
      <div class="mt-6">
        <AddPersonDialog />
      </div>
    </div>

    <!-- 正常状态 -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="flex justify-between items-center p-4">
        <h2 class="text-xl font-semibold text-gray-800">人员管理</h2>
        <AddPersonDialog />
      </div>

      <!-- 表头 -->
      <div class="flex items-center gap-4 px-6 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200">
        <div class="w-1/5 text-left py-1">姓名</div>
        <div class="w-1/5 text-left py-1">权限</div>
        <div class="flex-grow py-1"></div>
        <div class="w-1/5 text-left py-1 max-w-[150px]">操作</div>
      </div>

      <!-- 表体 -->
      <div class="divide-y divide-gray-200">
        <div v-for="user in users" :key="user.id" class="flex items-center gap-4 px-6 py-4 text-sm text-gray-500 hover:bg-gray-50">
          <div class="w-1/5 font-medium text-xl text-gray-900">{{ user.username }}</div>
          <div class="w-1/5">
            <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
              {{ user.role === 'OPERATOR' ? '操作员' : '普通用户' }}
            </span>
          </div>
          <div class="flex-grow"></div>
          <div class="w-1/5 text-left max-w-[150px]">
            <div class="flex flex-wrap gap-4 justify-between">
              <ManagePermissions
                  :user-id="user.id"
                  :username="user.username"
                  :phone="user.phone"
                  :permission="user.role"
              />
              <UserDeleteDialog :user-id="user.id" :username="user.username" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUsersStore } from '@/store/usersStore.ts';
import AddPersonDialog from '@/components/layout/AddPersonDialog.vue';
import ManagePermissions from '@/components/layout/ManagePermissionsDialog.vue';
import UserDeleteDialog from "@/components/layout/UserDeleteDialog.vue";

const usersStore = useUsersStore();
const users = ref([]);
const loading = ref(false);
const error = ref(null);

// 加载用户数据
const loadUsers = async () => {
  loading.value = true;
  error.value = null;
  try {
    users.value = await usersStore.getAllUsers();
  } catch (err) {
    error.value = err.message || '获取用户数据失败';
    console.error('获取用户数据失败:', err);
  } finally {
    loading.value = false;
  }
};

// 组件创建时加载用户数据
onMounted(() => {
  loadUsers();
});

// 监听 store 变化，实时更新用户列表
usersStore.$subscribe((mutation, state) => {
  users.value = [...state.users];
});
</script>

<style scoped>
</style>