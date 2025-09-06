<template>
  <div class="dashboard-layout p-6 bg-gray-100 h-[80vh]">
    <EHI v-if="academies"/>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import EHI from '@/views/EHI.vue'
import { buildAcademiesWithOverall } from '@/utils/academyBuilder'
import type { Academy } from '@/types/majorModels'

/* 1. 占位：以后换成真实接口即可 */
async function getFakeData() {
  // 这里先同步返回假数据，模拟异步可改成 await fetch()
  const { defaultAcademyData } = await import('@/types/majorModels')
  return defaultAcademyData
}

const academies = ref<Academy[]>([])

onMounted(async () => {
  const raw = await getFakeData()          // 2. 拿原始数据
  academies.value = buildAcademiesWithOverall(raw) // 3. 加工
})

/* 4. 一次性扔给所有后代 */
provide('academies', academies)
</script>

<style scoped>
.dashboard-layout {
  font-family: 'Inter', sans-serif;
}
</style>