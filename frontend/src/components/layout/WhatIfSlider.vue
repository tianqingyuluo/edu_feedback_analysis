<script setup lang="ts">
import { ref, watch } from 'vue'
import { Slider } from '@/components/ui/slider'

const props = withDefaults(
    defineProps<{
      label: string
      max: number
      modelValue: number        // 1..max
    }>(),
    { max: 5, modelValue: 3 }
)
const emit = defineEmits<{
  'update:modelValue': [v: number]
}>()

/* 内部 0-based */
const internal = ref([props.modelValue - 1])
watch(internal, ([v]) => emit('update:modelValue', v + 1), { immediate: true })
watch(() => props.modelValue, v => { internal.value = [v - 1] })
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="text-sm font-medium text-gray-700">{{ label }}</div>

    <!-- 两端文字 -->
    <div class="flex justify-between px-1 text-xs text-gray-400">
      <span>非常不满意</span>
      <span>非常满意</span>
    </div>

    <!-- 刻度竖线 + Slider -->
    <div class="relative w-full h-6">
      <!-- 刻度竖线 -->
      <div
          class="absolute top-0 left-0 right-0 h-full flex justify-between
               text-blue-500 text-xs pointer-events-none"
      >
        <span v-for="i in max" :key="i">|</span>
      </div>

      <!-- Radix Slider（只允许刻度整数） -->
      <Slider
          v-model="internal"
          :max="max - 1"
          :step="1"
          class="absolute top-2 left-0 w-full"
      />
    </div>
  </div>
</template>