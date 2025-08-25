<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import DropDownMenuWithCheckBox from '@/components/layout/DropDownMenuWithCheckBox.vue'
import { Button } from '@/components/ui/button'

// 模拟学院专业数据（包含假数据）
const mockAcademyData = [
  // ... (你的 mockAcademyData 保持不变)
  {
    id: 1,
    name: "计算机学院",
    majors: [
      {
        id: 101,
        name: "计算机科学与技术",
        data: [85, 92, 78, 95, 88, 76, 83, 90, 87, 94, 79, 86]
      },
      {
        id: 102,
        name: "软件工程",
        data: [72, 85, 91, 68, 77, 89, 94, 81, 75, 83, 90, 78]
      },
      {
        id: 103,
        name: "人工智能",
        data: [95, 88, 92, 96, 89, 93, 87, 94, 91, 97, 90, 98]
      },
      {
        id: 104,
        name: "网络安全",
        data: [83, 79, 86, 91, 75, 82, 88, 84, 90, 87, 92, 85]
      }
    ]
  },
  {
    id: 2,
    name: "经济管理学院",
    majors: [
      {
        id: 201,
        name: "经济学",
        data: [67, 74, 81, 69, 72, 78, 85, 76, 79, 83, 70, 75]
      },
      {
        id: 202,
        name: "工商管理",
        data: [89, 82, 76, 91, 85, 88, 80, 84, 87, 92, 79, 86]
      },
      {
        id: 203,
        name: "金融学",
        data: [94, 87, 91, 96, 89, 92, 85, 90, 93, 97, 88, 95]
      },
      {
        id: 204,
        name: "会计学",
        data: [78, 83, 75, 80, 86, 79, 84, 81, 77, 82, 85, 88]
      }
    ]
  },
  {
    id: 3,
    name: "机械工程学院",
    majors: [
      {
        id: 301,
        name: "机械设计制造",
        data: [82, 88, 75, 79, 84, 90, 86, 81, 77, 83, 89, 85]
      },
      {
        id: 302,
        name: "车辆工程",
        data: [91, 85, 89, 94, 87, 92, 83, 88, 90, 95, 86, 93]
      },
      {
        id: 303,
        name: "材料成型",
        data: [76, 81, 74, 79, 83, 78, 85, 80, 77, 82, 84, 87]
      }
    ]
  }
]
// 使用示例数据
const academies = ref(mockAcademyData)

// 预定义的颜色数组
const colorPalette = [
  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#d7504b',
  '#c6e579', '#f4e001', '#f0805a', '#26c0c0', '#b5a8f0',
  '#ff9f7f', '#87e885', '#ffcb8b', '#a978e5', '#7cd6cf'
]

const selectedMajorIds = ref<number[]>([])
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null
const isChartReady = ref(false)

// 获取选中的专业信息
const selectedMajors = () => {
  return academies.value.flatMap(academy =>
      academy.majors.filter(major => selectedMajorIds.value.includes(major.id))
  )
}

// 清空选择
const clearSelection = () => {
  selectedMajorIds.value = []
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) {
    console.warn("chartRef.value is null, cannot initialize chart.");
    return;
  }

  // 确保DOM元素有尺寸
  const currentWidth = chartRef.value.clientWidth;
  const currentHeight = chartRef.value.clientHeight;

  console.log('Chart container dimensions:', currentWidth, 'x', currentHeight);

  if (currentWidth === 0 || currentHeight === 0) {
    console.warn("Chart container has zero dimensions. Retrying in 100ms...");
    setTimeout(initChart, 100); // 延迟重试
    return;
  }

  // 如果已经存在实例，先销毁
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }

  chartInstance = echarts.init(chartRef.value);
  isChartReady.value = true;
  console.log("ECharts instance initialized successfully.");

  // 初始空配置 (但包含轴线、标题等基础元素)
  const option = {
    title: {
      text: '专业数据统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: [], // 初始为空
      top: '10%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    },
    yAxis: {
      type: 'value',
      name: '分数/数量'
    },
    series: [] // 初始为空
  };
  chartInstance.setOption(option);

  // 首次初始化后，立即尝试更新一次图表，以处理初始状态或默认选择
  updateChart();
}

// 更新图表数据 - 现在使用真实的模拟数据
const updateChart = () => {
  if (!chartInstance || !isChartReady.value) {
    console.warn("Chart instance not ready, updateChart skipped.");
    return;
  }

  const selectedMajorsList = selectedMajors();
  const selectedMajorNames = selectedMajorsList.map(major => major.name);

  // 确保标题在无数据时显示提示
  const titleText = selectedMajorsList.length > 0 ? '专业数据统计' : '专业数据统计 (请选择专业)';

  // 创建完整的配置选项，确保包含所有必要的属性
  const option = {
    title: {
      text: titleText,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: selectedMajorNames,
      top: '10%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    },
    yAxis: {
      type: 'value',
      name: '分数/数量'
    },
    series: selectedMajorsList.map((major, index) => ({
      name: major.name,
      type: 'line',
      data: major.data, // 使用真实的模拟数据
      lineStyle: {
        width: 3
      },
      itemStyle: {
        color: colorPalette[index % colorPalette.length]
      }
    }))
  };

  // 使用 notMerge: true 确保完全替换而不是合并旧配置
  chartInstance.setOption(option, { notMerge: true });
  console.log("Chart updated.", selectedMajorsList.length, "majors displayed.");
}

// 监听选择变化，自动更新图表
watch(selectedMajorIds, () => {
  // 仅在图表实例准备好后才进行更新操作
  if (isChartReady.value && chartInstance) {
    // 使用 nextTick 确保DOM更新后执行
    nextTick(() => {
      updateChart();
    });
  }
}, { immediate: true }); // immediate: true 确保在组件挂载时立即执行一次

// 响应式调整图表大小
const resizeChart = () => {
  if (chartInstance && isChartReady.value) {
    chartInstance.resize();
  }
}

onMounted(() => {
  // 使用 nextTick 确保 DOM 已经渲染
  nextTick(() => {
    initChart();
  });
  window.addEventListener('resize', resizeChart);
})

// 组件卸载时清理
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
    isChartReady.value = false;
  }
  window.removeEventListener('resize', resizeChart);
})
</script>

<template>
  <div class="academy-chart-container">
    <!-- 顶部控制栏 -->
    <div class="control-bar">
      <div class="control-left">
        <DropDownMenuWithCheckBox
            v-model="selectedMajorIds"
            :academies="academies"
            placeholder="选择学院和专业"
            class="dropdown-menu"
        />
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <Button
              variant="outline"
              size="sm"
              @click="clearSelection"
              :disabled="selectedMajorIds.length === 0"
          >
            清空
          </Button>
          <Button
              size="sm"
              @click="updateChart"
              :disabled="selectedMajorIds.length === 0"
          >
            刷新图表
          </Button>
        </div>
      </div>
      <!-- 右上角可以放其他控件 -->
      <div class="selected-count">
        已选 {{ selectedMajorIds.length }} 个专业
      </div>
    </div>
    <!-- 图表区域 -->
    <div class="chart-section">
      <!-- ECharts 图表容器 -->
      <div ref="chartRef" class="chart-container"></div>
    </div>
  </div>
</template>

<style scoped>
.academy-chart-container {
  display: flex;
  flex-direction: column;
  height: 90vh; /* 确保容器有足够的高度 */
  padding: 20px;
  background-color: #f5f7fa;
}

.control-bar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap; /* 适应小屏幕 */
  gap: 15px;
}

.control-left {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.selected-count {
  font-size: 0.9rem;
  color: #666;
  white-space: nowrap;
}

.chart-section {
  flex-grow: 1; /* 让图表区域占据剩余空间 */
  display: flex;
  flex-direction: column;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chart-header {
  /* 移除或简化，因为ECharts有自己的标题 */
  margin-bottom: 10px;
  text-align: center;
  /* 保持可见性，但 ECharts 自己的标题会覆盖 */
}

.chart-title {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 5px;
}

.chart-subtitle {
  font-size: 0.9rem;
  color: #888;
}

.chart-container {
  flex-grow: 1; /* 关键：让图表容器占据 chart-section 内可用空间 */
  min-height: 400px; /* 至少给一个最小高度，防止内容少时为0 */
  /* padding-top: 20px; 适当调整，避免内容盖住echarts的顶部区域 */
}
</style>
