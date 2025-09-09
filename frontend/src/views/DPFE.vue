<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";

import {inject} from "vue";


const DPFESatisfactionPartData = inject('DPFESatisfactionPartData')
const DPFEHeatmapData = inject('DPFEHeatmapData')


// ========== 1. 多面板满意度分布 ==========
const partRef = ref(null);
let partChart = null;

const initPartChart = () => {
  partChart = echarts.init(partRef.value);
  
  const categories = Object.keys(DPFESatisfactionPartData.value);
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
      data: DPFESatisfactionPartData.value[cat].labels,
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
      data: DPFESatisfactionPartData.value[cat].values,
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
  
  partChart.setOption(option);
};

// ========== 2. 热力图 ==========
const heatmapRef = ref(null);
let heatmapChart = null;

const initHeatmapChart = () => {
  heatmapChart = echarts.init(heatmapRef.value);
  
  const data = [];
  const labels = DPFEHeatmapData.value.labels;
  
  DPFEHeatmapData.value.matrix.forEach((row, i) => {
    row.forEach((val, j) => {
      data.push([j, i, val.toFixed(2)]);
    });
  });
  
  const option = {
    tooltip: {
      position: "top",
      formatter: (params) => {
        return `<b>${labels[params.value[1]]}</b> vs <b>${labels[params.value[0]]}</b><br/>相关系数: <b>${params.value[2]}</b>`;
      }
    },
    grid: {
      left: "18%",
      top: "10%",
      right: "10%",
      bottom: "18%"
    },
    xAxis: {
      type: "category",
      data: labels,
      splitArea: {show: true},
      axisLabel: {rotate: 45, fontSize: 12}
    },
    yAxis: {
      type: "category",
      data: labels,
      splitArea: {show: true},
      axisLabel: {fontSize: 12}
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: "vertical",
      left: "left",
      top: "center",
      precision: 2,
      inRange: {
        color: ["#2166ac", "#f7f7f7", "#b2182b"]
      }
    },
    series: [
      {
        name: "相关性",
        type: "heatmap",
        data,
        label: {
          show: true,
          formatter: (p) => p.value[2],
          color: "#000",
          fontSize: 11
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: "rgba(0, 0, 0, 0.5)"
          }
        }
      }
    ]
  };
  
  heatmapChart.setOption(option);
};

// ========== 生命周期 ==========
onMounted(() => {
  initPartChart();
  initHeatmapChart();
  window.addEventListener("resize", () => {
    partChart && partChart.resize();
    heatmapChart && heatmapChart.resize();
  });
});

onBeforeUnmount(() => {
  partChart && partChart.dispose();
  heatmapChart && heatmapChart.dispose();
});
</script>

<template>

<div class="charts-container">
  <h1 class="text-3xl font-bold text-gray-800 mb-6">学生对不同方面的满意度分析</h1>
  <!-- 多面板满意度分布 -->
  <div ref="partRef" class="part-chart"></div>
  <h1 class="text-3xl font-bold text-gray-800 mb-6">不同面向的满意度关系</h1>
  
  <!-- 热力图 -->
  <div ref="heatmapRef" class="heatmap-chart"></div>
</div>
</template>

<style scoped>
.charts-container {
  display: flex;
  flex-direction: column;
  gap: 40px;
  width: 100%;
}

.part-chart {
  width: 100%;
  height: 900px; /* 适合 12 子图 */
}

.heatmap-chart {
  width: 100%;
  height: 800px;
}
</style>
