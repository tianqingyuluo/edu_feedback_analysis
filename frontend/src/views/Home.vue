<template>
  <div class="dashboard-layout p-6 bg-gray-100 h-[80vh] flex flex-col">
    <!-- 顶部菜单 -->
    <div class="flex items-center justify-between mb-4 p-1 rounded-lg bg-white shadow-sm">
      <!-- 左侧图表切换 -->
      <div class="flex space-x-2">
        <div
            v-for="key in ChartName"
            :key="key"
            @click="activeChart = key"
            :class="menuItemClass(key)"
        >
          {{ key }}
        </div>
      </div>

      <!-- 右侧 AI 聊天按钮 -->
      <Dialog>
        <DialogTrigger as-child>
          <Button variant="outline">AI 聊天</Button>
        </DialogTrigger>
        <DialogContent
            class="sm:max-w-[700px] grid-rows-[auto_minmax(0,1fr)_auto] p-0 max-h-[90dvh]"
        >
          <DialogHeader class="p-6 pb-0">
            <DialogTitle>AI 智能对话</DialogTitle>
          </DialogHeader>

          <div class="overflow-y-auto px-6 min-h-[80vh]">
            <AIchat  class="h-full"/>
          </div>
        </DialogContent>
      </Dialog>
    </div>
    <!--把你的图表往这个图表区加，一页一个，后续可能会有ai点评字段，加在原本的图表里，直接把这个文件当父组件，子图表通过prop获取 -->
    <!-- 图表区 -->
    <div class="flex-1 min-h-[80vh]">
      <EHI v-if="activeChart === 'EHI'" />
      <RPI v-if="activeChart === 'RPI'" />
      <BubbleChart v-if="activeChart === 'Bubble'" />
      <MetricChart v-if="activeChart === 'Metric'" />
      <TimePie v-if="activeChart === 'pie'" />
      <IPD v-if="activeChart === 'IPD'" />
      <DPFE v-if="activeChart === 'DPFE'" />
      <CSI v-if="activeChart === 'CSI'" />
      <!-- AIchat 已移到 Dialog，不再在这里渲染 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import { useRoute } from 'vue-router'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

import EHI from '@/views/EHI.vue'
import RPI from '@/views/RPI.vue'
import BubbleChart from '@/views/BubbleChart.vue'
import MetricChart from '@/views/Metric.vue'
import TimePie from '@/views/TimePie.vue'
import IPD from '@/views/IPD.vue'
import DPFE from '@/views/DPFE.vue'
import CSI from '@/views/CSI.vue'
import AIchat from '@/views/AIchat/AIchat.vue'

import AnalysisService from '@/api/analysis'

//下面是类型导入，如果需要可以导入一下
import { buildAcademiesWithOverall } from '@/utils/academyBuilder'
import { buildTimeAcademies } from '@/utils/buildTimeData'
import type { Academy } from '@/types/majorModels'
import type { MetricGroup } from '@/types/Metric'
import {studentTypeData} from "@/types/IPDValues.ts";

import type {studentTypeStruct,twoDimensionalStruct,threeDimensionalStruct} from "@/types/IPDValues.ts";
import type{satisfactionPartStruct,heatmapStruct} from "@/types/DPFEValues.ts";
import {
  type satisfactionDistributionStruct,
  type overallSatisfactionStruct,
  type SatisfactionContributionStruct,
  satisfactionDistributionData, overallSatisfactionData, SatisfactionContributionData
} from "@/types/CSIValues.ts";

const route = useRoute()
const reportId = ref<string>(route.params.reportId as string)
//取一个名字加在 ChartName， ChartName里（上面的是类，下面的是实例），和图表区的名字对的上就行
/* ---------- 图表切换 ---------- */
type ChartName = 'EHI' | 'RPI' | 'Bubble' | 'Metric' | 'pie' | 'IPD' | 'DPFE' | 'CSI'
const activeChart = ref<ChartName>('EHI')
const  ChartName: ChartName[] = ['EHI', 'RPI', 'Bubble', 'Metric', 'pie', 'IPD', 'DPFE', 'CSI']
//动态选中样式，不用管
const menuItemClass = (key: ChartName) => [
  'px-4 py-2 rounded-md cursor-pointer text-sm font-medium transition',
  activeChart.value === key
      ? 'bg-blue-600 text-white shadow'
      : 'text-gray-700 hover:bg-gray-200',
]
//需要什么数据在这里加一个变量
/* ---------- 数据提供 ---------- */
const academies = ref<Academy[]>([])
const rpiAcademies = ref<Academy[]>([])
const bubbleData = ref<MetricGroup[]>([])
const trendData = ref<MetricGroup[]>([])
const rawTimeData = ref<Academy[]>([])

const IPDStudentTypeData = ref<studentTypeStruct>();
const IPDTwoDimensionalData = ref<twoDimensionalStruct>();
const IPDThreeDimensionalData = ref<threeDimensionalStruct>();

const DPFESatisfactionPartData = ref<satisfactionPartStruct>();
const DPFEHeatmapData = ref<heatmapStruct>();

const SCIOSatisfactionDistributionStruct=ref<satisfactionDistributionStruct>();
const SCISOverallSatisfactionStruct=ref<overallSatisfactionStruct>();
const SCISSatisfactionContributionStruct=ref<SatisfactionContributionStruct>();

//通过provide提供给下游组件
provide('academies', academies)
provide('rpiAcademies', rpiAcademies)
provide('bubbleData', bubbleData)
provide('trendData', trendData)
provide('timeAcademies', rawTimeData)

provide('IPDStudentTypeData', IPDStudentTypeData)
provide('IPDTwoDimensionalData', IPDTwoDimensionalData)
provide('IPDThreeDimensionalData', IPDThreeDimensionalData)

provide('DPFESatisfactionPartData', DPFESatisfactionPartData)
provide('DPFEHeatmapData', DPFEHeatmapData)

provide('SCIOSatisfactionDistributionStruct', SCIOSatisfactionDistributionStruct)
provide('SCISOverallSatisfactionStruct', SCISOverallSatisfactionStruct)
provide('SCISSatisfactionContributionStruct', SCISSatisfactionContributionStruct)
//这里是拉取数据的逻辑，到时候会调用cwh的方法，把我们后端生成的数据传给每一个要传下去的变量
/* ---------- 一次性拉数据 ---------- */
onMounted(async () => {
  const response = await AnalysisService.getResults(reportId.value)
  const model =await import('@/components/layout/willbedeleted/mock.json')//const result = response.model_predictions

  const model_predictions =model.message.model_predictions
  const statistical_analyses =model.message.statistical_analyses

  academies.value = statistical_analyses.correlation_based_EHI_builder
  rpiAcademies.value = statistical_analyses.correlation_based_RPI_builder
  bubbleData.value =statistical_analyses.teacher_student_interaction_bubble_chart
  trendData.value =statistical_analyses.academic_maturity_by_grade_aggregator
  rawTimeData.value = statistical_analyses.student_time_allocation_pie_chart

  const { studentTypeData, twoDimensionalData, threeDimensionalData } = await import('@/types/IPDValues.ts');
  IPDStudentTypeData.value = studentTypeData;
  IPDTwoDimensionalData.value = twoDimensionalData;
  IPDThreeDimensionalData.value = threeDimensionalData;
  
  const { satisfactionPartData, heatmapData } = await import('@/types/DPFEValues.ts');
  DPFESatisfactionPartData.value = satisfactionPartData;
  DPFEHeatmapData.value = heatmapData;
  
  const { satisfactionDistributionData, overallSatisfactionData, SatisfactionContributionData } = await import('@/types/CSIValues.ts');
  SCIOSatisfactionDistributionStruct.value = satisfactionDistributionData
  SCISOverallSatisfactionStruct.value = overallSatisfactionData;
  SCISSatisfactionContributionStruct.value = SatisfactionContributionData;
  
  
  
  
})

</script>

<style scoped>
.dashboard-layout {
  font-family: 'Inter', sans-serif;
}
</style>