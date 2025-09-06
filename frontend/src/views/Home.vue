<template>
  <div class="dashboard-layout p-6 bg-gray-100 h-[80vh] flex flex-col">
    <!-- 1. 横向 Menubar 菜单栏（使用 div 模拟） -->
    <div class="flex space-x-2 mb-4 p-1 rounded-lg bg-white shadow-sm">
      <div
          @click="activeChart = 'EHI'"
          :class="[
          'px-4 py-2 rounded-md cursor-pointer text-sm font-medium transition-colors duration-200 ease-in-out',
          activeChart === 'EHI'
            ? 'bg-blue-600 text-white shadow'
            : 'text-gray-700 hover:bg-gray-200'
        ]"
      >
        EHI
      </div>
      <div
          @click="activeChart = 'RPI'"
          :class="[
          'px-4 py-2 rounded-md cursor-pointer text-sm font-medium transition-colors duration-200 ease-in-out',
          activeChart === 'RPI'
            ? 'bg-blue-600 text-white shadow'
            : 'text-gray-700 hover:bg-gray-200'
        ]"
      >
        RPI
      </div>
    </div>
    <!-- 2. 单图表渲染区域 -->
    <div class="flex-1">
      <EHI v-if="activeChart === 'EHI'" />
      <RPI v-if="activeChart === 'RPI'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import EHI from '@/views/EHI.vue'
import RPI from '@/views/RPI.vue'
import { buildAcademiesWithOverall } from '@/utils/academyBuilder'
import type { Academy } from '@/types/majorModels'
import { useRoute } from 'vue-router'

const route = useRoute()
const reportId = ref<string>(route.params.reportId as string)

async function getFakeData() {
  const { defaultAcademyData } = await import('@/types/majorModels')
  return defaultAcademyData
}

const academies = ref<Academy[]>([])
const rpiAcademies = ref<Academy[]>([])

onMounted(async () => {
  const raw = await getFakeData()
  academies.value = buildAcademiesWithOverall(raw)
  rpiAcademies.value = buildAcademiesWithOverall(raw)
})

type ChartName = 'EHI' | 'RPI'
const activeChart = ref<ChartName>('EHI')

// 提供数据给子组件
provide('academies', academies)
provide('rpiAcademies', rpiAcademies)
</script>

<style scoped>
.dashboard-layout {
  font-family: 'Inter', sans-serif;
}
</style>