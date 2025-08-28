<script setup lang="ts">
// 导入 SidebarTrigger
import { SidebarTrigger } from "@/components/ui/sidebar";

import { Menu } from "lucide-vue-next";
</script>
<template>
  <div class="bg-gray-100 backdrop-blur-sm p-4 flex items-center justify-between h-16">
    <div class="max-w-full mx-auto flex items-center justify-between w-full"> <!-- max-w-7xl 可能会限制宽度 -->
      <!-- 左侧：系统标题 -->
      <div class="flex items-center space-x-4">
        <!-- 侧边栏触发器放在左侧，与标题相邻 -->
        <SidebarTrigger as-child>
          <button class="text-white hover:text-blue-300 p-2 rounded-full">
            <Menu class="h-6 w-6" /> <!-- 使用 Menu 图标 -->
          </button>
        </SidebarTrigger>
      </div>
      <!-- 右侧：用户信息 -->
      <div class="flex items-center">
        <button class=" hover:text-blue-300 transition-colors text-lg whitespace-nowrap">
          用户:admin
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 无需特殊的 scoped 样式，Tailwind 即可 */
</style>