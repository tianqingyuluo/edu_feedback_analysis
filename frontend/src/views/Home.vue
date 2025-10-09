<template>
  <div class="dashboard-layout p-6 bg-gray-100 h-[80vh] flex flex-col">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">数据加载中...</p>
      </div>
    </div>

    <!-- 内容区域 -->
    <div v-else>
      <!-- 顶部菜单 -->
      <div class="flex items-center justify-between mb-4 p-1 rounded-lg bg-white shadow-sm">
        <!-- 左侧图表切换 -->
        <div class="relative flex-1 flex items-center">
          <!-- 左箭头 -->
          <button
              @click="prevPage"
              :disabled="!canPrev"
              class="px-2 py-1 rounded-md text-gray-600 hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <!-- 当前 7 个按钮 -->
          <div class="flex space-x-2 px-2">
            <div
                v-for="key in currentButtons"
                :key="key"
                @click="activeChart = key"
                :class="menuItemClass(key)"
            >
              {{ key }}
            </div>
          </div>

          <button
              @click="nextPage"
              :disabled="!canNext"
              class="absolute right-0 top-1/2 -translate-y-1/2 px-2 py-1 rounded-md text-gray-600 hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        <!-- 右侧 AI 聊天按钮 -->
        <Dialog v-model:open="dialogOpen">
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

      <!-- 图表区 -->
      <div class="flex-1 min-h-[80vh]">
        <EHI v-if="activeChart === '学业综合健康指数'" />
        <RPI v-if="activeChart === '学生资源感知指数'" />
        <BubbleChart v-if="activeChart === '师生互动关联气泡图'" />
        <MetricChart v-if="activeChart === '学业成熟度跨年级对比'" />
        <TimePie v-if="activeChart === '学生时间分配饼图'" />
        <IPD v-if="activeChart === '学生画像分布'" />
        <DPFE v-if="activeChart === '学生多方面满意度'" />
        <CSI v-if="activeChart === '学生整体满意度'" />
        <what-if-dialog v-if="activeChart==='whatIf选择器'" :dataid="dataId" :taskid="reportId"/>
        <SankeyFlow v-if="activeChart==='满意度组成桑基图'"/>
        <!-- AIchat 已移到 Dialog，不再在这里渲染 -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, provide, computed} from 'vue'
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
import WhatIfDialog from "@/views/WhatIfDialog.vue";
import SankeyFlow from "@/views/SankeyFlow.vue";
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
} from "@/types/CSIValues.ts";
import type {GraphData} from "@/types/sankey.ts";
import AnalysisService from "@/api/analysis.ts";
import type {Comments} from "@/types/analysis.ts";


const comments = ref<Comments>({} as Comments)   // 空对象先占住类型
provide('comments', comments)
const dialogOpen = ref(false)
const openChatDialog = () => (dialogOpen.value = true)
provide('openChatDialog', openChatDialog)
const route = useRoute()
const reportId = ref<string>(route.params.reportId as string)
const dataId = ref<string>(route.params.dataId as string)
//取一个名字加在 ChartName， ChartName里（上面的是类，下面的是实例），和图表区的名字对的上就行
/* ---------- 图表切换 ---------- */
type ChartName = '学业综合健康指数' | 'whatIf选择器' | '学生资源感知指数' | '师生互动关联气泡图' | '学业成熟度跨年级对比' | '学生时间分配饼图' | '学生画像分布' | '学生多方面满意度' | '学生整体满意度' | '满意度组成桑基图'
const activeChart = ref<ChartName>('学业综合健康指数')
const  ChartName: ChartName[] = ['学业综合健康指数', 'whatIf选择器', '学生资源感知指数', '师生互动关联气泡图', '学业成熟度跨年级对比', '学生时间分配饼图', '学生画像分布', '学生多方面满意度', '学生整体满意度', '满意度组成桑基图']
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
const sankeyData = ref<GraphData>()

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
provide('sankeyData', sankeyData)

provide('IPDStudentTypeData', IPDStudentTypeData)
provide('IPDTwoDimensionalData', IPDTwoDimensionalData)
provide('IPDThreeDimensionalData', IPDThreeDimensionalData)

provide('DPFESatisfactionPartData', DPFESatisfactionPartData)
provide('DPFEHeatmapData', DPFEHeatmapData)

provide('SCIOSatisfactionDistributionStruct', SCIOSatisfactionDistributionStruct)
provide('SCISOverallSatisfactionStruct', SCISOverallSatisfactionStruct)
provide('SCISSatisfactionContributionStruct', SCISSatisfactionContributionStruct)


const loading = ref(true)
//这里是拉取数据的逻辑，到时候会调用cwh的方法，把我们后端生成的数据传给每一个要传下去的变量
/* ---------- 一次性拉数据 ---------- */
onMounted (async() => {
  try {
    loading.value = true

    const response = await AnalysisService.getResults(reportId.value)
    // const response =await import('@/components/layout/willbedeleted/mock.json')
    console.log(response)
    const model = response

    const model_predictions = model.model_predictions
    const statistical_analyses = model.statistical_analyses
    comments.value = model.comments
    // 设置数据
    academies.value = statistical_analyses.correlation_based_EHI_builder
    rpiAcademies.value = statistical_analyses.correlation_based_RPI_builder
    bubbleData.value = statistical_analyses.teacher_student_interaction_bubble_chart
    trendData.value = statistical_analyses.academic_maturity_by_grade_aggregator
    rawTimeData.value = statistical_analyses.student_time_allocation_pie_chart
    sankeyData.value = statistical_analyses.student_satisfaction_route_sankey_chart
    // sankeyData.value = {'nodes': [{'name': '综合满意度'}, {'name': '学习投入度'}, {'name': '初始资源感知'}, {'name': '专业课体验'}, {'name': '师生关系'}], 'links': [{'source': '初始资源感知', 'target': '学习投入度', 'value': 0.6144438611962052}, {'source': '师生关系', 'target': '学习投入度', 'value': 0.01041381570427746}, {'source': '初始资源感知', 'target': '专业课体验', 'value': 0.5029164697631084}, {'source': '师生关系', 'target': '专业课体验', 'value': 0.3434227158829257}, {'source': '学习投入度', 'target': '综合满意度', 'value': -0.0034114560839615658}, {'source': '专业课体验', 'target': '综合满意度', 'value': 0.3438874686335253}, {'source': '初始资源感知', 'target': '综合满意度', 'value': 0.7070912793006805}]}
    IPDStudentTypeData.value = model.statistical_analyses.student_portrait_chart.studentTypeData;
    IPDTwoDimensionalData.value = {
      pca_scatter: model.statistical_analyses.student_portrait_chart.pca_scatter
    };
    IPDThreeDimensionalData.value = {
      pca_3d_scatter: model.statistical_analyses.student_portrait_chart.pca_3d_scatter
    }

    DPFESatisfactionPartData.value = model.statistical_analyses.satisfaction_part_chart.satisfactionPartData
    DPFEHeatmapData.value = model.statistical_analyses.satisfaction_part_chart.heatmapData;

    SCIOSatisfactionDistributionStruct.value = model.statistical_analyses.satisfaction_whole_chart.satisfactionDistributionData;
    SCISOverallSatisfactionStruct.value = model.statistical_analyses.satisfaction_whole_chart.overallSatisfactionData;
    SCISSatisfactionContributionStruct.value = model.statistical_analyses.satisfaction_whole_chart.SatisfactionContributionData
  } catch (error) {
    console.error('数据加载失败:', error)
  } finally {
    loading.value = false
  }
})
/* --------------- 分页 --------------- */
const PAGE_SIZE = 8                    // 每页按钮数
const currentPage = ref(0)              // 当前页码

const pageChunks = computed<ChartName[][]>(() => {
  const pages: ChartName[][] = []
  for (let i = 0; i < ChartName.length; i += PAGE_SIZE) {
    pages.push(ChartName.slice(i, i + PAGE_SIZE))
  }
  return pages
})
const currentButtons = computed<ChartName[]>(() => pageChunks.value[currentPage.value] ?? [])

function prevPage() {
  if (currentPage.value > 0) currentPage.value--
}
function nextPage() {
  if (currentPage.value < pageChunks.value.length - 1) currentPage.value++
}

const canPrev = computed(() => currentPage.value > 0)
const canNext = computed(() => currentPage.value < pageChunks.value.length - 1)
</script>

<style scoped>
.dashboard-layout {
  font-family: 'Inter', sans-serif;
}
</style>