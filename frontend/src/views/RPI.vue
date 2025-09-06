<!-- pages/ResourceHeatmapPage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import FiltersBar from '@/components/layout/RPIGradeFilter.vue'
import HealthGauge from '@/components/layout/HealthGauge.vue'
import RadarChart from '@/components/layout/RadarChart.vue'
import ResourceHeatmap from '@/components/layout/ResourceHeatmap.vue'
import type { Major } from '@/types/majorModels.ts'
import RPIGradeFilter from "@/components/layout/RPIGradeFilter.vue";

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
  <div class="dashboard-layout p-6 bg-gray-100 min-h-screen">
    <h1 class="text-3xl font-bold text-gray-800 mb-6">
      学生资源感知度仪表盘
    </h1>

    <RPIGradeFilter
        v-model:selectedMajors="selectedMajors"
        v-model:selectedGrade="selectedGrade"
        @apply-filters="calculateEHI"
        class="sticky top-0 z-10 bg-white/90 backdrop-blur px-6 py-4 shadow-sm mb-6"
    />

    <!-- 2. 仪表盘 | 雷达图 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-1">
        <HealthGauge
            :ehi-value="ehiValue"
            MetricName="RPI"
            title="综合资源感知度 (RPI)"
        />
      </div>
      <div class="md:col-span-2">
        <RadarChart
            :selected-majors-for-radar="selectedMajors"
            :selected-grades-for-radar="selectedGrade"
            :indicators="radarIndicators"
            title="综合资源感知度 (RPI)"
        />
      </div>
    </div>

    <!-- 3. 热力图 -->
    <div class="mt-6 bg-white rounded-lg shadow p-4">
      <ResourceHeatmap
          :selected-majors="selectedMajors"
          :selected-grade="selectedGrade"
          class="w-full min-h-[800px]"
      />
    </div>
  </div>
</template>