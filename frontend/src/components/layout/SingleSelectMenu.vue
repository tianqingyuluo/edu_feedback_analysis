<!-- AcademyMajorSingleDropdown.vue -->
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
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
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
  modelValue?: Major
  placeholder?: string
}
const props = withDefaults(defineProps<Props>(), {
  academies: () => [],
  placeholder: '选择学院专业',
})
const emit = defineEmits<{
  'update:modelValue': [value: Major | undefined]
}>()

/* ---------- 选中逻辑 ---------- */
const selectedMajor = computed(() => props.modelValue)

const handleMajorSelect = (major: Major) => {
  emit('update:modelValue', major)
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
const selectedText = computed(() =>
    selectedMajor.value ? selectedMajor.value.name : props.placeholder,
)
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" class="w-full justify-between">
        <span class="truncate">{{ selectedText }}</span>
        <ChevronDownIcon class="h-4 w-4 opacity-50 shrink-0" />
      </Button>
    </DropdownMenuTrigger>

    <DropdownMenuContent class="w-80 max-h-96 overflow-y-auto">
      <DropdownMenuLabel>选择学院和专业（单选）</DropdownMenuLabel>
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
                <span class="font-semibold text-sm">{{ academy.name }}</span>

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
            <RadioGroup
                :model-value="selectedMajor?.name"
                @update:model-value="
                (name) => {
                  const found = academies
                    .flatMap((a) => a.majors)
                    .find((m) => m.name === name)
                  if (found) handleMajorSelect(found)
                }
              "
            >
              <div
                  v-for="major in academy.majors"
                  :key="major.name"
                  class="pl-8 pr-2 py-1.5 cursor-pointer flex items-center space-x-2"
              >
                <RadioGroupItem :value="major.name" :id="major.name" />
                <label
                    :for="major.name"
                    class="text-sm cursor-pointer flex-1"
                >
                  {{ major.name }}
                </label>
              </div>
            </RadioGroup>
          </CollapsibleContent>
        </Collapsible>

        <DropdownMenuSeparator
            v-if="academy !== academies[academies.length - 1]"
        />
      </DropdownMenuGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>