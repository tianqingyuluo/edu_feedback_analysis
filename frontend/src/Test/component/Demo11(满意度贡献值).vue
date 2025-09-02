<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";

// 提供的 JSON 数据
const jsonData = {
  "labels": [
    "校园生活_均值",
    "学校服务_均值",
    "学习情况_均值",
    "自我提升_均值",
    "实习_均值",
    "专业课_均值",
    "思政课_均值",
    "劳动教育_均值",
    "老师教育_均值",
    "美育教育_均值"
  ],
  "values": [
    0.1786,
    0.1245,
    0.1132,
    0.0992,
    0.0857,
    0.0661,
    0.0631,
    0.0614,
    0.0587,
    0.0566
  ]
};

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
