<!-- MetricDropdown.vue -->
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
import type { Metric, MetricGroup } from "@/types/metricModels.ts";

// 定义props
interface Props {
  metricGroups: MetricGroup[]
  modelValue?: Metric[] // 选中的指标对象数组
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  metricGroups: () => [],
  modelValue: () => [],
  placeholder: '选择指标'
})

const emit = defineEmits<{
  'update:modelValue': [value: Metric[]]
}>()

const isOpen = ref(false)

// 检查指标是否被选中
const isMetricSelected = (metric: Metric) => {
  return props.modelValue.some(selectedMetric =>
      selectedMetric.name === metric.name
  )
}

// 检查组是否部分选中（有些指标选了，有些没选）
const isGroupIndeterminate = (group: MetricGroup) => {
  const selectedCount = group.metrics.filter(metric =>
      isMetricSelected(metric)
  ).length
  return selectedCount > 0 && selectedCount < group.metrics.length
}

// 检查组是否全部选中
const isGroupAllSelected = (group: MetricGroup) => {
  return group.metrics.every(metric =>
      isMetricSelected(metric)
  )
}

// 处理指标选择
const handleMetricSelect = (metric: Metric) => {
  const newSelected = [...props.modelValue]
  const index = newSelected.findIndex(selectedMetric =>
      selectedMetric.name === metric.name
  )

  if (index > -1) {
    newSelected.splice(index, 1) // 取消选择
  } else {
    newSelected.push({ ...metric }) // 选择（创建新对象避免引用问题）
  }

  emit('update:modelValue', newSelected)
}

// 切换组所有指标的选择状态
const toggleGroupSelection = (group: MetricGroup) => {
  const allSelected = isGroupAllSelected(group)
  let newSelected = [...props.modelValue]

  if (!allSelected) {
    // 选择所有该组的指标（去重）
    group.metrics.forEach(metric => {
      if (!isMetricSelected(metric)) {
        newSelected.push({ ...metric }) // 创建新对象
      }
    })
  } else {
    // 取消选择所有该组的指标
    newSelected = newSelected.filter(selectedMetric =>
        !group.metrics.some(metric => metric.name === selectedMetric.name)
    )
  }

  emit('update:modelValue', newSelected)
}

// 显示选中的指标名称
const selectedMetricsText = computed(() => {
  if (props.modelValue.length === 0) {
    return props.placeholder
  }

  if (props.modelValue.length === 1) {
    return props.modelValue[0].name
  }

  return `已选择 ${props.modelValue.length} 个指标`
})

// 获取选中指标的统计信息（可选）
const selectedMetricsStats = computed(() => {
  return props.modelValue.map(metric => ({
    name: metric.name,
    dataPoints: metric.data.length,
    latestValue: metric.data.length > 0 ? metric.data[metric.data.length - 1] : null
  }))
})
</script>

<template>
  <DropdownMenu v-model:open="isOpen">
    <DropdownMenuTrigger as-child>
      <Button variant="outline" class="w-full justify-between">
        <span class="truncate">{{ selectedMetricsText }}</span>
        <ChevronDownIcon class="h-4 w-4 opacity-50 shrink-0" />
      </Button>
    </DropdownMenuTrigger>

    <DropdownMenuContent class="w-80 max-h-96 overflow-y-auto">
      <DropdownMenuLabel>选择指标</DropdownMenuLabel>
      <DropdownMenuSeparator />

      <DropdownMenuGroup v-for="group in metricGroups" :key="group.name">
        <!-- 组项（可点击选择全部） -->
        <DropdownMenuItem
            class="px-2 py-1.5 cursor-pointer"
            @select.prevent
            @click="toggleGroupSelection(group)"
        >
          <div class="flex items-center space-x-2 w-full">
            <Checkbox
                :model-value="isGroupAllSelected(group)"
                :indeterminate="isGroupIndeterminate(group)"
                @click.stop
                @update:model-value="toggleGroupSelection(group)"
            />
            <span class="font-semibold text-sm">{{ group.name }}</span>
            <span class="text-xs text-muted-foreground ml-auto">
              ({{
                group.metrics.filter(m => isMetricSelected(m)).length
              }}/{{ group.metrics.length }})
            </span>
          </div>
        </DropdownMenuItem>

        <!-- 指标项 -->
        <DropdownMenuItem
            v-for="metric in group.metrics"
            :key="metric.name"
            class="pl-8 pr-2 py-1.5 cursor-pointer"
            @select.prevent
            @click="handleMetricSelect(metric)"
        >
          <div class="flex items-center space-x-2 w-full">
            <Checkbox
                :model-value="isMetricSelected(metric)"
                @click.stop
                @update:model-value="handleMetricSelect(metric)"
            />
            <div class="flex flex-col">
              <span class="text-sm">{{ metric.name }}</span>
            </div>
          </div>
        </DropdownMenuItem>

        <DropdownMenuSeparator v-if="group !== metricGroups[metricGroups.length - 1]" />
      </DropdownMenuGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>