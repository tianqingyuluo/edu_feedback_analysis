<template>
  <div class="dashboard-layout p-6 bg-gray-100 h-[80vh] flex flex-col">
    <!-- 顶部菜单 -->
    <div class="flex space-x-2 mb-4 p-1 rounded-lg bg-white shadow-sm">
      <div @click="activeChart = 'EHI'"   :class="menuItemClass('EHI')">EHI</div>
      <div @click="activeChart = 'RPI'"   :class="menuItemClass('RPI')">RPI</div>
      <div @click="activeChart = 'Bubble'" :class="menuItemClass('Bubble')">Bubble</div>
      <div @click="activeChart = 'Metric'" :class="menuItemClass('Metric')">Metric</div>
      <div @click="activeChart = 'pie'" :class="menuItemClass('pie')">pie</div>
    </div>

    <!-- 图表区 -->
    <div class="flex-1">
      <EHI        v-if="activeChart === 'EHI'" />
      <RPI        v-if="activeChart === 'RPI'" />
      <BubbleChart v-if="activeChart === 'Bubble'" />
      <MetricChart v-if="activeChart === 'Metric'" />
      <TimePie v-if="activeChart==='pie'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import EHI from '@/views/EHI.vue'
import RPI from '@/views/RPI.vue'
import BubbleChart from '@/views/BubbleChart.vue'
import MetricChart from '@/views/Metric.vue'
import { buildAcademiesWithOverall } from '@/utils/academyBuilder'
import type { Academy } from '@/types/majorModels'
import {type MetricGroup} from '@/types/Metric'
import { useRoute } from 'vue-router'
import TimePie from "@/views/TimePie.vue";
import {buildTimeAcademies} from "@/utils/buildTimeData.ts";

const route = useRoute()
const reportId = ref<string>(route.params.reportId as string)
//加一个图就往ChartName后加一个阻断
type ChartName = 'EHI' | 'RPI' | 'Bubble' | 'Metric' | 'pie'
const activeChart = ref<ChartName>('EHI')//决定现在选择哪个页
//数据都写在一起，导入类型，确保类型正确
/* ---------- 数据 ---------- */
const academies      = ref<Academy[]>([])
const rpiAcademies   = ref<Academy[]>([])
const bubbleData     = ref<MetricGroup[]>([])   // 气泡图专用
const trendData      = ref<MetricGroup[]>([]) // 趋势图专用
const rawTimeData = ref<Academy[]>([])//饼图专用
//后续组件都最为这个组件的下游组件，这个组件统一 provide，下游组件通过inject接受
/* ---------- 统一 provide ---------- */
provide('academies',      academies)
provide('rpiAcademies',   rpiAcademies)
provide('bubbleData',     bubbleData)   // 气泡图
provide('trendData',      trendData)    // 趋势图
provide('timeAcademies',  rawTimeData)//饼图
//下面是拉数据的函数，目前逻辑不正确，将假数据贴进去即可，后续会正确返回后端数据
/* ---------- 一次性拉数据 ---------- */
onMounted(async () => {
  // 1. 基础学院数据
  const { defaultAcademyData } = await import('@/types/majorModels')
  academies.value    = buildAcademiesWithOverall(defaultAcademyData)
  rpiAcademies.value = buildAcademiesWithOverall(defaultAcademyData)

  // 2. 气泡图需要的 metrics
  const { default: academiesData } = await import('@/components/layout/willbedeleted/bubble_data.json')
  bubbleData.value = academiesData as MetricGroup[]

  //3.趋势图需要的数据
  const {defaultMetricData}=await import('@/types/Metric')
  trendData.value = defaultMetricData
  //4.饼图需要的数据
  const { default: timeAcademies } = await import('@/components/layout/willbedeleted/compact_time_data.json')
  rawTimeData.value = buildTimeAcademies(timeAcademies)
})

/* ---------- 菜单样式 ---------- */
const menuItemClass = (key: ChartName) => [
  'px-4 py-2 rounded-md cursor-pointer text-sm font-medium transition',
  activeChart.value === key
      ? 'bg-blue-600 text-white shadow'
      : 'text-gray-700 hover:bg-gray-200'
]
</script>
<style scoped>
.dashboard-layout { font-family: 'Inter', sans-serif; }
</style>