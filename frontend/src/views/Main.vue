<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useDocStore } from '@/store/useDocStore'
import {SidebarProvider} from "@/components/ui/sidebar";
import AppSidebar from "@/components/layout/AppSidebar.vue";
import TopWrapper from "@/components/layout/topWrapper.vue";

/* ---------- 局部 loading ---------- */
const loading = ref(true)

const store = useDocStore()
onMounted(async () => {
  try {
    await store.fetchDocs()
    await store.initKnowledgeBase()
  } catch (e: any) {
    ElMessage.error('初始化失败：' + e.message)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <!-- **** 仅插入这一段：loading 时显示转圈 + 文字 **** -->
  <div v-if="loading" class="init-box">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
    <p>正在加载知识库文档，初次打开本软件需要初始化，可能开启速度较慢，请耐心等待</p>
  </div>

  <!-- **** 以下完全不变 **** -->
  <div v-else class="app-container">
    <SidebarProvider :defaultOpen="true">
      <div class="layout-wrapper">
        <AppSidebar class="app-sidebar w-64 flex-shrink-0" />
        <div class="right-content-area">
          <TopWrapper class="top-wrapper flex-shrink-0" />
          <div class="router-view-container bg-gray-100">
            <router-view />
          </div>
        </div>
      </div>
    </SidebarProvider>
  </div>
</template>

<style scoped>
/* **** 仅新增：loading 盒子（占满可视区域，不影响原布局） **** */
.init-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  color: #374151;
  background: #ffffff;
}

/* **** 以下仍是你原来的样式 **** */
.app-container { display: flex; height: 100vh; overflow: hidden; }
.layout-wrapper { display: flex; flex: 1; height: 100%; }
.app-sidebar { flex-shrink: 0; }
.right-content-area { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
.top-wrapper { flex-shrink: 0; }
.router-view-container { flex: 1; overflow: auto; }
</style>