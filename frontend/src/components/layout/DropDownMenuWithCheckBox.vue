<!-- AcademyMajorDropdown.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { Checkbox } from '@/components/ui/checkbox'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { ChevronDownIcon } from 'lucide-vue-next'
import type { Academy } from "@/types/majorModels.ts";

// 定义props
interface Props {
  academies: Academy[]
  modelValue?: number[] // 选中的专业ID数组
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  academies: () => [],
  modelValue: () => [],
  placeholder: '选择学院专业'
})

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
}>()

const isOpen = ref(false)

// 处理专业选择
const handleMajorSelect = (majorId: number) => {
  const newSelected = [...props.modelValue]
  const index = newSelected.indexOf(majorId)

  if (index > -1) {
    newSelected.splice(index, 1) // 取消选择
  } else {
    newSelected.push(majorId) // 选择
  }

  emit('update:modelValue', newSelected)
}

// 检查专业是否被选中
const isMajorSelected = (majorId: number) => {
  return props.modelValue.includes(majorId)
}

// 检查学院是否部分选中（有些专业选了，有些没选）
const isAcademyIndeterminate = (academy: Academy) => {
  const selectedCount = academy.majors.filter(major =>
      props.modelValue.includes(major.id)
  ).length
  return selectedCount > 0 && selectedCount < academy.majors.length
}

// 检查学院是否全部选中
const isAcademyAllSelected = (academy: Academy) => {
  return academy.majors.every(major =>
      props.modelValue.includes(major.id)
  )
}

// 切换学院所有专业的选择状态
const toggleAcademySelection = (academy: Academy) => {
  const allSelected = isAcademyAllSelected(academy)
  let newSelected = [...props.modelValue]

  if (!allSelected) {
    // 选择所有该学院的专业（去重）
    const academyMajorIds = academy.majors.map(major => major.id)
    const combined = [...new Set([...newSelected, ...academyMajorIds])]
    newSelected = combined
  } else {
    // 取消选择所有该学院的专业
    newSelected = newSelected.filter(id =>
        !academy.majors.some(major => major.id === id)
    )
  }

  emit('update:modelValue', newSelected)
}

// 显示选中的专业名称 - 修改为始终显示数量
const selectedMajorsText = computed(() => {
  if (props.modelValue.length === 0) {
    return props.placeholder
  }
  return `已选择 ${props.modelValue.length} 个专业`
})
</script>

<template>
  <DropdownMenu v-model:open="isOpen">
    <DropdownMenuTrigger as-child>
      <Button variant="outline" class="w-full justify-between">
        <span>{{ selectedMajorsText }}</span>
        <ChevronDownIcon class="h-4 w-4 opacity-50" />
      </Button>
    </DropdownMenuTrigger>

    <DropdownMenuContent class="w-80 max-h-96 overflow-y-auto">
      <DropdownMenuLabel>选择学院和专业</DropdownMenuLabel>
      <DropdownMenuSeparator />

      <DropdownMenuGroup v-for="academy in academies" :key="academy.id">
        <!-- 学院项（可点击选择全部） -->
        <DropdownMenuItem
            class="px-2 py-1.5 cursor-pointer"
            @select.prevent
            @click="toggleAcademySelection(academy)"
        >
          <div class="flex items-center space-x-2 w-full">
            <Checkbox
                :model-value="isAcademyAllSelected(academy)"
                :indeterminate="isAcademyIndeterminate(academy)"
                @click.stop
                @update:model-value="toggleAcademySelection(academy)"
            />
            <span class="font-semibold text-sm">{{ academy.name }}</span>
            <span class="text-xs text-muted-foreground ml-auto">
              ({{
                academy.majors.filter(m => modelValue.includes(m.id)).length
              }}/{{ academy.majors.length }})
            </span>
          </div>
        </DropdownMenuItem>

        <!-- 专业项 -->
        <DropdownMenuItem
            v-for="major in academy.majors"
            :key="major.id"
            class="pl-8 pr-2 py-1.5 cursor-pointer"
            @select.prevent
            @click="handleMajorSelect(major.id)"
        >
          <div class="flex items-center space-x-2 w-full">
            <Checkbox
                :model-value="isMajorSelected(major.id)"
                @click.stop
                @update:model-value="handleMajorSelect(major.id)"
            />
            <span class="text-sm">{{ major.name }}</span>
          </div>
        </DropdownMenuItem>

        <DropdownMenuSeparator v-if="academy !== academies[academies.length - 1]" />
      </DropdownMenuGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>