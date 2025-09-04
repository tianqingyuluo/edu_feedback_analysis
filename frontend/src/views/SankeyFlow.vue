<script setup lang="ts">
import { onMounted,ref } from 'vue'
import * as echarts from 'echarts'
import sankeyData from './temp1.json'

let chart: echarts.ECharts
const chartRef = ref<HTMLDivElement>()

onMounted(() => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)

  const nodes = sankeyData.nodes.map((d: any) => ({ name: d.name }))
  const links = sankeyData.links.map((d: any) => ({
    source: d.source,
    target: d.target,
    value: Math.abs(d.value) // 桑基图不接受负值
  }))

  chart.setOption({
    title: { text: '学生满意度流向图', left: 'center' },
    tooltip: { trigger: 'item', triggerOn: 'mousemove' },
    series: [
      {
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        data: nodes,
        links: links,
        orient: 'horizontal',
        label: { position: 'right' },
        lineStyle: { color: 'gradient', curveness: 0.5 }
      }
    ]
  })
})
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <h1 class="text-2xl font-bold mb-4 text-center">满意度流向桑基图</h1>
    <div class="bg-white rounded-lg shadow-sm p-6">
      <div ref="chartRef" class="w-full h-[600px]"></div>
    </div>
  </div>
</template>