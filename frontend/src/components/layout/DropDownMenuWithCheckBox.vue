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
import type { Academy, Major } from "@/types/majorModels.ts";

// 定义props
interface Props {
  academies: Academy[]
  modelValue?: Major[] // 选中的专业对象数组
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  academies: () => [],
  modelValue: () => [],
  placeholder: '选择学院专业'
})

const emit = defineEmits<{
  'update:modelValue': [value: Major[]]
}>()

const isOpen = ref(false)

// 检查专业是否被选中
const isMajorSelected = (major: Major) => {
  return props.modelValue.some(selectedMajor =>
      selectedMajor.name === major.name
  )
}

// 检查学院是否部分选中（有些专业选了，有些没选）
const isAcademyIndeterminate = (academy: Academy) => {
  const selectedCount = academy.majors.filter(major =>
      isMajorSelected(major)
  ).length
  return selectedCount > 0 && selectedCount < academy.majors.length
}

// 检查学院是否全部选中
const isAcademyAllSelected = (academy: Academy) => {
  return academy.majors.every(major =>
      isMajorSelected(major)
  )
}

// 处理专业选择
const handleMajorSelect = (major: Major) => {
  const newSelected = [...props.modelValue]
  const index = newSelected.findIndex(selectedMajor =>
      selectedMajor.name === major.name
  )

  if (index > -1) {
    newSelected.splice(index, 1) // 取消选择
  } else {
    newSelected.push(major) // 选择
  }

  emit('update:modelValue', newSelected)
}

// 切换学院所有专业的选择状态
const toggleAcademySelection = (academy: Academy) => {
  const allSelected = isAcademyAllSelected(academy)
  let newSelected = [...props.modelValue]

  if (!allSelected) {
    // 选择所有该学院的专业（去重）
    academy.majors.forEach(major => {
      if (!isMajorSelected(major)) {
        newSelected.push(major)
      }
    })
  } else {
    // 取消选择所有该学院的专业
    newSelected = newSelected.filter(selectedMajor =>
        !academy.majors.some(major => major.name === selectedMajor.name)
    )
  }

  emit('update:modelValue', newSelected)
}

// 显示选中的专业名称
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
        <span class="truncate">{{ selectedMajorsText }}</span>
        <ChevronDownIcon class="h-4 w-4 opacity-50 shrink-0" />
      </Button>
    </DropdownMenuTrigger>

    <DropdownMenuContent class="w-80 max-h-96 overflow-y-auto">
      <DropdownMenuLabel>选择学院和专业</DropdownMenuLabel>
      <DropdownMenuSeparator />

      <DropdownMenuGroup v-for="academy in academies" :key="academy.name">
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
                academy.majors.filter(m => isMajorSelected(m)).length
              }}/{{ academy.majors.length }})
            </span>
          </div>
        </DropdownMenuItem>

        <!-- 专业项 -->
        <DropdownMenuItem
            v-for="major in academy.majors"
            :key="major.name"
            class="pl-8 pr-2 py-1.5 cursor-pointer"
            @select.prevent
            @click="handleMajorSelect(major)"
        >
          <div class="flex items-center space-x-2 w-full">
            <Checkbox
                :model-value="isMajorSelected(major)"
                @click.stop
                @update:model-value="handleMajorSelect(major)"
            />
            <span class="text-sm">{{ major.name }}</span>
          </div>
        </DropdownMenuItem>

        <DropdownMenuSeparator v-if="academy !== academies[academies.length - 1]" />
      </DropdownMenuGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>