<!-- components/FiltersBar.vue -->
<script setup lang="ts">
import { ref, watch, inject} from 'vue'
import DropDownMenuWithCheckBox from '@/components/layout/DropDownMenuWithCheckBox.vue'
import { Button } from '@/components/ui/button'
import {type Academy, type Major } from '@/types/majorModels.ts'

/* ---------- 年级选项 ---------- */
interface GradeOption { value: string; label: string }
const gradeOptions: GradeOption[] = [
  { value: '大一', label: '大一' },
  { value: '大二', label: '大二' },
  { value: '大三', label: '大三' },
  { value: '大四', label: '大四' },
]

/* ---------- 响应式数据 ---------- */
const selectedAcademicsAndMajors = ref<Major[]>([])
const selectedGrade = ref<string[]>([])
const academies = inject<Academy[]>('academies', [])

/* ---------- emit ---------- */
const emit = defineEmits<{
  (e: 'update:selectedMajors', majors: Major[]): void
  (e: 'update:selectedGrade', grade: string[]): void
  (e: 'apply-filters'): void
}>()

/* ---------- 监听 & 自动 apply ---------- */
watch(selectedAcademicsAndMajors, (v) => { emit('update:selectedMajors', v); emit('apply-filters') }, { deep: true })
watch(selectedGrade, (v) => { emit('update:selectedGrade', v); emit('apply-filters') }, { deep: true })

/* ---------- 年级下拉 ---------- */
const handleGradeChange = (e: Event) => {
  const t = e.target as HTMLSelectElement
  selectedGrade.value = t.value && t.value !== 'all' ? [t.value] : []
}

/* ---------- 清空 ---------- */
const clearAllFilters = () => {
  selectedAcademicsAndMajors.value = []
  selectedGrade.value = []
  emit('apply-filters')
}

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
          :value="selectedGrade.length ? selectedGrade[0] : 'all'"
          @change="handleGradeChange"
          class="block w-[150px] pl-3 pr-8 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      >
        <option value="all">所有年级</option>
        <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ g.label }}</option>
      </select>
    </div>

    <div class="filter-actions flex flex-wrap gap-2 mt-auto">
      <Button variant="outline" size="sm" @click="clearAllFilters">清空</Button>
      <Button size="sm" @click="emit('apply-filters')">应用筛选</Button>
    </div>
  </div>
</template>

<style scoped>
.filter-group { min-width: 150px; }
</style>