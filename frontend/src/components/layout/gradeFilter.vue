<!-- components/FiltersBar.vue -->
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import DropDownMenuWithCheckBox from '@/components/layout/DropDownMenuWithCheckBox.vue'
import { Button } from '@/components/ui/button'
import { defaultAcademyData, type Academy, type Major } from '@/types/majorModels.ts'

interface GradeOption {
  value: string;
  label: string;
}

const gradeOptions: GradeOption[] = [
  { value: '大一', label: '大一' },
  { value: '大二', label: '大二' },
  { value: '大三', label: '大三' },
  { value: '大四', label: '大四' },
];

const academies = ref<Academy[]>(defaultAcademyData);
const selectedAcademicsAndMajors = ref<Major[]>([]);
const selectedGrade = ref<string[]>([]); // 内部仍然保持数组形式

const emit = defineEmits<{
  (e: 'update:selectedMajors', majors: Major[]): void;
  (e: 'update:selectedGrade', grade: string[]): void;
  (e: 'apply-filters'): void;
}>();

// 【修改点 1】监听 selectedAcademicsAndMajors 变化
watch(selectedAcademicsAndMajors, (newValue) => {
  emit('update:selectedMajors', newValue);
  emit('apply-filters'); // <--- 【关键】专业变化时，立即触发应用筛选
}, { deep: true });

// 【修改点 2】监听 selectedGrade 变化
watch(selectedGrade, (newValue) => {
  emit('update:selectedGrade', newValue);
  emit('apply-filters'); // <--- 【关键】年级变化时，立即触发应用筛选
}, { deep: true }); // 年级现在是数组，所以 deep:true 更安全

const handleGradeChange = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  if (!target.value || target.value === 'all') {
    selectedGrade.value = [];
  } else {
    selectedGrade.value = [target.value];
  }
};

const clearAllFilters = () => {
  selectedAcademicsAndMajors.value = [];
  selectedGrade.value = [];
  emit('apply-filters');
};

const applyFilters = () => {
  emit('apply-filters');
};

const isApplyDisabled = computed(() => {
  return selectedAcademicsAndMajors.value.length === 0 && selectedGrade.value.length === 0;
});
</script>

<template>
  <div class="filter-bar-container bg-white p-4 rounded-lg shadow-sm flex flex-wrap items-end gap-4">
    <div class="filter-group">
      <label class="block text-sm font-medium text-gray-700 mb-1">学院 & 专业</label>
      <DropDownMenuWithCheckBox
          v-model="selectedAcademicsAndMajors"
          :academies="academies"
          placeholder="选择学院和专业"
          class="w-[250px]"
      />
    </div>
    <div class="filter-group">
      <label class="block text-sm font-medium text-gray-700 mb-1">年级</label>
      <select
          :value="selectedGrade.length > 0 ? selectedGrade[0] : 'all'"
          @change="handleGradeChange"
          class="block w-[150px] pl-3 pr-8 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      >
        <option value="all">所有年级</option>
        <option v-for="grade in gradeOptions" :key="grade.value" :value="grade.value">
          {{ grade.label }}
        </option>
      </select>
    </div>
    <div class="filter-actions flex flex-wrap gap-2 mt-auto">
      <Button
          variant="outline"
          size="sm"
          @click="clearAllFilters"
          :disabled="isApplyDisabled"
      >
        清空
      </Button>
      <Button
          size="sm"
          @click="applyFilters"
          :disabled="isApplyDisabled"
      >
        应用筛选
      </Button>
    </div>
  </div>
</template>

<style scoped>
.filter-group {
  min-width: 150px;
}
</style>