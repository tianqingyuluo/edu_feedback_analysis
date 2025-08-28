<script setup lang="ts">
import AppSidebar from "@/components/layout/AppSidebar.vue";
import { SidebarProvider } from "@/components/ui/sidebar";
// 确保导入的组件名称与实际文件名匹配，通常首字母大写
import TopWrapper from "@/components/layout/topWrapper.vue";
</script>
<template>
  <div class="app-container">
    <SidebarProvider :defaultOpen="true"> <!-- 初始状态设置为打开 -->
      <div class="layout-wrapper">
        <AppSidebar class="app-sidebar w-64 flex-shrink-0" />
        <!-- 右侧内容区域（包含顶栏和主内容） -->
        <div class="right-content-area">
          <TopWrapper class="top-wrapper flex-shrink-0" />
          <!-- 主内容区域在顶栏下方，横跨右侧区域剩余空间 -->
          <div class="router-view-container bg-gray-100">
            <router-view></router-view>
          </div>
        </div>
      </div>
    </SidebarProvider>
  </div>
</template>
<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden; /* 防止整个页面滚动 */
}
.layout-wrapper {
  display: flex; /* 使得 AppSidebar 和 right-content-area 左右分布 */
  flex: 1; /* 占据 app-container 的所有空间 */
  height: 100%; /* 确保高度填充 app-container */
}
/* AppSidebar 样式 */
.app-sidebar {
  flex-shrink: 0;
}
.right-content-area {
  display: flex;
  flex-direction: column; /* 使得 TopWrapper 和 router-view-container 垂直分布 */
  flex: 1; /* 占据 layout-wrapper 除去 AppSidebar 后的所有剩余宽度 */
  overflow: hidden; /* 隐藏自身的滚动条，让子元素控制 */
}
.top-wrapper {
  flex-shrink: 0; /* 阻止顶栏被压缩 */
  /* top-wrapper 的高度现在应该由它自身组件内部控制，例如 h-16 */
}
.router-view-container {
  flex: 1; /* 占据 right-content-area 除去 TopWrapper 后的所有剩余垂直空间 */
  overflow: auto; /* 允许 router-view-container 内部内容滚动 */
}
</style>