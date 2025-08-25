<script setup>
import { ref } from 'vue'
import ScoreGradientCard from "@/components/layout/ScoreGradientCard.vue"
import TextImageCard from "@/components/layout/TextImageCard.vue" // 导入新组件

const cardList = ref([
  { title: "总体满意度", score1: 4.2, score2: 5.0, conclusion: "上升12%" },
  { title: "任务完成率", score1: 8.5, score2: 10.0, conclusion: "下降3%" },
  { title: "响应速度", score1: 3.7, score2: 5.0, conclusion: "上升5%" },
  { title: "用户留存率", score1: 86.4, score2: 100.0, conclusion: "持平" }
])

const imageCards = ref([
  {
    text: "满意度趋势",
    imageUrl: "https://img95.699pic.com/element/40203/7897.png_300.png"
  },
  {
    text: "各学院评分对比",
    imageUrl: "https://img95.699pic.com/element/40203/7897.png_300.png"
  },
  {
    text: "课程类型分布",
    imageUrl: "https://img95.699pic.com/element/40203/7897.png_300.png"
  },
  {
    text: "相关性分析",
    imageUrl: "https://img95.699pic.com/element/40203/7897.png_300.png"
  }
])
</script>

<template>
  <div class="p-4 bg-gray-100 space-y-6"> <!-- 增加垂直间距 -->
    <div class="mx-auto max-w-[1800px] space-y-6"> <!-- 内部增加间距 -->

      <!-- 指标看板 -->
      <div class="min-h-[200px] rounded-lg shadow-md p-4 bg-white">
        <h2 class="text-xl font-semibold mb-4">指标看板</h2>
        <div class="flex flex-wrap gap-4">
          <div
              v-for="(card, index) in cardList"
              :key="'metric-'+index"
              class="w-[400px] flex-1"
          >
            <ScoreGradientCard
                :title="card.title"
                :score1="card.score1"
                :score2="card.score2"
                :conclusion="card.conclusion"
            />
          </div>
        </div>
      </div>

      <!-- 新增的图片卡片区域 -->
      <div class="min-h-[200px] rounded-lg shadow-md p-4 bg-white">
        <h2 class="text-xl font-semibold mb-4">功能展示</h2>
        <div class="flex flex-wrap gap-4">
          <div
              v-for="(card, index) in imageCards"
              :key="'image-'+index"
              class="min-w-[300px] flex-1"
          >
            <TextImageCard
                :text="card.text"
                :imageUrl="card.imageUrl"
            />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>