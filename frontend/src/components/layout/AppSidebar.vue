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
const navigateTo = (route: string) => {
  router.push(route);
};
</script>

<template>
  <Sidebar collapsible="none" class="bg-gray-800">
    <SidebarContent>
      <SidebarGroup class="p-0">
        <SidebarMenu class="space-y-1">
          <SidebarMenuItem v-for="item in navItems" :key="item.path" class="py-3 hover:bg-gray-700 transition-colors duration-200 "
                           @click="navigateTo(item.path)">
            <SidebarMenuButton
                asChild
                class="w-full pointer-events-none"
            >
              <router-link
                  :to="item.path"
                  class="sidebar-link block py-2 text-xl font-bold  rounded-none pl-8 "
                  :class="{'text-blue-400 ': isActiveTab(item.path),
                  'text-white ': !isActiveTab(item.path)}
"
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