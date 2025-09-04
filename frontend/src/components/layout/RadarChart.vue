<!-- components/RadarChart.vue -->
<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick,computed} from 'vue'
import * as echarts from 'echarts'
import type { Major } from '@/types/majorModels.ts' // 导入 Major 类型

const props = defineProps<{
  selectedMajorsForRadar: Major[];
  selectedGradesForRadar: string[]; // 接收选中的年级数组（会是空数组或包含一个元素的数组）
  title?: string;
  indicators?: { name: string; max: number; min: number }[];
}>();

const radarChartRef = ref<HTMLElement | null>(null);
let radarChartInstance: echarts.ECharts | null = null;
const isRadarChartReady = ref(false);

const radarIndicators = computed(() =>
        props.indicators ?? [
          { name: '课前预习得分', max: 100, min: 0 },
          { name: '课堂互动得分', max: 100, min: 0 },
          { name: '课后复习得分', max: 100, min: 0 },
          { name: '知识拓展得分', max: 100, min: 0 },
          { name: '课外自习时长', max: 100, min: 0 },
          { name: '科研实践参与得分', max: 100, min: 0 },
          { name: '合作学习得分', max: 100, min: 0 },
        ]
);

// ECharts 颜色调色板
const colorPalette = [
  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#d7504b',
  '#c6e579', '#f4e001', '#f0805a', '#26c0c0', '#b5a8f0',
  '#ff9f7f', '#87e885', '#ffcb8b', '#a978e5', '#7cd6cf'
];

const initRadarChart = () => {
  if (!radarChartRef.value) {
    // console.warn("RadarChart: radarChartRef.value is null, cannot initialize radar chart.");
    return;
  }
  const currentWidth = radarChartRef.value.clientWidth;
  const currentHeight = radarChartRef.value.clientHeight;
  if (currentWidth === 0 || currentHeight === 0) {
    // console.warn("RadarChart: container has zero dimensions. Retrying in 100ms...");
    setTimeout(initRadarChart, 100);
    return;
  }
  if (radarChartInstance) {
    radarChartInstance.dispose();
    radarChartInstance = null;
  }
  radarChartInstance = echarts.init(radarChartRef.value);
  isRadarChartReady.value = true;
  // console.log("RadarChart: ECharts instance initialized successfully.");
  updateRadarChart();
};

const updateRadarChart = () => {
  if (!radarChartInstance || !isRadarChartReady.value) {
    // console.warn("RadarChart: instance not ready, updateRadarChart skipped.");
    return;
  }

  const legendData = props.selectedMajorsForRadar.map(m => m.name);

  const seriesData = props.selectedMajorsForRadar.map((major, index) => {
    const aggregatedScores = Array(radarIndicators.value.length).fill(0); // 始终是6个维度
    const gradeCountsPerIndicator = Array(radarIndicators.value.length).fill(0); // 始终是6个维度
    let gradesToProcess: string[] = [];

    // Determine which grades to process
    if (props.selectedGradesForRadar.length === 0) {
      // If no specific grade selected, process all grades available in the major data
      gradesToProcess = major.grades.map(g => g.name);
      if (gradesToProcess.length === 0) {
        // If no grades at all, return an empty series value for this major
        return {
          name: major.name,
          value: Array(radarIndicators.value.length).fill(0),
          itemStyle: { color: colorPalette[index % colorPalette.length] },
          lineStyle: { width: 0 }, // No line if no data
          areaStyle: { opacity: 0 } // No area if no data
        };
      }
    } else {
      // Process only the specific selected grade(s) - in your case, typically one grade
      gradesToProcess = props.selectedGradesForRadar;
    }

    // Aggregate data for the determined grades
    gradesToProcess.forEach(gradeName => {
      const gradeEntry = major.grades.find(g => g.name === gradeName);
      if (gradeEntry) {
        // 【!!! 关键修改：方案 B --- 只取前 radarIndicators.value.length (6) 位数据 !!!】
        for (let i = 0; i < radarIndicators.value.length; i++) { // 循环雷达指标的个数 (6次)
          if (i < gradeEntry.data.length) { // 确保原始数据有这么多维度以避免越界
            aggregatedScores[i] += gradeEntry.data[i];
            gradeCountsPerIndicator[i]++;
          }
        }
      } else {
        // console.warn(`RadarChart: Major "${major.name}" - NO data entry found for grade "${gradeName}" among its grades. Available: ${major.grades.map(g => g.name).join(', ')}`);
      }
    });

    // Calculate the averaged scores for this major
    const averagedRadarScores = aggregatedScores.map((sum, i) =>
        gradeCountsPerIndicator[i] > 0 ? sum / gradeCountsPerIndicator[i] : 0
    );

    return {
      name: major.name,
      // Ensure values are within 0-100 range and are numbers
      value: averagedRadarScores.map(score => Math.max(0, Math.min(score, 100))),
      itemStyle: {
        color: colorPalette[index % colorPalette.length]
      },
      lineStyle: {
        width: 2
      },
      areaStyle: {
        opacity: 0.2
      }
    };
  });

  // ECharts 选项配置
  const option: echarts.EChartsOption = {
    title: {
      text: props.title ?? '专业 EHI 雷达图分析',
      left: 'center',
      top: '2%',
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {},
    legend: {
      data: legendData,
      bottom: '2%',
      left: 'center',
      selectedMode: 'multiple',
      itemGap: 10,
      textStyle: {
        fontSize: 12
      }
    },
    radar: {
      indicator: radarIndicators.value,
      radius: '70%',
      center: ['50%', '50%'],
      axisName: {
        color: '#000000', 
        fontSize: 12
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(211, 253, 250, 0.8)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(211, 253, 250, 0.8)'
        }
      },
      splitArea: {
        areaStyle: {
          color: ['#F6FAFD', '#EDF5F8'].map(color => echarts.color.modifyAlpha(color, 0.8))
        }
      }
    },
    series: [
      {
        name: '专业指标',
        type: 'radar',
        data: seriesData,
        symbol: 'none',
        animationDuration: 1000,
        animationEasing: 'cubicOut'
      }
    ]
  };

  radarChartInstance.setOption(option, { notMerge: true });
};

const resizeRadarChart = () => {
  if (radarChartInstance && isRadarChartReady.value) {
    radarChartInstance.resize();
  }
};

onMounted(() => {
  nextTick(() => {
    initRadarChart();
  });
  window.addEventListener('resize', resizeRadarChart);
});

onUnmounted(() => {
  if (radarChartInstance) {
    radarChartInstance.dispose();
    radarChartInstance = null;
    isRadarChartReady.value = false;
  }
  window.removeEventListener('resize', resizeRadarChart);
});

watch([() => props.selectedMajorsForRadar, () => props.selectedGradesForRadar], () => {
  if (isRadarChartReady.value) {
    nextTick(() => {
      updateRadarChart();
    });
  }
}, { deep: true });
</script>

<template>
  <div class="radar-chart-card bg-white p-6 rounded-lg shadow-md h-full flex flex-col">
    <div ref="radarChartRef" class="radar-chart-container flex-grow min-h-[450px]"></div>
  </div>
</template>

<style scoped>
/* 样式保持不变 */
</style>