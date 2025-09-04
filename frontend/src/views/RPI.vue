<!-- pages/ResourceHeatmapPage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import FiltersBar from '@/components/layout/gradeFilter.vue'
import HealthGauge from '@/components/layout/HealthGauge.vue'
import RadarChart from '@/components/layout/RadarChart.vue'
import ResourceHeatmap from '@/components/layout/ResourceHeatmap.vue'
import type { Major } from '@/types/majorModels.ts'

const selectedMajors = ref<Major[]>([])
const selectedGrade = ref<string[]>([])

// 仪表盘值（RPI）
const ehiValue = ref(0)

// 雷达图维度
const radarIndicators = [
  { name: '教室设备满意度', max: 100, min: 0 },
  { name: '实训室满意度', max: 100, min: 0 },
  { name: '图书馆满意度', max: 100, min: 0 },
  { name: '网络资源满意度', max: 100, min: 0 },
  { name: '体育设施满意度', max: 100, min: 0 },
  { name: '住宿条件满意度', max: 100, min: 0 }
]

// 第 7 位数据索引 = 6
const RPI_INDEX = 6

// 计算仪表盘值（RPI）
const calculateEHI = () => {
  if (selectedMajors.value.length === 0) {
    ehiValue.value = 0
    return
  }

  let total = 0
  let count = 0

  selectedMajors.value.forEach(major => {
    const grades = selectedGrade.value.length
        ? selectedGrade.value.map(g => major.grades.find(gr => gr.name === g)).filter(Boolean)
        : major.grades

    grades.forEach(grade => {
      if (grade && grade.data.length > RPI_INDEX) {
        total += grade.data[RPI_INDEX]
        count++
      }
    })
  })

  ehiValue.value = count > 0 ? Math.round(total / count) : 0
}

// 初始计算
onMounted(() => calculateEHI())
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <h1 class="text-2xl font-bold mb-4">资源满意度分析页面</h1>

    <!-- 筛选栏 -->
    <div class="sticky top-0 z-50 bg-white shadow-lg rounded-b-lg">
      <FiltersBar
          v-model:selectedMajors="selectedMajors"
          v-model:selectedGrade="selectedGrade"
          @apply-filters="calculateEHI"
      />
    </div>

    <!-- 第一行：仪表盘 | 雷达图 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <!-- 左侧仪表盘 -->
      <div>
        <HealthGauge :ehi-value="ehiValue" title="资源满意度总览" MetricName="RPI" />
      </div>

      <!-- 右侧雷达图 -->
      <div>
        <RadarChart
            :selected-majors-for-radar="selectedMajors"
            :selected-grades-for-radar="selectedGrade"
            title="资源维度雷达图"
            :indicators="radarIndicators"
        />
      </div>
    </div>

    <!-- 第二行：热力图独占整宽并自适应高度 -->
    <div class="mt-6">
      <ResourceHeatmap
          :selected-majors="selectedMajors"
          :selected-grade="selectedGrade"
          class="w-full h-auto min-h-[500px] lg:min-h-[600px]"
      />
    </div>
  </div>
</template>