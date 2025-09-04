<!-- views/HomeView.vue -->
<script setup lang="ts">
import {ref, onMounted} from 'vue'
import FiltersBar from '@/components/layout/gradeFilter.vue'
import HealthGauge from '@/components/layout/HealthGauge.vue'
import RadarChart from '@/components/layout/RadarChart.vue'
import type { Major } from '@/types/majorModels.ts'

const selectedMajorsFiltered = ref<Major[]>([]);
const selectedGradeFiltered = ref<string[]>([]);
const calculatedEHI = ref<number>(0);

// 定义一个常量用于指明 EHI 值的索引
const EHI_DATA_INDEX = 7;

const calculateEHI = () => {

  if (selectedMajorsFiltered.value.length === 0) {
    calculatedEHI.value = 0;
    return;
  }

  let totalEHIValueSum = 0;
  let contributionCount = 0;

  selectedMajorsFiltered.value.forEach(major => {
    let majorSeventhDataPoints: number[] = [];

    if (selectedGradeFiltered.value.length === 0) {
      // 没有任何年级被选中，表示选择“所有年级”
      major.grades.forEach(gradeData => {
        // 确保数据长度足够且 EHI_DATA_INDEX 存在
        if (gradeData.data.length > EHI_DATA_INDEX) {
          majorSeventhDataPoints.push(gradeData.data[EHI_DATA_INDEX]);
        }
      });
    } else {
      // 选择了具体的年级 (selectedGradeFiltered 数组中只有一个元素)
      const gradeName = selectedGradeFiltered.value[0];
      const gradeData = major.grades.find(g => g.name === gradeName);
      if (gradeData && gradeData.data.length > EHI_DATA_INDEX) {
        majorSeventhDataPoints.push(gradeData.data[EHI_DATA_INDEX]);
      }
    }

    if (majorSeventhDataPoints.length > 0) {
      // 计算该专业在所有匹配年级下的所有第7位数据的平均值
      const avgSeventhDataForMajor = majorSeventhDataPoints.reduce((sum, val) => sum + val, 0) / majorSeventhDataPoints.length;
      totalEHIValueSum += avgSeventhDataForMajor;
      contributionCount++;
    }
  });

  if (contributionCount > 0) {
    // 【最终 EHI】计算所有“贡献”的专业平均值，作为最终 EHI 值
    let newEHI = totalEHIValueSum / contributionCount;
    calculatedEHI.value = Math.max(0, Math.min(100, Math.round(newEHI))); // 确保在0-100之间
    console.log("HomeView: EHI calculated successfully. New calculatedEHI (average of 7th dimension):", calculatedEHI.value);
  } else {
    calculatedEHI.value = 0; // 没有匹配到任何数据
    console.log("HomeView: No valid 7th dimension data to calculate EHI. calculatedEHI set to 0.");
  }
};

const handleApplyFilters = () => {
  // console.log("HomeView: handleApplyFilters triggered!");
  calculateEHI();
};

onMounted(() => {
  // console.log("HomeView: Component mounted. Performing initial EHI calculation.");
  calculateEHI();
});
</script>

<template>
  <div class="dashboard-layout p-6 bg-gray-100 h-[80vh]">
    <h1 class="text-3xl font-bold text-gray-800 mb-6">学生健康度分析仪表盘</h1>
    <div class="mb-6">
      <FiltersBar
          v-model:selectedMajors="selectedMajorsFiltered"
          v-model:selectedGrade="selectedGradeFiltered"
          @apply-filters="handleApplyFilters"
      />
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-1">
        <HealthGauge :ehi-value="calculatedEHI" MetricName="EHI"/>
      </div>
      <div class="md:col-span-2">
        <RadarChart
            :selected-majors-for-radar="selectedMajorsFiltered"
            :selected-grades-for-radar="selectedGradeFiltered"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-layout {
  font-family: 'Inter', sans-serif;
}
</style>