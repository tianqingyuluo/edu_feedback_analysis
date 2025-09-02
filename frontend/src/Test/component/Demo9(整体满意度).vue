<script setup>
import { ref, onMounted } from "vue";
import * as echarts from "echarts";

const chartRef = ref(null);

// 新 JSON 数据
const data = {
  labels: [
    "学习情况",
    "思政课",
    "专业课",
    "体育教育",
    "美育教育",
    "劳动教育",
    "校园生活",
    "实习",
    "自我提升",
    "老师教育",
    "学校服务",
    "学校基础条件"
  ],
  series: [
    {
      name: "一般",
      data: [0.465, 0.771, 0.755, 0.8, 0.797, 0.798, 0.578, 0.742, 0.757, 0.775, 0.759, 0.741]
    },
    {
      name: "满意",
      data: [0.579, 0.986, 0.951, 0.991, 0.987, 0.989, 0.686, 0.966, 0.973, 0.988, 0.978, 0.959]
    },
    {
      name: "较不满意",
      data: [0.361, 0.758, 0.737, 0.795, 0.767, 0.777, 0.286, 0.715, 0.738, 0.776, 0.744, 0.717]
    },
    {
      name: "不满意",
      data: [0.333, 0.626, 0.64, 0.63, 0.542, 0.563, 0.277, 0.548, 0.627, 0.685, 0.608, 0.553]
    },
    {
      name: "较满意",
      data: [0.469, 0.91, 0.859, 0.911, 0.893, 0.896, 0.505, 0.806, 0.843, 0.909, 0.865, 0.829]
    }
  ]
};

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
