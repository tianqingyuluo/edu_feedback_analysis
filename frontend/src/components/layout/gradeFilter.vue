<!-- components/FiltersBar.vue -->
<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import DropDownMenuWithCheckBox from '@/components/layout/DropDownMenuWithCheckBox.vue'
import { Button } from '@/components/ui/button'
import { defaultAcademyData, type Academy, type Major } from '@/types/majorModels.ts'

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
const academies = ref<Academy[]>([])   // ① 先留空

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

/* ---------- 构造数据 ---------- */
onMounted(() => {
  // 1. 生成「全校整体」专业
  const gradeSet = new Set<string>()
  defaultAcademyData.forEach(ac =>
      ac.majors[0].grades.forEach(g => gradeSet.add(g.name))
  )
  const allGrades = Array.from(gradeSet).sort()

  const wholeSchoolMajor: Major = {
    name: '全校整体',
    grades: allGrades.map(gName => {
      const dimLen = defaultAcademyData[0].majors[0].grades.find(g => g.name === gName)?.data.length ?? 0
      const dataAvg: number[] = []
      for (let d = 0; d < dimLen; d++) {
        let sum = 0, cnt = 0
        defaultAcademyData.forEach(ac =>
            ac.majors.forEach(ma =>
                ma.grades.forEach(gr => {
                  if (gr.name === gName && gr.data[d] !== undefined) { sum += gr.data[d]; cnt++ }
                })
            )
        )
        dataAvg.push(cnt ? Number((sum / cnt).toFixed(2)) : 0)
      }
      return { name: gName, data: dataAvg }
    })
  }

  // 2. 生成「XX学院整体」专业 & 插入对应学院
  const processed: Academy[] = defaultAcademyData.map(ac => {
    const overall: Major = {
      name: `${ac.name}整体`,
      grades: ac.majors[0].grades.map((_, gIdx) => {
        const gName = ac.majors[0].grades[gIdx].name
        const dimLen = ac.majors[0].grades[gIdx].data.length
        const dataAvg: number[] = []
        for (let d = 0; d < dimLen; d++) {
          let sum = 0, cnt = 0
          ac.majors.forEach(m => {
            const g = m.grades[gIdx]
            if (g && g.data[d] !== undefined) { sum += g.data[d]; cnt++ }
          })
          dataAvg.push(cnt ? Number((sum / cnt).toFixed(2)) : 0)
        }
        return { name: gName, data: dataAvg }
      })
    }
    return { ...ac, majors: [overall, ...ac.majors] }
  })

  // 3. 学校整体学院放最前
  academies.value = [
    { name: '学校整体', majors: [wholeSchoolMajor] },
    ...processed
  ]
})
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