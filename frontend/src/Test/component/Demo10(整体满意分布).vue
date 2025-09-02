<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';

// JSON 数据
const jsonData = {
  "labels": ["满意", "较满意", "一般", "较不满意", "不满意"],
  "values": [2929, 2877, 3782, 3280, 958]
};

const chartRef = ref(null);
let chartInstance = null;

const initChart = () => {
  chartInstance = echarts.init(chartRef.value);
  
  const option = {
    title: {
      text: '满意度分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0];
        return `${p.axisValue}<br/>人数: ${p.data}`;
      }
    },
    xAxis: {
      type: 'category',
      data: jsonData.labels,
      axisTick: { alignWithLabel: true }
    },
    yAxis: {
      type: 'value',
      name: '人数'
    },
    series: [
      {
        name: '人数',
        type: 'bar',
        data: jsonData.values,
        itemStyle: {
          color: '#4CAF50'
        },
        barWidth: '50%'
      }
    ]
  };
  
  chartInstance.setOption(option);
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', () => {
    chartInstance && chartInstance.resize();
  });
});

onBeforeUnmount(() => {
  chartInstance && chartInstance.dispose();
});
</script>

<template>
<div ref="chartRef" class="w-full h-[500px]"></div>
</template>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>
