<script setup lang="ts">
import {inject, onMounted, type Ref, ref} from 'vue'
import * as echarts from 'echarts'
import type { GraphData} from '@/types/sankey'
import CommentFollowUp from "@/components/layout/CommentFollowUp.vue";
import type {Comments} from "@/types/analysis.ts";

const sankeyData =inject<Ref<GraphData>>('sankeyData')
let chart: echarts.ECharts
const chartRef = ref<HTMLDivElement>()
const comments = inject<Comments>('comments')
onMounted(() => {
  if (!chartRef.value) return
  if (!sankeyData) {
    console.warn('桑基图数据为空')
    return
  }
  console.log(sankeyData)
  chart = echarts.init(chartRef.value)

  const nodes = sankeyData.value.nodes.map((d: any) => ({ name: d.name }))
  const links = sankeyData.value.links.map((d: any) => ({
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
  <div class="p-6 bg-gray-50 min-h-[80%]">
    <h1 class="text-2xl font-bold mb-4 text-center">满意度流向桑基图</h1>
    <div class="bg-white rounded-lg shadow-sm p-6">
      <div ref="chartRef" class="w-full h-[600px]"></div>
    </div>
  </div>
  <CommentFollowUp
      :comment="comments.student_satisfaction_route_sankey_chart"
      :chart="sankeyData"
  />
</template>