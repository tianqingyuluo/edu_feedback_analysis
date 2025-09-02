<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";

// ==============================
// 后端返回的 JSON 数据（直接替换成接口返回即可）
// ==============================
const satisfactionData = {
  "学习情况": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [0,158,1659,7277,4732] },
  "思政课": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [5344,6997,1038,406,41] },
  "专业课": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [3639,7327,2511,331,18] },
  "体育教育": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [4834,7905,922,0,165] },
  "美育教育": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [4462,7685,1395,0,284] },
  "劳动教育": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [4492,7865,1272,0,197] },
  "校园生活": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [564,1734,3239,3724,4565] },
  "实习": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [2986,8547,1123,1039,131] },
  "自我提升": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [3248,8267,1863,425,23] },
  "老师教育": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [4932,7639,1031,213,11] },
  "学校服务": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [3732,7937,1658,455,44] },
  "学校基础条件": { "labels": ["满意","较满意","一般","较不满意","不满意"], "values": [3064,7296,2433,856,177] }
};

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
