<script setup lang="ts">
import { ref, inject, watchEffect, computed } from 'vue'
import * as echarts from 'echarts'
import { Button } from '@/components/ui/button'
import type { Academy, Major } from '@/types/majorModels'
import SingleSelectMenu from '@/components/layout/SingleSelectMenu.vue'

/* ---------- 年级 ---------- */
const gradeOptions = ['大一', '大二', '大三', '大四']
const selectedGrade = ref<string>('大一')
const academies = inject<Academy[]>('timeAcademies', [])

/* ---------- 专业单选 ---------- */
const selectedMajor = ref<Major | null>(null)

/* ---------- 计算当前选中年级的数据 ---------- */
const currentGradeData = computed(() => {
  if (!selectedMajor.value) return []

  // 找到当前选中年级的数据
  const gradeData = selectedMajor.value.grades.find(g => g.name === selectedGrade.value)
  return gradeData?.data || []
})

/* ---------- 清除 ---------- */
const clearAll = () => {
  selectedGrade.value = '大一'
  selectedMajor.value = null
}

/* ---------- 确认 ---------- */
const applyFilters = () => { /* watchEffect 已自动更新饼图 */ }

/* ---------- 饼图 ---------- */
let chart: echarts.ECharts
const chartRef = ref<HTMLDivElement>()
const labels = ['学习', '科研', '竞赛', '实践', '实习', '志愿', '社团', '其他']

watchEffect(() => {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  const data = currentGradeData.value
  chart.setOption({
    title: {
      text: selectedMajor.value?.name || '',
      left: 'center',
      subtext: selectedMajor.value ? `${selectedGrade.value}数据` : '',
      subtextStyle: { fontSize: 14 }
    },
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: labels.map((n, i) => ({ name: n, value: data[i] || 0 })),
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } }
      }
    ]
  })
})
</script>

<template>
  <!-- 最外层：统一边距 -->
  <div class="p-6 bg-gray-50 min-h-screen">
    <h1 class="text-2xl font-bold mb-4">时间分配分析</h1>

    <!-- 筛选栏白色卡片 -->
    <div class="bg-white rounded-lg shadow-sm p-4 mb-6">
      <div class="filter-bar-container flex flex-wrap items-end gap-4">
        <!-- 年级 -->
        <div class="filter-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">年级</label>
          <select
              v-model="selectedGrade"
              class="block w-[150px] pl-3 pr-8 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          >
            <option v-for="g in gradeOptions" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>

        <!-- 学院/专业 -->
        <div class="filter-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">学院 & 专业</label>
          <SingleSelectMenu
              v-model="selectedMajor"
              :academies="academies"
              placeholder="请选择专业"
              class="w-[250px]"
          />
        </div>

        <!-- 按钮 -->
        <div class="filter-actions flex flex-wrap gap-2 mt-auto">
          <Button variant="outline" size="sm" @click="clearAll">清空</Button>
          <Button size="sm" @click="applyFilters">确认</Button>
        </div>
      </div>
    </div>

    <!-- 饼图白色卡片 -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <div ref="chartRef" class="w-full h-[400px]"></div>
      <!-- 添加数据提示 -->
      <div v-if="selectedMajor && currentGradeData.length === 0" class="text-center text-gray-500 mt-4">
        该专业没有 {{ selectedGrade }} 的数据
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-group { min-width: 150px; }
</style>