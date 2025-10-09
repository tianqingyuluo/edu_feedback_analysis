<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton
} from '@/components/ui/sidebar'
import { useRoute, useRouter } from 'vue-router'
import { useRoutesStore } from '@/store/routeStore'
import type { AppRoute } from '@/store/routeStore'
import { computed} from 'vue'
import { useUserStore } from '@/store/userStore'

/* ---------- 权限常量 ---------- */
type Role = 'ADMIN' | 'OPERATOR' | 'USER'

/* ---------- 导航配置 ---------- */
interface NavItem {
  name: string
  path: string
  access: Role[]   // 允许访问的角色
}

const navItems: NavItem[] = [
  { name: '数据管理', path: '/admin/data-hub',    access: ['ADMIN', 'OPERATOR'] },
  { name: '人员管理', path: '/admin/user-mgmt',   access: ['ADMIN'] },
  { name: '分析管理', path: '/admin/analytics',   access: ['ADMIN', 'OPERATOR', 'USER'] },
  { name: '向量库文档管理',path :'/admin/Document' ,access: ['ADMIN']}
]

/* ---------- 路由与权限 ---------- */
const route = useRoute()
const router = useRouter()
const routesStore = useRoutesStore()
const userStore = useUserStore()

/* 当前用户角色（大写） */
const userRole = computed<Role>(() => (userStore.userInfo?.role || 'ADMIN').toUpperCase() as Role)

/* 根据权限过滤后的菜单 */
const allowedNavItems = computed(() =>
    navItems.filter(item => item.access.includes(userRole.value))
)

/* 激活样式 */
const isActiveTab = (tabRoute: string) => route.path.startsWith(tabRoute)

/* 跳转逻辑 */
const navigateTo = (item: NavItem) => {
  const exists = routesStore.routeList.some((r: AppRoute) => r.path === item.path)
  if (!exists) routesStore.addRoute(item.path, item.name)
  router.push(item.path)
}
</script>

<template>
  <Sidebar
      collapsible="offcanvas"
      class="bg-white border-r border-gray-200 max-w-[12rem]"
  >
    <div class="px-6 py-4 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-900">管理系统</h2>
    </div>

    <SidebarContent>
      <SidebarGroup class="p-0">
        <SidebarMenu class="flex flex-col gap-1 px-2 py-2">
          <!-- 只渲染有权限的菜单 -->
          <SidebarMenuItem
              v-for="item in allowedNavItems"
              :key="item.path"
              class="py-3 transition-colors duration-200"
              :class="{
              'hover:bg-gray-100': !isActiveTab(item.path),
              'bg-blue-50 text-blue-600 rounded-lg mx-2': isActiveTab(item.path)
            }"
              @click="navigateTo(item)"
          >
            <SidebarMenuButton as-child class="w-full pointer-events-none">
              <router-link
                  :to="item.path"
                  :class="[
                  'block w-full px-4 text-[18px]',
                  isActiveTab(item.path)
                    ? 'text-blue-600 font-medium'
                    : 'text-gray-900'
                ]"
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