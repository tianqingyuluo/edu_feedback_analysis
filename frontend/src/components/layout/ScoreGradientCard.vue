<template>
  <div
      class="gradient-card p-5 rounded-xl shadow-lg flex flex-col justify-between"
      :style="{
      minWidth: '180px',
      maxWidth: '100%',
      width: '100%',
      flex: '1 0 auto',
      minHeight: '160px'
    }"
  >
    <div class="space-y-3">
      <!-- 标题 - 放大字体 -->
      <h3 class="text-white font-semibold text-base">{{ title }}</h3>

      <!-- 分数展示 - 放大数字 -->
      <div class="flex items-end space-x-2">
        <span class="text-white text-4xl font-bold">{{ score1 }}</span>
        <span class="text-white text-opacity-80 text-lg pb-1">/{{ score2 }}</span>
      </div>
    </div>

    <!-- 结论 - 放大字体 -->
    <p
        class="text-white text-sm mt-3 font-medium"
    >
      {{ conclusion }}
    </p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  score1: number
  score2: number
  conclusion: string
}

defineProps<Props>()
</script>

<style scoped>
.gradient-card {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
}
</style>