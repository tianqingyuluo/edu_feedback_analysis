<template>
  <div class="card-container p-5 rounded-xl shadow-lg flex flex-col bg-white transition-transform duration-200 hover:-translate-y-0.5 min-w-[180px] w-full h-[320px]">
    <!-- 文字区域 -->
    <div class="text-content mb-4">
      <h3 class="text-gray-800 font-semibold text-base">{{ text }}</h3>
    </div>

    <!-- 图片容器：固定高度，允许图片变形 -->
    <div class="image-content rounded-lg overflow-hidden flex-1 min-h-0">
      <img
          :src="imageUrl"
          :alt="text || '卡片图片'"
          class="w-full h-full object-center"
      >
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  text: string
  imageUrl: string
}

defineProps<Props>()
</script>