<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();
const tabs = [
  { title: '首页', route: '/home' },
  { title: '数据', route: '/data' },
  { title: '分析', route: '/analysis' },
  { title: '对话', route: '/chat' }
];

const navigateTo = (route: string) => {
  router.push(route);
};

const isActiveTab = (tabRoute: string) => {
  return route.path.startsWith(tabRoute);
};
</script>

<template>
  <!-- 顶部导航栏容器 -->
  <div class="fixed top-0 left-0 right-0 z-50 bg-gray-900 backdrop-blur-sm p-4 shadow-md">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <!-- 左侧：系统标题 -->
      <div class="absolute left-8">
        <span class="text-white font-bold text-2xl whitespace-nowrap">教育质量分析系统</span>
      </div>

      <!-- 中间：导航菜单 -->
      <div class="flex-1 flex justify-center">
        <div class="flex space-x-1">
          <button
              v-for="tab in tabs"
              :key="tab.route"
              @click="navigateTo(tab.route)"
              class="px-6 py-2  rounded-lg text-center text-lg font-medium transition-all duration-200 "
              :class="{
              'text-blue-400 ': isActiveTab(tab.route),
              'text-white hover:text-blue-300 ': !isActiveTab(tab.route)
            }"
          >
            {{ tab.title }}
          </button>
        </div>
      </div>

      <!-- 右侧：用户信息 -->
      <div class="absolute right-8">
        <button class="text-white hover:text-blue-300 transition-colors text-lg whitespace-nowrap">
          用户:admin
        </button>
      </div>
    </div>
  </div>
</template>