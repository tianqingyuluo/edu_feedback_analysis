<script setup lang="ts">
import {onMounted, reactive, ref, watch} from 'vue'
import WhatIfSlider from '@/components/layout/WhatIfSlider.vue'
import {Button} from "@/components/ui/button";
import type {FeatureItem, whatIfResponse} from "@/types/whatIf.ts";
import WhatIfService from '@/api/whatIf.ts'

interface Props {
  dataid: string;
  taskid: string;
}
const props = defineProps<Props>();

/* ---------- 状态管理 ---------- */
const features = ref<FeatureItem[]>([])
const loading = ref(false)
const dataLoading = ref(true) // 新增：数据加载状态
const result = ref<whatIfResponse | null>(null)
const error = ref<string | null>(null)
const useMockData = ref(true)

const generateMockResult = (formData: Record<string, number>): whatIfResponse => {
  const totalScore = Object.values(formData).reduce((sum, score) => sum + score, 0)
  const avgScore = totalScore / Object.keys(formData).length
  const predictedClass = Math.min(5, Math.max(1, Math.round(avgScore)))

  // 使用字符串形式的评分作为 key
  const probabilities: Record<string, number> = {}
  for (let i = 1; i <= 5; i++) {
    const distance = Math.abs(avgScore - i)
    probabilities[String(i)] = Math.max(0, 1 - distance / 5)
  }

  // 归一化概率
  const totalProb = Object.values(probabilities).reduce((sum, prob) => sum + prob, 0)
  Object.keys(probabilities).forEach(key => {
    probabilities[key] = probabilities[key] / totalProb
  })

  // 构建 top_k_classes，class_label 也是字符串评分
  const topKClasses = Object.entries(probabilities)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([class_label, probability]) => ({
        class_label,
        probability
      }))

  return {
    prediction: {
      predicted_class: predictedClass,
      probabilities,
      top_k_classes: topKClasses
    },
    metadata: {
      timestamp: new Date().toISOString()
    }
  }
}
/* ---------- 数据加载 ---------- */
onMounted(async () =>{
  console.log(props.dataid,props.taskid)
  dataLoading.value = true
  try {
    // const response = await WhatIfService.getWhatIfPrediction(props.dataid, props.taskid)
    const response= [
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
    console.log('原始数据',response)
    features.value = response
    console.log('特征数据加载完成:', features.value)
  } catch (err) {
    console.error('特征数据加载失败:', err)
    error.value = '特征数据加载失败，请刷新重试'
  } finally {
    dataLoading.value = false
  }
})

/* ---------- 表单数据 ---------- */
const form = reactive<Record<string, number>>({})

/* 初始化：全部取中间值 */
watch(
    () => features.value,
    (newFeatures) => {
      if (!Array.isArray(newFeatures)) return   // ← 关键保护
      newFeatures.forEach(f => {
        form[f.feature_name] = Math.ceil(f.feature_classes / 2)
      })
    },
    { immediate: true, deep: true }
)

/* ---------- 提交 ---------- */
async function handleSubmit() {
  loading.value = true
  error.value = null
  result.value = null

  try {
    const formDataArray = features.value.map(feature => ({
      feature_name: feature.feature_name,
      feature_classes: form[feature.feature_name]
    }))
    console.log('提交给后端的数据:', form)

    if (useMockData.value) {
      console.log(JSON.stringify({
        features: formDataArray,
        task_id: props.taskid
      }, null, 2))
      await new Promise(resolve => setTimeout(resolve, 1500))
      result.value = generateMockResult(form)
      console.log('假数据预测结果:', result.value)
    } else {
      const response = await WhatIfService.executeWhatIf({
        features: formDataArray,
        task_id: props.taskid
      })
      result.value = response
      console.log('真实API预测结果:', response)
    }
  } catch (err) {
    console.error('提交失败:', err)
    error.value = '提交失败，请联系工作人员'
  } finally {
    loading.value = false
  }
}

// 重置表单
function resetForm() {
  features.value.forEach(f => {
    form[f.feature_name] = Math.ceil(f.feature_classes / 2)
  })
  result.value = null
  error.value = null
}

const getSatisfactionLabel = (score: number): string => {
  const labels = {
    1: '非常不满意',
    2: '比较不满意',
    3: '一般',
    4: '比较满意',
    5: '非常满意'
  }
  return labels[score as keyof typeof labels] || `评分 ${score}`
}
</script>

<template>
  <!-- 白色底框容器 -->
  <div class="min-h-screen bg-gray-50">
    <div class="mx-auto max-w-4xl bg-white rounded-xl shadow p-6">
      <!-- 数据加载状态 -->
      <div v-if="dataLoading" class="flex flex-col items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <span class="text-blue-600 text-lg">正在加载特征数据...</span>
        <p class="text-gray-500 mt-2">请稍候</p>
      </div>

      <!-- 数据加载错误 -->
      <div v-else-if="error && !dataLoading" class="py-8 text-center">
        <div class="text-red-600 text-lg mb-2">数据加载失败</div>
        <p class="text-gray-600 mb-4">{{ error }}</p>
      </div>

      <!-- 主要内容 -->
      <div v-else>
        <!-- 顶部控制栏 -->
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-xl font-bold">满意度 What-if 模拟</h1>
          <div class="flex items-center space-x-4">
            <Button
                variant="outline"
                @click="resetForm"
                :disabled="loading"
            >
              重置
            </Button>
          </div>
        </div>

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
        <div class="mt-6 flex justify-end space-x-3">
          <Button
              variant="outline"
              @click="resetForm"
              :disabled="loading"
          >
            重置
          </Button>
          <Button
              class="btn-primary"
              @click="handleSubmit"
              :disabled="loading"
          >
            <span v-if="loading" class="flex items-center">
              预测中...
            </span>
            <span v-else>开始预测</span>
          </Button>
        </div>

        <!-- 预测加载状态 -->
        <div v-if="loading" class="mt-6 p-4 bg-blue-50 rounded-lg">
          <div class="flex items-center justify-center">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
            <span class="text-blue-600">
              {{ useMockData ? '模拟预测中...' : '正在请求预测，请稍候...' }}
            </span>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center">
            <span class="text-red-600">{{ error }}</span>
          </div>
        </div>

        <!-- 预测结果 -->
        <div v-if="result" class="mt-6 p-6 bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg">
          <div class="flex justify-between items-start mb-4">
            <h2 class="text-lg font-semibold text-green-800">预测结果</h2>
          </div>

          <div class="mb-6 p-4 bg-white rounded-lg border">
            <h3 class="font-medium text-gray-700 mb-2">总体满意度预测</h3>
            <div class="flex items-center space-x-4">
              <div class="text-3xl font-bold text-green-600">
                {{ getSatisfactionLabel(result.prediction?.predicted_class) }}
              </div>
              <div class="text-sm text-gray-500">
                (预测评分: {{ result.prediction?.predicted_class }}/5)
              </div>
            </div>
          </div>

          <!-- 概率分布 -->
          <div class="mb-6">
            <h3 class="font-medium text-gray-700 mb-3">满意度概率分布</h3>
            <div class="space-y-3">
              <div
                  v-for="i in 5"
                  :key="i"
                  class="bg-white p-3 rounded-lg border"
              >
                <div class="flex justify-between items-center mb-2">
                  <span class="font-medium text-gray-700">{{ getSatisfactionLabel(i) }}</span>
                  <span class="font-bold text-green-600">
                    {{ ((result.prediction?.probabilities?.[String(i)] || 0) * 100).toFixed(1) }}%
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                      class="bg-green-500 h-2 rounded-full transition-all duration-500"
                      :style="{ width: `${(result.prediction?.probabilities?.[String(i)] || 0) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Top K 类别 -->
          <div v-if="result.prediction?.top_k_classes?.length" class="mb-4">
            <h3 class="font-medium text-gray-700 mb-3">Top 预测结果</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div
                  v-for="(item, index) in result.prediction.top_k_classes"
                  :key="index"
                  class="bg-white p-3 rounded-lg border text-center"
                  :class="{
                      'ring-2 ring-green-500': index === 0,
                      'opacity-90': index === 1,
                      'opacity-80': index === 2
                  }"
              >
                <div class="text-2xl font-bold text-green-600 mb-1">
                  {{ (item.probability * 100).toFixed(1) }}%
                </div>
                <div class="text-sm text-gray-600">{{ getSatisfactionLabel (Number(item.class_label)) }}</div>
              </div>
            </div>
          </div>

          <!-- 元数据 -->
          <div class="mt-6 pt-4 border-t border-gray-200">
            <div class="text-xs text-gray-500 space-y-1">
              <div>预测时间: {{ new Date(result.metadata?.timestamp).toLocaleString() }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>