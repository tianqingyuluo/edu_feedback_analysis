<!-- components/HealthGauge.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
const props = defineProps<{
  ehiValue: number; // 0-100
  title?: string;
  MetricName:string;
}>();
const gaugeChartRef = ref<HTMLElement | null>(null);
let gaugeChartInstance: echarts.ECharts | null = null;
const isGaugeChartReady = ref(false);
const healthLevel = computed(() => {
  if (props.ehiValue >= 80) return { text: '健康度高', color: '#38a169' };
  if (props.ehiValue >= 60) return { text: '健康度中等', color: '#d69e2e' };
  return { text: '健康度低 / 风险', color: '#e53e3e' };
});
const updateGaugeChart = () => {
  if (!gaugeChartInstance) {
    console.warn("HealthGauge: ECharts instance not found or disposed during update, skipping.");
    return;
  }
  if (!isGaugeChartReady.value) {
    console.warn("HealthGauge: isGaugeChartReady is false during update, skipping (should not happen if init successful).");
    return;
  }
  console.log(`HealthGauge: updateGaugeChart called. Current props.ehiValue: ${props.ehiValue}. Applying to chart.`);
  const option: echarts.EChartsOption = {
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 100,
        center: ['50%', '55%'],
        radius: '100%',
        axisLabel: {
          distance: 25,
          color: '#999',
          fontSize: 12
        },
        splitNumber: 5,
        axisLine: {
          lineStyle: {
            width: 30,
            color: [
              [0.59, '#e53e3e'],
              [0.79, '#d69e2e'],
              [1, '#38a169']
            ]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12.3,16.5H0.5L12.8,0.7z',
          length: '70%',
          width: 10,
          offsetCenter: [0, '-5%'],
          itemStyle: {
            // ECharts DEPRECATED: color: 'auto'; use color: 'inherit' instead.
            color: 'inherit' // Changed from 'auto' to 'inherit' as suggested
          }
        },
        axisTick: {
          distance: -30,
          length: 8,
          lineStyle: {
            color: '#fff',
            width: 2
          }
        },
        splitLine: {
          distance: -30,
          length: 30,
          lineStyle: {
            color: '#fff',
            width: 4
          }
        },
        detail: {
          valueAnimation: true,
          formatter: '{value}',
          offsetCenter: [0, '80%'],
          fontSize: 36,
          fontWeight: 'bold',
          color: 'inherit' // Changed from 'auto' to 'inherit'
        },
        data: [
          {
            value: props.ehiValue, // Bind to the prop here
            name: props.MetricName
          }
        ],
        title: {
          offsetCenter: [0, '50%'],
          fontSize: 16,
          color: '#333'
        }
      }
    ]
  };
  try {
    gaugeChartInstance.setOption(option, { notMerge: true });
    console.log("HealthGauge: Chart option set successfully for value:", props.ehiValue);
  } catch (error) {
    console.error("HealthGauge: Error setting chart option:", error);
  }
};

// 【!!! 关键修改 !!!】 集中初始化和首次渲染逻辑
onMounted(() => {
  console.log("HealthGauge: Component mounted. Initializing ECharts.");
  nextTick(() => {
    if (!gaugeChartRef.value) {
      console.error("HealthGauge: gaugeChartRef.value is null in onMounted nextTick, cannot initialize.");
      return;
    }
    try {
      gaugeChartInstance = echarts.init(gaugeChartRef.value);
      isGaugeChartReady.value = true;
      console.log("HealthGauge: ECharts instance initialized successfully. isGaugeChartReady:", isGaugeChartReady.value);
      // 【关键】ECharts 实例初始化完成后，立即用当前最新的 prop 值进行第一次渲染
      updateGaugeChart();
    } catch (error) {
      console.error("HealthGauge: Failed to initialize ECharts instance in onMounted:", error);
    }
  });
  window.addEventListener('resize', resizeGaugeChart);
});

onUnmounted(() => {
  console.log("HealthGauge: Component unmounted. Disposing ECharts instance.");
  if (gaugeChartInstance) {
    gaugeChartInstance.dispose();
    gaugeChartInstance = null;
    isGaugeChartReady.value = false;
  }
  window.removeEventListener('resize', resizeGaugeChart);
});
// Watch for changes in the ehiValue prop and trigger chart update ONLY IF CHART IS READY
watch(() => props.ehiValue, (newValue, oldValue) => {
  console.log(`HealthGauge Watcher: ehiValue prop changed from ${oldValue} to ${newValue}.`);
  if (isGaugeChartReady.value) { // 只有当 ECharts 实例准备就绪后才由 watcher 触发更新
    nextTick(() => {
      console.log("HealthGauge Watcher: Chart is ready, calling updateGaugeChart.");
      updateGaugeChart();
    });
  } else {
    // console.warn("HealthGauge Watcher: Chart not ready yet when ehiValue changed. Skipping update.");
    // Initial update will be handled by onMounted after initialization.
  }
}, { immediate: false }); // 【关键修改】immediate: false，首次渲染由 onMounted 统一处理
const resizeGaugeChart = () => {
  if (gaugeChartInstance && isGaugeChartReady.value) {
    gaugeChartInstance.resize();
  }
};
</script>
<template>
  <div class="health-gauge-card bg-white p-6 rounded-lg shadow-md flex flex-col items-center h-full justify-center">
    <h3 class="text-xl font-semibold mb-4 pt-24 text-center">{{props.title||'综合健康指数 (EHI)'}}</h3>
    <div ref="gaugeChartRef" class="gauge-chart-container w-full max-w-[300px] h-[500px] mx-auto"></div>
    <div class="ehi-summary mt-4 text-center pb-24">
      <span class="text-3xl font-bold" :style="{ color: healthLevel.color }">{{ props.ehiValue }}</span>
      <span class="ml-2 text-xl font-medium" :style="{ color: healthLevel.color }">({{ healthLevel.text }})</span>
    </div>
  </div>
</template>
<style scoped>
.health-gauge-card {
  min-height: 350px; /* 确保卡片有足够的最小高度 */
}
</style>