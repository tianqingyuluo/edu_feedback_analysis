<script setup lang="ts">
import ImgIndex from '@/Test/Index.vue'
import ExcelManagement from './views/ExcelManagement.vue';
import EHI from './views/EHI.vue';
import RPI from './views/RPI.vue';
</script>

<template>
  <!-- 根容器，通常包含全局布局（如导航栏、页脚） -->
  <div id="app">
<!--    <ImgIndex/>-->
<!--    <ExcelManagement/>-->
    <router-view/>
<!--    <EHI/>-->
<!--    <RPI/>-->
  </div>
</template>
