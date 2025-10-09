<script setup lang="ts">
import type { DocItem } from '@/types/document'
import { Button } from '@/components/ui/button'
import { ElMessageBox } from 'element-plus'

interface Props {
  list: DocItem[]
  loading: boolean
  page: number
  totalPages: number
}
const props = defineProps<Props>()

const emit = defineEmits<{
  upload: [file: File]
  remove: [id: string]          // 正常删除
  removeFailed: [id: string]    // 仅用于上传失败文件
  changePage: [page: number]
}>()

function onUpload(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  emit('upload', file)
  target.value = ''
}

async function onRemove(row: DocItem) {
  await ElMessageBox.confirm(`确定删除 ${row.filename}？`, '提示')
  emit('remove', row.id)
}

/** 上传失败文件：单独按钮，无需二次确认 */
function onRemoveFailed(row: DocItem) {
  emit('removeFailed', row.id)
}
function statusText(s: string): string {
  switch (s) {
    case 'processed': return '已处理'
    case 'uploaded':  return '上传中'
    case 'error':     return '上传失败'
    default:          return s
  }
}
</script>

<template>
  <div class="bg-white rounded shadow overflow-hidden">
    <!-- 工具栏 -->
    <div class="px-6 py-3 border-b flex justify-between items-center">
      <span class="text-sm text-gray-600">共 {{ list.length }} 条</span>
      <label>
        <div class="relative inline-block">
          <input
              type="file"
              accept=".pdf,.txt,.csv,.docx,.doc"
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              @change="onUpload"
          />
          <Button size="sm">添加文档</Button>
        </div>
      </label>
    </div>

    <!-- 表格 -->
    <div class="divide-y">
      <div v-if="loading" class="px-6 py-10 text-center text-gray-400">加载中...</div>
      <div v-else-if="!list.length" class="px-6 py-10 text-center text-gray-400">暂无文档</div>

      <div v-for="r in list" :key="r.id" class="px-6 py-3 grid grid-cols-12 gap-4 text-sm items-center">
        <!-- 文件名 -->
        <div class="col-span-4 truncate" :title="r.filename">{{ r.filename }}</div>

        <!-- 大小 -->
        <div class="col-span-2">{{ (r.file_size / 1024).toFixed(2) }} KB</div>

        <!-- 上传时间 -->
        <div class="col-span-3">{{ new Date(r.uploaded_at).toLocaleString('zh-CN') }}</div>

        <!-- 状态 -->
        <div class="col-span-2">
          <!-- 其余状态保持原色 -->
          <span class="px-2 py-0.5 text-xs rounded" :class="{
              'bg-green-100 text-green-700': r.status==='processed',
              'bg-yellow-100 text-yellow-700': r.status==='uploaded',
              'bg-red-100 text-red-700': r.status==='error'
            }">{{ statusText(r.status) }}</span>
        </div>

        <!-- 操作 -->
        <div class="col-span-1 flex justify-end gap-1">
          <!-- 上传中：无按钮 -->
          <template v-if="r.status==='uploaded'" />

          <!-- 上传失败：独立红色删除按钮 -->
          <Button
              v-else-if="r.status==='error'"
              variant="destructive"
              @click="onRemoveFailed(r)"
          >
            删除
          </Button>
          <!-- 其他状态：正常删除 -->
          <Button
              v-else
              variant="destructive"
              @click="onRemove(r)"
          >
            删除
          </Button>
        </div>
      </div>
    </div>
    <!-- 分页 -->
    <div class="px-6 py-3 border-t flex justify-end items-center gap-2">
      <Button :disabled="page===1" @click="emit('changePage',page-1)">上一页</Button>
      <span class="text-xs text-gray-600">{{ page }} / {{ totalPages }}</span>
      <Button :disabled="page===totalPages" @click="emit('changePage',page+1)">下一页</Button>
    </div>
  </div>
</template>