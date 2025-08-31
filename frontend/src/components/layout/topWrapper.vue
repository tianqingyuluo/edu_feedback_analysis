<!-- components/layout/TopWrapper.vue -->
<script setup lang="ts">
import { useRouter } from 'vue-router';
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Menu, X } from "lucide-vue-next";
import { useRoutesStore } from "@/store/routeStore.ts";

const routesStore = useRoutesStore();
const router = useRouter();

const navigateToRoute = (path: string) => {
  router.push(path);
};

const handleDeleteRouteClick = (id: string, event: Event) => {
  event.stopPropagation();
  routesStore.deleteRoute(id);
};
</script>

<template>
  <div>
    <!-- 上半部分：导航栏 - 保持不变 -->
    <div class="bg-gray-100 backdrop-blur-sm p-4 flex items-center justify-between h-16 z-10 border-gray-200">
      <div class="max-w-full mx-auto flex items-center justify-between w-full">
        <div class="flex items-center space-x-4">
          <SidebarTrigger as-child>
            <button class="text-gray-700 hover:text-blue-600 p-2 rounded-full transition-colors">
              <Menu class="h-6 w-6" />
            </button>
          </SidebarTrigger>
          <span class="text-lg font-semibold text-gray-800">我的应用</span>
        </div>
        <div class="flex items-center">
          <button class="text-gray-700 hover:text-blue-600 transition-colors text-lg whitespace-nowrap">
            用户:admin
          </button>
        </div>
      </div>
    </div>

    <!-- 下半部分：动态渲染路由列表 - 每个路由项都是 bg-gray-50 的小按钮/标签 -->
    <div class="bg-gray-100 py-1 px-4 w-full border-gray-200 overflow-hidden h-8">
      <div v-if="routesStore.routeList.length > 0"
           class="flex flex-wrap items-center gap-x-2 gap-y-1 max-w-full mx-auto text-sm">
        <div
            v-for="route in routesStore.routeList"
            :key="route.id"
            @click="navigateToRoute(route.path)"
            class="group-item relative flex items-center bg-gray-50 text-gray-700
                   px-2 py-0.5 rounded-md cursor-pointer hover:bg-gray-200 hover:text-blue-600
                   transition-colors whitespace-nowrap text-sm"
        >
          <span class="truncate">{{ route.name }}</span>

          <!-- 删除按钮，在路由项内部，悬停时出现 -->
          <button
              @click="handleDeleteRouteClick(route.id, $event)"
              class="ml-1 text-gray-400
                     hover:text-red-500 transition-opacity-colors text-[10px] w-4 h-4
                     flex items-center justify-center rounded-full"
              aria-label="删除路由"
              title="删除此路由"
          >
            <X class="h-3 w-3" />
          </button>
        </div>
      </div>
      <div v-else class="text-gray-500 text-center py-1 text-xs max-w-full mx-auto">
        暂无常用路由，点击侧边栏菜单可添加。
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 确保 `white-space-nowrap` 在 Tailwind 中可用，或者使用自定义 CSS */
/* 由于现在每个路由项是一个背景框，不再需要 group 类来控制悬停，
   而是直接在 .group-item 上定义悬停效果和 .group-item:hover .opacity-0 即可。
   不过，为了兼容以前的 group-hover 逻辑，我们仍然可以将其命名为 group-item
   并使用 group-hover。
*/
.group-item.relative:hover .opacity-0 {
  opacity: 100;
}
</style>