<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useUploadStore } from '@/store/uploadStore'
import { Button } from '@/components/ui/button'
import { onMounted, ref } from 'vue'
import { Progress } from '@/components/ui/progress'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {useRoutesStore} from "@/store/routeStore.ts";
import {useUserStore} from "@/store/userStore.ts";
const router = useRouter()
/* ---------- store ---------- */
const store = useUploadStore()
const routeStore = useRoutesStore()
const { items, total, page, size, loading, error, analyzedList } = storeToRefs(store)
const userStore = useUserStore()
const userRole = userStore.userInfo?.role ?? 'ADMIN'

/* 分页 */
function prev() {
  if (page.value > 1) store.changePage(page.value - 1)
}
function next() {
  if (page.value < Math.ceil(total.value / size.value)) store.changePage(page.value + 1)
}

async function handleAnalyze(id: string) {
  await store.startAnalyze(id)
}
/* 查看按钮 */
function handleSelect(dataId: string) {
  const taskId = store.getTaskIdByDataId(dataId)
  if (!taskId) {
    ElMessage.warning('暂无对应的分析任务')
    return
  }

  const row = store.items.find(it => it.id === dataId)
  if (!row) return

  const routeName = row.filename.replace(/\.[^.]+$/, '')
  const routePath = `/admin/report/${taskId}/${dataId}`

  routeStore.addRoute(routePath, routeName)

  router.push(`/admin/report/${taskId}/${dataId}`)
}

/* 首次加载 */
onMounted(() => store.fetchPage())

function handleFailReason(id: string) {
  console.log('TODO 查看失败原因', id)
  // 后续可弹窗 / 跳详情 / 调接口拿失败信息
}
</script>
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- 加载 -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      <span class="ml-3 text-gray-600">加载中...</span>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {{ error }}
      <Button size="sm" variant="destructive" class="ml-4" @click="store.fetchPage()">重试</Button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!items.length" class="bg-white rounded-lg shadow p-8 text-center text-gray-500">
      暂无上传记录
    </div>

    <!-- 表格 -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider border-b grid grid-cols-12 gap-4">
        <div class="col-span-5">文件名</div>
        <div class="col-span-2">大小</div>
        <div class="col-span-3">上传时间</div>
        <div class="col-span-1">状态</div>
        <div class="col-span-1">操作</div>
      </div>

      <div class="divide-y divide-gray-200">
        <div v-for="r in items" :key="r.id" class="px-6 py-4 grid grid-cols-12 gap-4 items-center text-sm">
          <!-- 文件名 -->
          <div class="col-span-5 font-medium text-gray-900 truncate" :title="r.filename">{{ r.filename }}</div>
          <!-- 大小 -->
          <div class="col-span-2 text-gray-600">{{ (r.size / 1024).toFixed(2) }} KB</div>
          <!-- 上传时间 -->
          <div class="col-span-3 text-gray-600">{{ new Date(r.uploaded_at).toLocaleString('zh-CN') }}</div>
          <!-- 状态 -->
          <div class="col-span-1">
            <span v-if="r.status==='已分析'"   class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">已分析</span>
            <span v-else-if="r.status==='分析中'" class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">分析中</span>
            <span v-else-if="r.status==='分析失败'" class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">分析失败</span>
            <span v-else-if="r.status==='等待中'" class="px-2 py-1 bg-purple-100 text-purple-400 text-xs rounded-full">等待中</span>
            <span v-else class="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">未分析</span>
          </div>
          <!-- 操作 -->
          <!-- 操作 -->
          <div class="col-span-1 flex items-center justify-end gap-2 h-10">
            <!-- 未分析 -->
            <Button
                v-if="r.status==='未分析'"
                class="h-10 px-4"
                :disabled="userRole === 'USER'"
            @click="handleAnalyze(r.id)"
            >分析</Button>

            <Progress
                v-else-if="r.status==='分析中'"
                :model-value="r.progress ?? 0"
                class="w-full"
            />

            <!-- 分析失败：查看原因 -->
            <Button
                v-else-if="r.status==='分析失败'"
                size="sm"
                variant="destructive"
                @click="handleFailReason(r.id)"
            >查看原因</Button>
            <span v-else-if="r.status==='等待中'" class="px-2 py-1 text-xs">等待处理</span>
            <!-- 已分析：查看结果 -->
            <a
                v-else
                class="h-10 flex items-center text-blue-600 hover:text-blue-800 underline cursor-pointer"
                @click="handleSelect(r.id)"
            >查看</a>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="flex justify-end items-center gap-2 px-6 py-4 border-t">
        <Button size="sm" :disabled="page===1" @click="prev">上一页</Button>
        <span class="text-sm text-gray-600">{{ page }} / {{ Math.ceil(total/size) }}</span>
        <Button size="sm" :disabled="page>=Math.ceil(total/size)" @click="next">下一页</Button>
      </div>
    </div>
  </div>
</template>