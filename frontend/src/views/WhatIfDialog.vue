<script setup lang="ts">
import { reactive, watch } from 'vue'
import WhatIfSlider from '@/components/layout/WhatIfSlider.vue'
import {Button} from "@/components/ui/button";

/* ---------- 接口类型 ---------- */
interface FeatureItem {
  feature_name: string
  feature_classes: number
}

/* ---------- 模拟后端数据 ---------- */
const features: FeatureItem[] = [
  { feature_name: '教室设备满意度', feature_classes: 5 },
  { feature_name: '体育设施满意度', feature_classes: 5 },
  { feature_name: '宿舍条件满意度', feature_classes: 5 },
  { feature_name: '实训室满意度', feature_classes: 5 },
  { feature_name: '一站式服务', feature_classes: 5 },
  { feature_name: '网络资源满意度', feature_classes: 5 },
  { feature_name: '职业规划满意度', feature_classes: 5 },
  { feature_name: '学业指导满意度', feature_classes: 5 },
  { feature_name: '图书馆满意度', feature_classes: 5 },
  { feature_name: '心理健康满意度', feature_classes: 5 },
  { feature_name: '体育教育满意度', feature_classes: 5 },
  { feature_name: '思政课质量满意度', feature_classes: 5 },
  { feature_name: '教师总体满意度', feature_classes: 5 },
  { feature_name: '劳动教育满意度', feature_classes: 5 },
  { feature_name: '教师履职满意度', feature_classes: 5 },
  { feature_name: '思政课总体满意度', feature_classes: 5 },
  { feature_name: '实习场地满意度', feature_classes: 5 },
  { feature_name: '激发学习兴趣', feature_classes: 5 },
  { feature_name: '思政课内容满意度', feature_classes: 5 },
  { feature_name: '美育教育满意度', feature_classes: 5 },
]

/* ---------- 表单数据 ---------- */
const form = reactive<Record<string, number>>({})

/* 初始化：全部取中间值 */
watch(
    () => features,
    () => {
      features.forEach(f => {
        form[f.feature_name] = Math.ceil(f.feature_classes / 2)
      })
    },
    { immediate: true }
)

/* ---------- 提交 ---------- */
function handleSubmit() {
  console.log('提交给后端的数据:', form)
  // axios.post('/api/whatif', form)
}
</script>

<template>
  <!-- 白色底框容器 -->
  <div class="min-h-screen bg-gray-50">
    <div class="mx-auto max-w-4xl bg-white rounded-xl shadow p-6">
      <h1 class="text-xl font-bold mb-4">满意度 What-if 模拟</h1>

      <!-- 滑动条列表 -->
      <div class="grid gap-4">
        <WhatIfSlider
            v-for="f in features"
            :key="f.feature_name"
            :label="f.feature_name"
            :max="f.feature_classes"
            v-model="form[f.feature_name]"
        />
      </div>

      <!-- 完成按钮：右侧 -->
      <div class="mt-6 flex justify-end">
        <Button class="btn-primary" @click="handleSubmit">完成</Button>
      </div>
    </div>
  </div>
</template>