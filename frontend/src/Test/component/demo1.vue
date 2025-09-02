<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'

// 容器 ref
const chartRef = ref(null)
let chartInstance = null

// ECharts 配置
const option = {
  title: {
    text: 'PCA 主成分方差贡献率'
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['单个主成分方差贡献率', '累计方差贡献率']
  },
  xAxis: {
    type: 'category',
    name: '主成分序号',
    data: ['1', '2', '3', '4', '5', '6', '7']
  },
  yAxis: {
    type: 'value',
    name: '方差解释比例'
  },
  series: [
    {
      name: '单个主成分方差贡献率',
      type: 'bar',
      data: [0.303, 0.197, 0.133, 0.063, 0.051, 0.051, 0.043],
      barGap: '0%'
    },
    {
      name: '累计方差贡献率',
      type: 'line',
      data: [0.303, 0.500, 0.633, 0.696, 0.747, 0.798, 0.841],
      smooth: false
    }
  ]
}

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(option)
  
  // 自适应窗口大小
  window.addEventListener('resize', () => {
    chartInstance.resize()
  })
})
</script>

<template>
<div ref="chartRef" style="width: 100%; height: 500px;"></div>
</template>
