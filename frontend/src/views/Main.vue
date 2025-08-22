<script setup lang="ts">
import topWrapper from "@/components/layout/topWrapper.vue";
import AppSidebar from "@/components/layout/AppSidebar.vue";
import { SidebarProvider } from "@/components/ui/sidebar";
</script>

<template>
  <div class="app-container">
    <topWrapper class="min-w-[900px]"/>
    <SidebarProvider>
      <div class="main-content-wrapper">
        <AppSidebar class="sticky top-[4.75rem] h-[calc(100vh-4.75rem)] overflow-y-auto"/>
        <div class="router-view-container">
          <router-view></router-view>
        </div>
      </div>
    </SidebarProvider>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content-wrapper {
  display: flex;
  flex: 1;
  position: relative;
}

.router-view-container {
  flex: 1;
  overflow: auto;
  margin-top: 4.75rem;
}
</style>