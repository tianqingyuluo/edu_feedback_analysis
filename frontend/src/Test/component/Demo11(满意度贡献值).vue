<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";
import {SatisfactionContributionData} from "@/types/CSIValues.ts"
// 提供的 JSON 数据
const jsonData = SatisfactionContributionData

const chartRef = ref(null);
let chartInstance = null;

onMounted(() => {
  chartInstance = echarts.init(chartRef.value);
  
  const option = {
    title: {
      text: "区分群体最重要的满意度维度",
      left: "center"
    },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (params) => `${params[0].name}: ${params[0].value}`
    },
    grid: { left: "20%", right: "5%", top: "15%", bottom: "10%" },
    xAxis: {
      type: "value",
      name: "重要性",
      min: 0
    },
    yAxis: {
      type: "category",
      data: jsonData.labels,
      inverse: true,  // 横向柱状图从上到下排列
      axisLabel: { interval: 0, rotate: 0 }
    },
    series: [
      {
        type: "bar",
        data: jsonData.values,
        itemStyle: {
          color: "#398cff"
        },
        barCategoryGap: "40%"
      }
    ]
  };
  
  chartInstance.setOption(option);
  
  window.addEventListener("resize", () => {
    chartInstance && chartInstance.resize();
  });
});

onBeforeUnmount(() => {
  chartInstance && chartInstance.dispose();
});
</script>

<template>
<div class="w-full h-[500px]">
  <div ref="chartRef" class="w-full h-full"></div>
</div>
</template>

<style scoped>
</style>
