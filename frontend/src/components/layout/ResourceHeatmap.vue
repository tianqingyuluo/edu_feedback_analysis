<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { Major } from '@/types/majorModels.ts'

const props = defineProps<{
  selectedMajors: Major[]
  selectedGrade: string[]
}>()
const heatmapRef = ref<HTMLElement | null>(null)
let heatmapInstance: echarts.ECharts | null = null

const resourceColumns = [
  '教室设备满意度', '实训室满意度', '图书馆满意度',
  '网络资源满意度', '体育设施满意度', '住宿条件满意度'
]

const chartData = computed(() => {
  const data: any[] = []
  props.selectedMajors.forEach((major, majorIndex) => {
    // 🔥 只取当前选中的年级
    const grades = props.selectedGrade.length
        ? props.selectedGrade.map(g => major.grades.find(gr => gr.name === g)).filter(Boolean)
        : major.grades

    const cnt = grades.length
    if (!cnt) return

    const sums = Array(resourceColumns.length).fill(0)
    grades.forEach(g => {
      resourceColumns.forEach((_, i) => {
        if (g && g.data.length > i) sums[i] += g.data[i]
      })
    })
    sums.forEach((sum, resIndex) => {
      data.push([resIndex, majorIndex, (sum / cnt).toFixed(2)])
    })
  })
  return data
})

const updateChart = () => {
  console.log('🔥 updateChart 被触发', props.selectedMajors.length)
  if (!heatmapRef.value) return
  if (!heatmapInstance) {
    heatmapInstance = echarts.init(heatmapRef.value)
  }
  const option = {
    title: { text: '资源满意度热力图', left: 'center' },
    tooltip: {
      position: 'top',
      formatter: (p: any) =>
          `${props.selectedMajors[p.data[1]]?.name} - ${resourceColumns[p.data[0]]}: ${p.data[2]}`
    },
    grid: { height: '60%', top: '15%' },
    xAxis: { type: 'category', data: resourceColumns, splitArea: { show: true } },
    yAxis: { type: 'category', data: props.selectedMajors.map(m => m.name), splitArea: { show: true } },
    visualMap: { min: 60, max: 100, calculable: true, orient: 'horizontal', left: 'center', bottom: '5%',
      inRange: { color: ['#d73027', '#fee08b', '#1a9641'] } },
    series: [{
      name: '满意度',
      type: 'heatmap',
      data: chartData.value,
      label: { show: true },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,.5)' } }
    }]
  }
  heatmapInstance.setOption(option, { notMerge: true })
}

onMounted(() => {
  nextTick(updateChart)
})

watch(
    [() => props.selectedMajors, () => props.selectedGrade],
    () => {
      console.log('🔥 watch 触发，重新计算热力图')
      nextTick(updateChart)
    },
    { deep: true }
)

onUnmounted(() => {
  heatmapInstance?.dispose()
})
</script>

<template>
  <div ref="heatmapRef" class="w-full h-[500px]" />
</template>