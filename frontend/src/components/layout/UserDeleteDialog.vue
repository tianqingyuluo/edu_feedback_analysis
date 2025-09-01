<!-- src/components/UserDeleteDialog.vue -->
<script setup lang="ts">
import { ref } from 'vue'; // ref 用于控制 Dialog 的打开/关闭状态

// --- 导入 Element Plus 的 ElMessage ---
import { ElMessage } from 'element-plus';
// -------------------------------------

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
// -------------------------------------

// --- 导入 Pinia store ---
import { useUsersStore } from '@/store/usersStore.ts';
const userStore = useUsersStore();
// -----------------------

// 定义 Props 接口
interface Props {
  userId: number;   // 要删除的用户ID (必须)
  username: string; // 要删除的用户名 (必须)
}
const props = defineProps<Props>();

// 用于控制对话框的打开/关闭状态
const isDialogOpen = ref(false);

const handleDelete = async () => {
  try {
    // 调用 Pinia store 中的删除用户方法
    await userStore.deleteUser(props.userId);

    // 删除成功后显示 ElMessage
    ElMessage.success({
      message: `用户 ${props.username} 已成功删除！`,
      duration: 3000,
    });

    // 关闭对话框
    isDialogOpen.value = false;

  } catch (error: any) {
    // 删除失败，显示 ElMessage 错误消息
    console.error(`删除用户 ${props.username} 失败:`, error);
    ElMessage.error({
      message: error.message || `删除用户 ${props.username} 失败，请稍后重试。`,
      duration: 5000,
    });
    // 可以选择重新抛出错误，如果父组件需要进一步处理
    // throw error;
  }
};
</script>

<template>
  <AlertDialog :open="isDialogOpen" @update:open="isDialogOpen = $event">
    <AlertDialogTrigger as-child>
      <!-- 删除按钮 -->
      <Button
          variant="destructive"
          class="bg-red-500 text-white text-xs hover:bg-red-600 transition-colors py-2 px-3 rounded"
      >
        删除
      </Button>
    </AlertDialogTrigger>
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>确认删除用户？</AlertDialogTitle>
        <AlertDialogDescription>
          您确定要永久删除用户 **{{ props.username }} (ID: {{ props.userId }})** 吗？此操作无法撤销。
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel @click="isDialogOpen = false">取消</AlertDialogCancel>
        <AlertDialogAction @click="handleDelete">确认删除</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>

<style scoped>

</style>