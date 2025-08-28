<template>
  <div id="app" class="container mx-auto px-4 py-8">
    <!-- 表格容器 - 变为一个普通的 div -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="flex justify-between items-center p-4">
        <h2 class="text-xl font-semibold text-gray-800">人员管理</h2> <!-- 添加的标题 -->
        <button
            @click="handleAddUser"
            class="px-4 py-2 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition-colors"
        >
          添加人员
        </button>
      </div>
      <!-- 表头 - 使用 div 模拟 -->
      <div class="flex items-center gap-4 px-6 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200">
        <!-- 姓名列头 - 占据 20% 宽度 -->
        <div class="w-1/5 text-left py-1">姓名</div>

        <!-- 权限列头 - 占据 20% 宽度 -->
        <div class="w-1/5 text-left py-1">权限</div>

        <!-- 空白列头 - 自动填充剩余空间 (flex-grow) -->
        <div class="flex-grow py-1"></div>

        <!-- 操作列头 - 占据 20% 宽度，左对齐 -->
        <div class="w-1/5 text-left py-1 max-w-[150px]">操作</div>
      </div>
      <!-- 表体 - 使用 v-for 渲染 div 模拟行 -->
      <div class="divide-y divide-gray-200">
        <div v-for="(user, index) in users" :key="user.id" class="flex items-center gap-4 px-6 py-4 text-sm text-gray-500 hover:bg-gray-50">
          <!-- 姓名列 - 占据 20% 宽度 -->
          <div class="w-1/5 font-medium text-xl text-gray-900">{{ user.name }}</div>
          <!-- 权限列 - 占据 20% 宽度 -->
          <div class="w-1/5">{{ user.permission }}</div>
          <!-- 空白 div - 自动填充剩余空间 (flex-grow) -->
          <div class="flex-grow"></div>
          <!-- 操作按钮 div - 占据 20% 宽度，内容左对齐 -->
          <div class="w-1/5 text-left max-w-[150px]">
            <!-- 保持 flex 和 flex-wrap，但将 gap 调回 4 或其他更大的值，
                 并添加 justify-between 尝试将按钮推到两端。 -->
            <div class="flex flex-wrap gap-4 justify-between">
              <Button
                  @click="handleManagePermissions(user)"
                  class="bg-blue-500 text-white text-xs hover:bg-blue-600 transition-colors py-2 px-3 rounded"
              >
                管理权限
              </Button>
              <Button
                  @click="handleDeleteUser(user)"
                  class="bg-red-500 text-white text-xs hover:bg-red-600 transition-colors py-2 px-3 rounded"
              >
                删除
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Button from '@/components/ui/button/Button.vue';
// 假数据
const users = ref([
  { id: 1, name: '张三', permission: '管理员' },
  { id: 2, name: '李四', permission: '编辑' },
  { id: 3, name: '王五', permission: '观察者' },
  { id: 4, name: '赵六', permission: '编辑' },
  { id: 5, name: '孙七', permission: '管理员' }
]);

// 删除用户处理函数
const handleDeleteUser = (user) => {
  console.log('删除用户:', user);
  // 在实际应用中，这里会调用API进行删除
  // 这里我们只做前端演示，将用户从列表中移除
  users.value = users.value.filter(u => u.id !== user.id);
  alert(`已删除用户: ${user.name}`);
};

// 管理权限处理函数
const handleManagePermissions = (user) => {
  console.log('管理权限:', user);
  // 在实际应用中，这里会打开一个模态框或跳转到权限管理页面
  alert(`管理用户 ${user.name} 的权限`);
  // 示例：更改用户的权限 (仅为演示，实际应用可能更复杂)
  const newPermission = prompt(`请为用户 ${user.name} 输入新的权限 (当前: ${user.permission}):`);
  if (newPermission !== null && newPermission.trim() !== '') {
    user.permission = newPermission.trim();
    alert(`用户 ${user.name} 的权限已更新为: ${newPermission.trim()}`);
  }
};

// 添加人员处理函数
const handleAddUser = () => {
  console.log('添加人员');
  // 在实际应用中，这里会打开一个表单或模态框让用户输入人员信息
  // 这里我们只是演示，添加一个假的 newUser
  const newUserName = prompt('请输入新人员的用户名:');
  if (newUserName !== null && newUserName.trim() !== '') {
    const newUser = {
      id: users.value.length ? Math.max(...users.value.map(u => u.id)) + 1 : 1,
      name: newUserName.trim(),
      permission: '观察者' // 默认权限
    };
    users.value.push(newUser);
    alert(`已添加新人员: ${newUser.name}`);
  }
};
</script>

<style scoped>
/* 可以根据需要添加额外的scoped样式 */
</style>