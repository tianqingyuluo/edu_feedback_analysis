<script setup>
import {ref, onMounted, onBeforeUnmount} from "vue";
import * as echarts from "echarts";
import {twoDimensionalData} from '@/types/IPDValues.js'
// 后端返回的 JSON 数据（可替换为接口获取）
const scatterData =twoDimensionalData


const chartRef = ref(null);
let chartInstance = null;

const initChart = () => {
  chartInstance = echarts.init(chartRef.value);
  
  // 按 student_persona 分组
  const groups = {};
  scatterData.pca_scatter.forEach((item) => {
    if (!groups[item.student_persona]) groups[item.student_persona] = [];
    groups[item.student_persona].push([item.pc1, item.pc2]);
  });
  
  const series = Object.keys(groups).map((key) => ({
    name: key,
    type: "scatter",
    data: groups[key],
    emphasis: {
      focus: 'series'
    }
  }));
  
  const option = {
    title: {text: "PCA降维前两维聚类散点图"},
    tooltip: {
      trigger: 'item',
      formatter: (params) => `${params.seriesName}<br/>PC1: ${params.value[0]}<br/>PC2: ${params.value[1]}`
    },
    legend: {data: Object.keys(groups)},
    xAxis: {name: "主成分1", type: "value"},
    yAxis: {name: "主成分2", type: "value"},
    series: series
  };
  
  chartInstance.setOption(option);
};

onMounted(() => {
  initChart();
  window.addEventListener("resize", () => {
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
  height: 500px;
}
</style>
