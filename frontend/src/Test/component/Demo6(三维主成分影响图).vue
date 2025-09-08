<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";
import "echarts-gl";  // 引入 ECharts 3D 支持;
import {threeDimensionalData} from '@/types/IPDValues.js'


// 后端返回的 JSON 数据（可替换成接口获取）
const scatter3DData=threeDimensionalData;

const chartRef = ref(null);
let chartInstance = null;

const initChart = () => {
  chartInstance = echarts.init(chartRef.value);
  
  // 按 student_persona 分组
  const groups = {};
  scatter3DData.pca_3d_scatter.forEach((item) => {
    if (!groups[item.student_persona]) groups[item.student_persona] = [];
    groups[item.student_persona].push([item.pc1, item.pc2, item.pc3]);
  });
  
  const series = Object.keys(groups).map((key) => ({
    name: key,
    type: 'scatter3D',
    data: groups[key],
    symbolSize: 10,
    emphasis: { focus: 'series' }
  }));
  
  const option = {
    title: { text: "PCA前三主成分三维聚类散点图" },
    tooltip: {
      formatter: (params) =>
          `${params.seriesName}<br/>PC1: ${params.value[0]}<br/>PC2: ${params.value[1]}<br/>PC3: ${params.value[2]}`
    },
    legend: { data: Object.keys(groups), top: 30 },
    xAxis3D: { name: '主成分1' },
    yAxis3D: { name: '主成分2' },
    zAxis3D: { name: '主成分3' },
    grid3D: {
      boxWidth: 200,
      boxDepth: 200,
      boxHeight: 200,
      viewControl: { autoRotate: false }
    },
    series: series
  };
  
  chartInstance.setOption(option);
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', () => {
    chartInstance && chartInstance.resize();
  });
});

onBeforeUnmount(() => {
  chartInstance && chartInstance.dispose();
});
</script>

<template>
<div ref="chartRef" class="chart"></div>
</template>

<style scoped>
.chart {
  width: 100%;
  height: 600px;
}
</style>
