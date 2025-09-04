<!-- components/layout/BubbleMetricDropdown.vue -->
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
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import type { Metric, MetricGroup } from '@/types/Metric.ts'

const props = defineProps<{
  metricGroups: MetricGroup[]
  modelValue?: Metric[]
  placeholder?: string
}>()
const emit = defineEmits<{
  'update:modelValue': [value: Metric[]]
}>()

const expandedMap = ref<Record<string, boolean>>({})
props.metricGroups.forEach(group => {
  expandedMap.value[group.name] = false
})

const isMetricSelected = (metric: Metric) =>
    props.modelValue?.some(m => m.name === metric.name) || false

const handleMetricSelect = (metric: Metric) => {
  const currentSelected = props.modelValue ? [...props.modelValue] : []
  const index = currentSelected.findIndex(m => m.name === metric.name)
  if (index > -1) {
    currentSelected.splice(index, 1)
  } else {
    currentSelected.push(metric)
  }
  emit('update:modelValue', currentSelected)
}

const isGroupAllSelected = (group: MetricGroup) =>
    group.metrics.every(isMetricSelected) && group.metrics.length > 0

const isGroupIndeterminate = (group: MetricGroup) =>
    !isGroupAllSelected(group) && group.metrics.some(isMetricSelected)

const toggleGroupSelection = (group: MetricGroup) => {
  let currentSelected = props.modelValue ? [...props.modelValue] : []
  const allSelected = isGroupAllSelected(group)
  if (allSelected) {
    currentSelected = currentSelected.filter(
        selectedMetric => !group.metrics.some(groupMetric => groupMetric.name === selectedMetric.name)
    )
  } else {
    group.metrics.forEach(groupMetric => {
      if (!isMetricSelected(groupMetric)) {
        currentSelected.push(groupMetric)
      }
    })
  }
  emit('update:modelValue', currentSelected)
}

const selectedText = computed(() => {
  if (!props.modelValue || props.modelValue.length === 0) return props.placeholder || '选择专业'
  return `已选择 ${props.modelValue.length} 个专业`
})
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" class="w-full justify-between pr-2">
        <span class="truncate">{{ selectedText }}</span>
        <ChevronDownIcon class="h-4 w-4 opacity-50 shrink-0" />
      </Button>
    </DropdownMenuTrigger>

    <DropdownMenuContent class="w-80 max-h-96 overflow-y-auto">
      <DropdownMenuLabel>选择学院与专业</DropdownMenuLabel>
      <DropdownMenuSeparator />

      <DropdownMenuGroup v-for="group in metricGroups" :key="group.name">
        <Collapsible v-model:open="expandedMap[group.name]">
          <!-- 学院行 -->
          <CollapsibleTrigger as-child>
            <DropdownMenuItem class="px-2 py-1.5 cursor-pointer" @select.prevent @click.stop>
              <div class="flex items-center justify-between w-full">
                <div class="flex items-center space-x-2">
                  <!-- ✅ 受控写法 -->
                  <Checkbox
                      :model-value="isGroupAllSelected(group)"
                      :indeterminate="isGroupIndeterminate(group)"
                      @click.stop.prevent="toggleGroupSelection(group)"
                  />
                  <span class="font-semibold text-sm">{{ group.name }}</span>
                </div>
                <span class="text-xs text-muted-foreground ml-auto flex items-center gap-1">
                  {{ group.metrics.filter(isMetricSelected).length }}/{{ group.metrics.length }}
                  <ChevronDownIcon
                      :class="{ 'rotate-180': expandedMap[group.name] }"
                      class="h-4 w-4 transition-transform"
                  />
                </span>
              </div>
            </DropdownMenuItem>
          </CollapsibleTrigger>

          <!-- 专业列表 -->
          <CollapsibleContent>
            <DropdownMenuItem
                v-for="metric in group.metrics"
                :key="metric.name"
                class="pl-8 pr-2 py-1.5 cursor-pointer"
                @select.prevent
                @click.prevent="handleMetricSelect(metric)"
            >
              <div class="flex items-center space-x-2 w-full">
                <!-- ✅ 受控写法 -->
                <Checkbox
                    :model-value="isMetricSelected(metric)"
                    @update:model-value="handleMetricSelect(metric)"
                />
                <span class="text-sm">{{ metric.name }}</span>
                <span class="text-xs text-muted-foreground ml-auto">
                  人数:{{ metric.data[2] }}
                </span>
              </div>
            </DropdownMenuItem>
          </CollapsibleContent>
        </Collapsible>

        <DropdownMenuSeparator v-if="group !== metricGroups[metricGroups.length - 1]" />
      </DropdownMenuGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>