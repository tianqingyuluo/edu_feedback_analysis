<!-- AcademyMajorDropdown.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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
import { Checkbox } from '@/components/ui/checkbox'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { ChevronDownIcon } from 'lucide-vue-next'
import type { Academy, Major } from '@/types/majorModels'

/* ---------- props / emits ---------- */
interface Props {
  academies: Academy[]
  modelValue?: Major[]
  placeholder?: string
}
const props = withDefaults(defineProps<Props>(), {
  academies: () => [],
  modelValue: () => [],
  placeholder: '选择学院专业',
})
const emit = defineEmits<{
  'update:modelValue': [value: Major[]]
}>()

/* ---------- 选中逻辑 ---------- */
const isMajorSelected = (major: Major) =>
    props.modelValue.some(m => m.name === major.name)

const isAcademyIndeterminate = (academy: Academy) => {
  const c = academy.majors.filter(isMajorSelected).length
  return c > 0 && c < academy.majors.length
}
const isAcademyAllSelected = (academy: Academy) =>
    academy.majors.every(isMajorSelected)

const toggleAcademySelection = (academy: Academy) => {
  const all = isAcademyAllSelected(academy)

  if (all) {
    const next = props.modelValue.filter(
      m => !academy.majors.some(ma => ma.name === m.name)
    )
    emit('update:modelValue', next)
  } else {
    const allMajors = [...props.modelValue, ...academy.majors]
    const next = allMajors.filter((major, index, array) =>
      array.findIndex(m => m.name === major.name) === index
    )
    emit('update:modelValue', next)
  }
}

const handleMajorSelect = (major: Major) => {
  const idx = props.modelValue.findIndex(m => m.name === major.name)
  const next = [...props.modelValue]
  idx > -1 ? next.splice(idx, 1) : next.push(major)
  emit('update:modelValue', next)
}

/* ---------- 展开状态 ---------- */
const expandedMap = ref<Record<string, boolean>>({})
const toggleExpand = (name: string) => {
  expandedMap.value[name] = !expandedMap.value[name]
}

/* ---------- 默认展开第一个 ---------- */
onMounted(() => {
  if (props.academies.length) expandedMap.value[props.academies[0].name] = true
})

/* ---------- 占位文字 ---------- */
const selectedMajorsText = computed(() =>
    props.modelValue.length
        ? `已选择 ${props.modelValue.length} 个专业`
        : props.placeholder,
)

</script>

<template>
  <DropdownMenu>
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
        <Collapsible v-model:open="expandedMap[academy.name]">
          <!-- 学院行（触发器） -->
          <CollapsibleTrigger as-child>
            <DropdownMenuItem
                class="px-2 py-1.5 cursor-pointer"
                @select.prevent
            >
              <div class="flex items-center justify-between w-full">
                <div class="flex items-center space-x-2">
                  <Checkbox
                      :model-value="isAcademyAllSelected(academy)"
                      :indeterminate="isAcademyIndeterminate(academy)"
                      @click.stop
                      @update:model-value="toggleAcademySelection(academy)"
                  />
                  <span class="font-semibold text-sm">{{ academy.name }}</span>
                  <span class="text-xs text-muted-foreground ml-auto">
                    {{ academy.majors.filter(isMajorSelected).length }}/{{
                      academy.majors.length
                    }}
                  </span>
                </div>

                <!-- 展开箭头 -->
                <button
                    class="p-1 rounded hover:bg-gray-100"
                    @click.stop="toggleExpand(academy.name)"
                >
                  <ChevronDownIcon
                      class="h-4 w-4 transition-transform"
                      :class="{ 'rotate-180': expandedMap[academy.name] }"
                  />
                </button>
              </div>
            </DropdownMenuItem>
          </CollapsibleTrigger>

          <!-- 专业列表（折叠内容） -->
          <CollapsibleContent>
            <div>
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
            </div>
          </CollapsibleContent>
        </Collapsible>

        <DropdownMenuSeparator v-if="academy !== academies[academies.length - 1]" />
      </DropdownMenuGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>