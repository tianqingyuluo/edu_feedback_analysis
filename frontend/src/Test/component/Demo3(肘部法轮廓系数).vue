<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";

// 模拟后端返回的 JSON 数据（你可以通过接口获取）
const clusterData = {
  k: [2, 3, 4, 5, 6, 7, 8, 9],
  wcss: [
    132344.86691569278,
    111554.60866224075,
    99210.98628550781,
    91243.06359960242,
    85872.26624278113,
    81347.59751551146,
    77241.26858626751,
    72957.96542254437
  ],
  silhouette: [
    0.26339974437540487,
    0.22012531774956814,
    0.1821608829199447,
    0.17149771126931257,
    0.16472566339972697,
    0.16571350908401528,
    0.16447327325547345,
    0.16873965689016268
  ]
};

const elbowRef = ref(null);
const silhouetteRef = ref(null);
let elbowChart = null;
let silhouetteChart = null;

const initCharts = () => {
  // 肘部法 (WCSS)
  elbowChart = echarts.init(elbowRef.value);
  elbowChart.setOption({
    title: { text: "肘部法 (WCSS)" },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: clusterData.k,
      name: "聚类数 K"
    },
    yAxis: {
      type: "value",
      name: "WCSS"
    },
    series: [
      {
        name: "WCSS",
        type: "line",
        data: clusterData.wcss,
        smooth: true,
        symbol: "circle"
      }
    ]
  });
  
  // 轮廓系数
  silhouetteChart = echarts.init(silhouetteRef.value);
  silhouetteChart.setOption({
    title: { text: "轮廓系数 (Silhouette Score)" },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: clusterData.k,
      name: "聚类数 K"
    },
    yAxis: {
      type: "value",
      name: "轮廓系数"
    },
    series: [
      {
        name: "轮廓系数",
        type: "line",
        data: clusterData.silhouette,
        smooth: true,
        symbol: "circle"
      }
    ]
  });
};

onMounted(() => {
  initCharts();
  window.addEventListener("resize", () => {
    elbowChart && elbowChart.resize();
    silhouetteChart && silhouetteChart.resize();
  });
});

onBeforeUnmount(() => {
  elbowChart && elbowChart.dispose();
  silhouetteChart && silhouetteChart.dispose();
});
</script>

<template>
<div class="charts">
  <!-- 肘部法 -->
  <div ref="elbowRef" class="chart"></div>
  <!-- 轮廓系数 -->
  <div ref="silhouetteRef" class="chart"></div>
</div>
</template>

<style scoped>
.charts {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.chart {
  width: 100%;
  height: 400px;
}
</style>
