<script setup lang="ts">
import { ref, watch, onMounted, nextTick,inject } from 'vue'
import * as echarts from 'echarts'
import { DropdownMenu, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import BubbleMetricDropdown from '@/components/layout/BubbleMetricDropdown.vue'
import type { Metric, MetricGroup } from '@/types/Metric.ts'

const metricGroups = inject<MetricGroup[]>('bubbleData', [])
const selectedMetrics = ref<Metric[]>([])

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

/* ---------- 图表更新 ---------- */
const updateChart = () => {
  if (!chartInstance) return

  /* 学院级固定色 + 平方根缩放 */
  const GROUP_COLORS = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'
  ]

  const groupMap = new Map<string, Metric[]>()
  selectedMetrics.value.forEach(m => {
    const academy = metricGroups.value.find(g => g.metrics.some(orig => orig.name === m.name))
    if (!academy) return
    if (!groupMap.has(academy.name)) groupMap.set(academy.name, [])
    groupMap.get(academy.name)!.push(m)
  })

  const series = Array.from(groupMap.entries()).map(([name, majors], idx) => ({
    name,
    type: 'scatter',
    data: majors.map(m => ({ value: m.data, name: m.name })),
    symbolSize: (val: [number, number, number]) =>
        Math.min(30, Math.max(6, Math.sqrt(val[2]) * 1.8)),
    itemStyle: { color: GROUP_COLORS[idx % GROUP_COLORS.length] },
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } }
  }))

  const option: echarts.EChartsOption = {
    title: {
      text: series.length ? '课堂参与度 vs 教学满意度' : '请选择专业',
      left: 'center'
    },
    tooltip: {
      formatter: (params: any) => {
        const [x, y, size] = params.value
        return `${params.seriesName}<br/>专业：${params.name}<br/>课堂参与：${x}<br/>教学满意度：${y}<br/>人数：${size}`
      }
    },
    xAxis: { name: '课堂参与度', type: 'value' },
    yAxis: { name: '教学投入满意度', type: 'value' },
    series
  }

  chartInstance.setOption(option, { notMerge: true })
}

/* ---------- 生命周期 ---------- */
onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  }
})

watch(selectedMetrics, () => nextTick(updateChart), { deep: true })
</script>

<template>
  <div class="p-4 bg-gray-50 h-full flex flex-col gap-4">
    <!-- 控制条 -->
    <div class="bg-white rounded-md shadow-sm p-2 inline-flex items-center gap-2">
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <div class="inline-flex items-center gap-2">
            <BubbleMetricDropdown
                v-model="selectedMetrics"
                :metric-groups="metricGroups"
                placeholder="选择学院"
                class="w-64"
            />
            <Button variant="outline" size="sm" @click.stop="selectedMetrics = []">清空</Button>
          </div>
        </DropdownMenuTrigger>
      </DropdownMenu>
    </div>

    <!-- 图表 -->
    <div class="bg-white rounded-md shadow p-3 flex-1 min-h-[500px]">
      <div ref="chartRef" class="w-full h-full min-h-[500px]" />
    </div>
  </div>
</template>