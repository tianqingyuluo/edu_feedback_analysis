

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";

// 模拟后端返回的 JSON 数据（你实际可以通过 API 获取）
const chartData = {
  xAxis: [
    "主成分1",
    "主成分2",
    "主成分3",
    "主成分4",
    "主成分5",
    "主成分6",
    "主成分7"
  ],
  bar: [
    0.31040233252697064,
    0.1626172291672862,
    0.07333080913381385,
    0.06880071570447906,
    0.05101947532427003,
    0.050830827952017696,
    0.04288523257771087
  ],
  line: [
    0.31040233252697064,
    0.47301956169425685,
    0.5463503708280707,
    0.6151510865325498,
    0.6661705618568198,
    0.7170013898088374,
    0.7598866223865482
  ]
};

const chartRef = ref(null);
let chartInstance = null;

const initChart = () => {
  chartInstance = echarts.init(chartRef.value);
  
  const option = {
    title: {
      text: "PCA 主成分方差贡献率"
    },
    tooltip: {
      trigger: "axis"
    },
    legend: {
      data: ["单个主成分方差贡献率", "累计方差贡献率"]
    },
    xAxis: {
      type: "category",
      data: chartData.xAxis
    },
    yAxis: {
      type: "value",
      name: "方差解释比例"
    },
    series: [
      {
        name: "单个主成分方差贡献率",
        type: "bar",
        data: chartData.bar,
        itemStyle: {
          color: "#5470C6"
        }
      },
      {
        name: "累计方差贡献率",
        type: "line",
        data: chartData.line,
        itemStyle: {
          color: "#EE6666"
        },
        smooth: true
      }
    ]
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
<div class="chart-container">
  <div ref="chartRef" class="chart"></div>
</div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
}
.chart {
  width: 100%;
  height: 100%;
}
</style>
