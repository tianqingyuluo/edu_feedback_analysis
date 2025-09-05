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
import { useRoutesStore } from '@/store/routeStore.ts';
import type { AppRoute } from '@/store/routeStore.ts'; // 导入 AppRoute 类型以供使用

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
const routesStore = useRoutesStore(); // 初始化 Pinia store

const isActiveTab = (tabRoute: string) => {
  return route.path.startsWith(tabRoute);
};

// 修改 navigateTo (或者使用 item.path 和 item.name)
const navigateTo = (item: { path: string; name: string }) => {
  // 1. 检查 routesStore 中是否已存在相同路径的路由，避免重复添加
  const exists = routesStore.routeList.some((r: AppRoute) => r.path === item.path);

  if (!exists) {
    // 2. 将当前路由添加到 Pinia Store
    // 注意：addRoute 期待 path 和 name 作为参数
    routesStore.addRoute(item.path, item.name);
  }

  // 3. 执行路由跳转
  router.push(item.path);
};
</script>

<template>
  <Sidebar collapsible="offcanvas" class="bg-white border-r border-gray-200 max-w-[192px]">
    <SidebarContent>
      <SidebarGroup class="p-0">
        <SidebarMenu class="space-y-1">
          <SidebarMenuItem
              v-for="item in navItems"
              :key="item.path"
              class="py-3 transition-colors duration-200"
              :class="{
                'hover:bg-gray-100': !isActiveTab(item.path),
                'bg-blue-50 text-blue-600 rounded-lg mx-2': isActiveTab(item.path)
              }"
              @click="navigateTo(item)"
          >
          <SidebarMenuButton
              asChild
              class="w-full pointer-events-none"
          >
            <router-link
                :to="item.path"
                class="sidebar-link block py-2 text-[18px] rounded-none pl-8"
                :class="{
                    'text-blue-600': isActiveTab(item.path),
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
</style>