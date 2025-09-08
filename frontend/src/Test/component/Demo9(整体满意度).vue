<script setup>
import { ref, onMounted } from "vue";
import * as echarts from "echarts";
import {overallSatisfactionData} from "@/types/CSIValues.ts"

const chartRef = ref(null);

// 新 JSON 数据
const data = overallSatisfactionData

// 分两列
const leftLabels = data.labels.slice(0, 6);
const rightLabels = data.labels.slice(6);

function makeSeries(labels, gridIndex) {
  return data.series.map(item => ({
    name: item.name,
    type: "bar",
    xAxisIndex: gridIndex,
    yAxisIndex: gridIndex,
    data: item.data.slice(gridIndex * 6, gridIndex * 6 + 6),
    emphasis: {focus: "series"}
  }));
}

onMounted(() => {
  const chart = echarts.init(chartRef.value);
  
  const option = {
    title: {text: "不同群体在各维度的平均满意度对比", left: "center"},
    tooltip: {trigger: "axis", axisPointer: {type: "shadow"}},
    legend: {top: 30},
    grid: [
      {left: "5%", right: "55%", bottom: "10%", top: "20%", containLabel: true},
      {left: "55%", right: "5%", bottom: "10%", top: "20%", containLabel: true}
    ],
    xAxis: [
      {type: "category", data: leftLabels, gridIndex: 0, axisLabel: {rotate: 30}},
      {type: "category", data: rightLabels, gridIndex: 1, axisLabel: {rotate: 30}}
    ],
    yAxis: [
      {type: "value", gridIndex: 0, min: 0, max: 1},
      {type: "value", gridIndex: 1, min: 0, max: 1}
    ],
    series: [
      ...makeSeries(leftLabels, 0),
      ...makeSeries(rightLabels, 1)
    ]
  };
  
  chart.setOption(option);
  window.addEventListener("resize", () => chart.resize());
});
</script>

<template>
<div ref="chartRef" class="w-full h-[600px]"></div>
</template>

<style scoped>
.w-full {
  width: 100%;
}

.h-\[600px\] {
  height: 600px;
}
</style>
