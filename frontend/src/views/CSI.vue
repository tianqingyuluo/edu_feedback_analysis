<script setup>
import {ref, onMounted, onBeforeUnmount, inject} from "vue";
import * as echarts from "echarts";
import CommentFollowUp from "@/components/layout/CommentFollowUp.vue";



const SCIOSatisfactionDistributionStruct = inject("SCIOSatisfactionDistributionStruct");
const SCISOverallSatisfactionStruct = inject("SCISOverallSatisfactionStruct");
const SCISSatisfactionContributionStruct = inject("SCISSatisfactionContributionStruct");
const comments = inject('comments')
// ========== 1. 满意度分布 ==========
const distRef = ref(null);
let distChart = null;
const initDistChart = () => {
  distChart = echarts.init(distRef.value);
  
  // 颜色映射
  const colorMap = {
    "满意": "#4CAF50",
    "较满意": "#74c0de",
    "一般": "#5571c6",
    "较不满意": "#fac859",
    "不满意": "#ee6767"
  };
  
  distChart.setOption({
    title: { text: "满意度分布", left: "center" },
    tooltip: {
      trigger: "axis",
      formatter: (params) => {
        const p = params[0];
        return `${p.axisValue}<br/>人数: ${p.data}`;
      }
    },
    xAxis: {
      type: "category",
      data: SCIOSatisfactionDistributionStruct.value.labels,
      axisTick: { alignWithLabel: true }
    },
    yAxis: { type: "value", name: "人数" },
    series: [
      {
        name: "人数",
        type: "bar",
        data: SCIOSatisfactionDistributionStruct.value.values,
        barWidth: "50%",
        itemStyle: {
          color: (params) => colorMap[params.name] || "#999" // 默认灰色
        }
      }
    ]
  });
};


// ========== 2. 各群体在维度的平均满意度对比 ==========
const overallRef = ref(null);
let overallChart = null;
const initOverallChart = () => {
  overallChart = echarts.init(overallRef.value);
  const data = SCISOverallSatisfactionStruct.value;
  
  const leftLabels = data.labels.slice(0, 6);
  const rightLabels = data.labels.slice(6);
  
  function makeSeries(gridIndex) {
    return data.series.map((item) => ({
      name: item.name,
      type: "bar",
      xAxisIndex: gridIndex,
      yAxisIndex: gridIndex,
      data: item.data.slice(gridIndex * 6, gridIndex * 6 + 6),
      emphasis: { focus: "series" }
    }));
  }
  
  overallChart.setOption({
    title: { text: "不同群体在各维度的平均满意度对比", left: "center" },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: {
      top: 30,
      data: ["满意", "较满意", "一般", "较不满意", "不满意"] // 固定顺序
    },
    grid: [
      { left: "5%", right: "55%", bottom: "10%", top: "20%", containLabel: true },
      { left: "55%", right: "5%", bottom: "10%", top: "20%", containLabel: true }
    ],
    xAxis: [
      { type: "category", data: leftLabels, gridIndex: 0, axisLabel: { rotate: 30 } },
      { type: "category", data: rightLabels, gridIndex: 1, axisLabel: { rotate: 30 } }
    ],
    yAxis: [
      { type: "value", gridIndex: 0, min: 0, max: 1 },
      { type: "value", gridIndex: 1, min: 0, max: 1 }
    ],
    series: [...makeSeries(0), ...makeSeries(1)]
  });
  
};

// ========== 3. 区分群体最重要的满意度维度 ==========
const contribRef = ref(null);
let contribChart = null;
const initContribChart = () => {
  contribChart = echarts.init(contribRef.value);
  contribChart.setOption({
    title: { text: "区分群体最重要的满意度维度", left: "center" },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (params) => `${params[0].name}: ${params[0].value}`
    },
    grid: { left: "20%", right: "5%", top: "15%", bottom: "10%" },
    xAxis: { type: "value", name: "重要性", min: 0 },
    yAxis: {
      type: "category",
      data: SCISSatisfactionContributionStruct.value.labels,
      inverse: true
    },
    series: [
      {
        type: "bar",
        data: SCISSatisfactionContributionStruct.value.values,
        itemStyle: { color: "#398cff" },
        barCategoryGap: "40%"
      }
    ]
  });
};

// ========== 生命周期 ==========
onMounted(() => {
  initDistChart();
  initOverallChart();
  initContribChart();
  window.addEventListener("resize", () => {
    distChart && distChart.resize();
    overallChart && overallChart.resize();
    contribChart && contribChart.resize();
  });
});

onBeforeUnmount(() => {
  distChart && distChart.dispose();
  overallChart && overallChart.dispose();
  contribChart && contribChart.dispose();
});
</script>

<template>
<h1 class="text-3xl font-bold text-gray-800 mb-6">学生对学校整体的满意度</h1>
<div class="charts">
  <!-- 满意度分布 -->
  <div ref="distRef" class="chart h-[500px]"></div>
  
  <!-- 平均满意度对比 -->
  <div ref="overallRef" class="chart h-[600px]"></div>
  
  <!-- 区分群体最重要的维度 -->
  <div ref="contribRef" class="chart h-[500px]"></div>
  <CommentFollowUp
      :comment="comments.satisfaction_whole_chart"
      :chart="SCIOSatisfactionDistributionStruct"
  />
</div>
</template>

<style scoped>
.charts {
  display: flex;
  flex-direction: column;
  gap: 40px;
}
.chart {
  width: 100%;
}
</style>
