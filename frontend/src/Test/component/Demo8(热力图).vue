<script setup>
import { ref, onMounted } from "vue";
import * as echarts from "echarts";
import {heatmapData} from '@/types/DPFEValues.js'
const jsonData = heatmapData

const chartRef = ref(null);

onMounted(() => {
  const chart = echarts.init(chartRef.value);
  
  const data = [];
  const labels = jsonData.labels;
  
  jsonData.matrix.forEach((row, i) => {
    row.forEach((val, j) => {
      data.push([j, i, val.toFixed(2)]);
    });
  });
  
  const option = {
    tooltip: {
      position: "top",
      formatter: (params) => {
        return `<b>${labels[params.value[1]]}</b> vs <b>${labels[params.value[0]]}</b><br/>相关系数: <b>${params.value[2]}</b>`;
      }
    },
    grid: {
      left: "18%",
      top: "10%",
      right: "10%",
      bottom: "18%"
    },
    xAxis: {
      type: "category",
      data: labels,
      splitArea: {show: true},
      axisLabel: {rotate: 45, fontSize: 12}
    },
    yAxis: {
      type: "category",
      data: labels,
      splitArea: {show: true},
      axisLabel: {fontSize: 12}
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: "vertical",
      left: "left",
      top: "center",
      precision: 2,
      inRange: {
        color: ["#2166ac", "#f7f7f7", "#b2182b"]
      }
    },
    series: [
      {
        name: "相关性",
        type: "heatmap",
        data,
        label: {
          show: true,
          formatter: (p) => p.value[2],
          color: "#000",
          fontSize: 11
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: "rgba(0, 0, 0, 0.5)"
          }
        }
      }
    ]
  };
  
  chart.setOption(option);
});
</script>

<template>
<div class="w-full h-screen flex items-center justify-center">
  <div ref="chartRef" class="w-[1000px] h-[800px]"></div>
</div>
</template>
