<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton
} from "@/components/ui/sidebar";
import {useRoute, useRouter} from "vue-router";

const navItems = [
  { name: "概览", path: "/home" },
  { name: "教学质量", path: "/teaching-quality" },
  { name: "学生满意度", path: "/student-satisfaction" },
  { name: "课程评估", path: "/course-evaluation" },
  { name: "教师评价", path: "/teacher-evaluation" },
  { name: "数据管理", path: "/data-management" },
  { name: "系统设置", path: "/system-settings" }
];
const route = useRoute();
const router = useRouter();
const isActiveTab = (tabRoute: string) => {
  return route.path.startsWith(tabRoute);
};
const navigateTo = (path: string) => { // 将参数名改为 path 更清晰
  router.push(path);
};
</script>
<template>
  <!-- 1. 侧栏背景改为白色，移除 bg-gray-800 -->
  <Sidebar collapsible="offcanvas" class="bg-white border-r border-gray-200">
    <SidebarContent>
      <SidebarGroup class="p-0">
        <SidebarMenu class="space-y-1">
          <SidebarMenuItem
              v-for="item in navItems"
              :key="item.path"
              class="py-3 transition-colors duration-200"
              :class="{
                // 3. 悬停效果：悬停时变为浅灰色背景
                'hover:bg-gray-100': !isActiveTab(item.path),
                // 4. 选中状态的背景改为浅蓝色，并增加圆角
                'bg-blue-50 text-blue-600 rounded-lg mx-2': isActiveTab(item.path)
              }"
              @click="navigateTo(item.path)"
          >
            <SidebarMenuButton
                asChild
                class="w-full pointer-events-none"
            >
              <router-link
                  :to="item.path"
                  class="sidebar-link block py-2 text-xl  rounded-none pl-8"
                  :class="{
                    // 2. 选中状态文字变为蓝色
                    'text-blue-600': isActiveTab(item.path),
                    // 2. 默认文字颜色变为黑色
                    'text-gray-900': !isActiveTab(item.path)
                  }"
              >
                {{ item.name }}
              </router-link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroup>
    </SidebarContent>
  </Sidebar>
</template>

<style scoped>
/* 如果有需要，可以在这里添加额外的样式，但 Tailwind 应该足够了 */
/* 确保 Sidebar 组件本身的宽度定义在布局组件中或者它自己有一个默认值 */
</style>