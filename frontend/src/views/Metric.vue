<script setup lang="ts">
import { ref, onMounted, watch, nextTick,inject } from 'vue'
import * as echarts from 'echarts'
import MetricDropdown from '@/components/layout/MetricDropdown.vue'
import { Button } from '@/components/ui/button'
import { type Metric } from '@/types/Metric.ts'
import {DropdownMenu} from "@/components/ui/dropdown-menu";

const metricGroups = inject<Metric[]>('trendData', [])  // 统一数据源
const selectedMetrics = ref<Metric[]>([])

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const colorPalette = [
  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'
]

const updateChart = () => {
  if (!chartInstance) return
  const series = selectedMetrics.value.map((metric, index) => ({
    name: metric.name,
    type: 'line',
    data: metric.data,
    lineStyle: { width: 3 },
    itemStyle: { color: colorPalette[index % colorPalette.length] }
  }))
  const xAxisData = Array.from(
      { length: Math.max(...selectedMetrics.value.map(m => m.data.length), 0) },
      (_, i) => `点${i + 1}`
  )
  const option = {
    title: { text: selectedMetrics.value.length ? '指标趋势图' : '请选择指标', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { data: selectedMetrics.value.map(m => m.name), top: '5%' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: '数值' },
    series
  }
  chartInstance.setOption(option, { notMerge: true })
}

watch(selectedMetrics, () => nextTick(updateChart), { deep: true })

onMounted(() => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  window.addEventListener('resize', () => chartInstance?.resize())
  updateChart()
})
</script>

<template>
  <div class="p-4 bg-gray-50 h-full flex flex-col gap-4">
    <!-- 控制条：一行白底 -->
    <!-- MetricFilterBar.vue -->
    <div class="bg-white rounded-md shadow-sm p-2 inline-flex items-center gap-2">
      <!-- 触发器直接包选择器 + 按钮 -->
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <div class="inline-flex items-center gap-2">
            <MetricDropdown
                v-model="selectedMetrics"
                :metric-groups="metricGroups"
                placeholder="选择指标"
                class="w-52"
            />
            <Button variant="outline" size="sm" @click.stop="selectedMetrics = []">
              清空
            </Button>
            <Button size="sm" @click.stop="updateChart">
              刷新
            </Button>
          </div>
        </DropdownMenuTrigger>
        <!-- 下拉内容 ... -->
      </DropdownMenu>
    </div>

    <!-- 图表区域 -->
    <div class="bg-white rounded-md shadow p-3 flex-1">
      <div ref="chartRef" class="w-full h-full"></div>
    </div>
  </div>
</template>