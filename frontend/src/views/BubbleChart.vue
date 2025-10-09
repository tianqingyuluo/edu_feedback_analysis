<script setup lang="ts">
import { ref, watch, onMounted, nextTick, inject } from 'vue'
import * as echarts from 'echarts'
import { DropdownMenu, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import BubbleMetricDropdown from '@/components/layout/BubbleMetricDropdown.vue'
import type { Metric, MetricGroup } from '@/types/Metric.ts'
import CommentFollowUp from "@/components/layout/CommentFollowUp.vue";
import type {Comments} from "@/types/analysis.ts";

const metricGroups = inject<MetricGroup[]>('bubbleData', [])
const selectedMetrics = ref<Metric[]>([])
const comments = inject<Comments>('comments')
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// ---------- 图表更新 ----------
const updateChart = () => {
  if (!chartInstance) return

  // 颜色池。如果专业数量很多，可能需要更复杂的颜色生成策略，
  // 或者使用 ECharts 默认的颜色循环（不指定 itemStyle.color）
  const COLOR_PALETTE = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc',
    '#ff7f50', '#87cefa', '#da70d6', '#32cd32', '#6495ed',
    '#ff69b4', '#ba55d3', '#cd5c5c', '#ffa500', '#40e0d0'
  ]; // 可以扩展这个颜色数组

  // 为每个选定的专业创建一个单独的 series，并分配一个独有颜色
  const series = selectedMetrics.value.map((metric, index) => {
    // 为每个专业分配一个颜色，通过索引从颜色池中循环获取
    const color = COLOR_PALETTE[index % COLOR_PALETTE.length];

    return {
      name: metric.name, // 将 series.name 设置为专业名称，用于图例
      type: 'scatter',
      data: [{
        value: [metric.data[0], metric.data[1], metric.data[2]], // x, y, size_value
        name: metric.name // 这里的 name 主要用于 tooltip
      }],
      symbolSize: (val: [number, number, number]) =>
          Math.min(30, Math.max(6, Math.sqrt(val[2]) * 1.8)),
      itemStyle: { color: color }, // 应用这个专业独有的颜色
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } }
    }
  }).filter(s => s.data.length > 0); // 过滤掉没有数据的 series

  const option: echarts.EChartsOption = {
    title: {
      text: selectedMetrics.value.length ? '课堂参与度 vs 教学满意度' : '请选择专业',
      left: 'center'
    },
    tooltip: {
      formatter: (params: any) => {
        const [x, y, size] = params.data.value;
        return `专业：${params.seriesName}<br/>课堂参与：${x}<br/>教学满意度：${y}<br/>人数：${size}`
      }
    },
    legend: {
      type: 'scroll',
      top: 'bottom',
      left: 'center',
      padding: [10, 0, 0, 0],
      itemGap: 10,
      textStyle: {
        fontSize: 12
      }
    },
    xAxis: { name: '学生的课堂参与度', type: 'value' },
    yAxis: { name: '学生对教师教学投入满意度', type: 'value' },
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
    <CommentFollowUp
        :comment="comments.teacher_student_interaction_bubble_chart"
        :chart="metricGroups"
    />
  </div>
</template>