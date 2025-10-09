<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";
import "echarts-gl"; // 3D 支持
import {inject} from "vue";
import CommentFollowUp from "@/components/layout/CommentFollowUp.vue";
const comments = inject('comments')
const IPDStudentTypeData = inject('IPDStudentTypeData')
const IPDTwoDimensionalData = inject('IPDTwoDimensionalData')
const IPDThreeDimensionalData = inject('IPDThreeDimensionalData')

// ======== 1. 柱状图：人数分布 ========
const barRef = ref(null);
let barChart = null;
const initBarChart = () => {
  barChart = echarts.init(barRef.value);
  barChart.setOption({
    title: { text: "各画像人数分布" },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: IPDStudentTypeData.valueOf.labels },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: IPDStudentTypeData.value.values,
        itemStyle: { color: "#5470C6" },
      },
    ],
  });
};

// ======== 2. 二维 PCA 散点图 ========
const scatter2DRef = ref(null);
let scatter2DChart = null;
const initScatter2DChart = () => {
  scatter2DChart = echarts.init(scatter2DRef.value);
  
  // 按 student_persona 分组
  const groups = {};
  IPDTwoDimensionalData.value.pca_scatter.forEach((item) => {
    if (!groups[item.student_persona]) groups[item.student_persona] = [];
    groups[item.student_persona].push([item.pc1, item.pc2]);
  });
  
  const series = Object.keys(groups).map((key) => ({
    name: key,
    type: "scatter",
    data: groups[key],
    emphasis: {focus: "series"},
    progressive: 2000, // 启用渐进渲染，适合大数据
  }));
  
  scatter2DChart.setOption({
    title: {text: "学生画像影响因素"},
    tooltip: {
      trigger: "item",
      formatter: (params) =>
          `${params.seriesName}<br/>PC1: ${params.value[0]}<br/>PC2: ${params.value[1]}`,
    },
    legend: {data: Object.keys(groups)},
    xAxis: {name: "完成作业、自习课、外阅读、网络课程时间", type: "value"},
    yAxis: {name: "课前预学、课堂参与、课后复习、延伸阅读", type: "value"},
    series: series,
  });
};

// ======== 3. 三维 PCA 散点图 ========
const scatter3DRef = ref(null);
let scatter3DChart = null;
const initScatter3DChart = () => {
  scatter3DChart = echarts.init(scatter3DRef.value);
  
  // 按 student_persona 分组
  const groups = {};
  IPDThreeDimensionalData.value.pca_3d_scatter.forEach((item) => {
    if (!groups[item.student_persona]) groups[item.student_persona] = [];
    groups[item.student_persona].push([item.pc1, item.pc2, item.pc3]);
  });
  
  const series = Object.keys(groups).map((key) => ({
    name: key,
    type: "scatter3D",
    data: groups[key],
    symbolSize: 10,
    emphasis: {focus: "series"},
    progressive: 2000, // 渐进渲染
  }));
  
  scatter3DChart.setOption({
    title: {text: "学生画像影响因素三维"},
    tooltip: {
      formatter: (params) =>
          `${params.seriesName}<br/>PC1: ${params.value[0]}<br/>PC2: ${params.value[1]}<br/>PC3: ${params.value[2]}`,
    },
    legend: {data: Object.keys(groups), top: 30},
    xAxis3D: { name: "学习时间" },
    yAxis3D: { name: "学习过程" },
    zAxis3D: { name: "拓展与合作" },
    
    grid3D: {
      boxWidth: 200,
      boxDepth: 200,
      boxHeight: 200,
      viewControl: {
        autoRotate: false,
        distance: 400, // ✅ 初始缩小视距，避免太大
        alpha: 25, // 默认俯视角
        beta: 45,  // 默认旋转角
      },
    },
    series: series,
  });
};

// ======== 生命周期管理 ========
onMounted(() => {
  
  console.log("IPDStudentTypeData:", IPDStudentTypeData);
  console.log("IPDTwoDimensionalData:", IPDTwoDimensionalData);
  console.log("IPDThreeDimensionalData:", IPDThreeDimensionalData);
  
  initBarChart();
  initScatter2DChart();
  initScatter3DChart();
  
  window.addEventListener("resize", () => {
    barChart && barChart.resize();
    scatter2DChart && scatter2DChart.resize();
    scatter3DChart && scatter3DChart.resize();
  });
});

onBeforeUnmount(() => {
  barChart && barChart.dispose();
  scatter2DChart && scatter2DChart.dispose();
  scatter3DChart && scatter3DChart.dispose();
});
</script>

<template>

<h1 class="text-3xl font-bold text-gray-800 mb-6">学生画像看板</h1>
<div class="charts">
  <!-- 各画像人数分布 -->
  <div ref="barRef" class="chart chart-bar"></div>
  
  <!-- PCA 2D 散点图 -->
  <div ref="scatter2DRef" class="chart chart-2d"></div>
  
  <!-- PCA 3D 散点图 -->
  <div ref="scatter3DRef" class="chart chart-3d"></div>
  <CommentFollowUp
      :comment="comments.student_portrait_chart"
      :chart="IPDStudentTypeData"
  />
</div>
</template>

<style scoped>
.charts {
  display: flex;
  flex-direction: column;
  gap: 30px;
  min-height: 2000px;
}

.chart {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 10px;
}

.chart-bar {
  height: 400px;
}

.chart-2d {
  height: 500px;
}

.chart-3d {
  height: 600px;
}
</style>
