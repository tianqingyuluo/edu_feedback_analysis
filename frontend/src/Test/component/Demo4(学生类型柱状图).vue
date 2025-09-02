<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";

// 新的 JSON 数据
const personaData = {
  labels: ["学业挣扎型", "自主学习型", "科研学霸型", "社团活跃型"],
  values: [6345, 3659, 2702, 1120]
};

const barRef = ref(null);
let barChart = null;

const initCharts = () => {
  // -------- 柱状图：人数分布 --------
  barChart = echarts.init(barRef.value);
  barChart.setOption({
    title: { text: "各画像人数分布" },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: personaData.labels
    },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: personaData.values,
        itemStyle: { color: "#5470C6" }
      }
    ]
  });
};

onMounted(() => {
  initCharts();
  window.addEventListener("resize", () => {
    barChart && barChart.resize();
  });
});

onBeforeUnmount(() => {
  barChart && barChart.dispose();
});
</script>

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
<template>
<div class="charts">
  <!-- 各画像人数分布 -->
  <div ref="barRef" class="chart"></div>
</div>
</template>

