<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";
import {satisfactionPartData} from '@/types/DPFEValues.js'

// ==============================
// 后端返回的 JSON 数据（直接替换成接口返回即可）
// ==============================
const satisfactionData =satisfactionPartData

const chartRef = ref(null);
let chartInstance = null;

const initChart = () => {
  chartInstance = echarts.init(chartRef.value);
  
  const categories = Object.keys(satisfactionData);
  const colors = ["#4CAF50", "#8BC34A", "#FFC107", "#FF9800", "#F44336"];
  
  const grid = [];
  const xAxis = [];
  const yAxis = [];
  const series = [];
  
  const rows = 4;
  const cols = 3;
  const cellWidth = 100 / cols;
  const cellHeight = 100 / rows;
  
  categories.forEach((cat, idx) => {
    const row = Math.floor(idx / cols);
    const col = idx % cols;
    
    grid.push({
      left: `${col * cellWidth + 5}%`,
      top: `${row * cellHeight + 5}%`,
      width: `${cellWidth - 8}%`,
      height: `${cellHeight - 10}%`
    });
    
    xAxis.push({
      type: "category",
      data: satisfactionData[cat].labels,
      gridIndex: idx,
      axisLabel: { fontSize: 10 }
    });
    
    yAxis.push({
      type: "value",
      gridIndex: idx,
      axisLabel: { fontSize: 10 }
    });
    
    series.push({
      type: "bar",
      xAxisIndex: idx,
      yAxisIndex: idx,
      data: satisfactionData[cat].values,
      itemStyle: { color: (params) => colors[params.dataIndex] },
      name: cat
    });
  });
  
  const option = {
    title: categories.map((cat, idx) => ({
      text: cat,
      left: grid[idx].left,
      top: `${parseFloat(grid[idx].top) - 4}%`,
      textStyle: { fontSize: 12 }
    })),
    tooltip: { trigger: "axis" },
    grid,
    xAxis,
    yAxis,
    series
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
  height: 900px; /* 给足高度容纳 12 个子图 */
}
</style>
