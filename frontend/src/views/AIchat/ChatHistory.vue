<template>
  <aside class="history-panel">
    <div class="head">
      <span>历史对话</span>
      <button class="new-btn" @click="$emit('new')">+ 新建</button>
    </div>

    <ul>
      <li
          v-for="h in historyList"
          :key="h.id"
          :class="{ active: h.id === currentId }"
          @click="selectSession(h.id)"
      >
        <span class="title-text">{{ h.title }}</span>

        <!-- 三个点下拉菜单 -->
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <button
                class="dots"
                @click.stop
                aria-label="更多操作"
            >
              <MoreHorizontal class="w-4 h-4" />
            </button>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end" class="w-32">
            <DropdownMenuItem @click="rename(h.id, h.title)">重命名</DropdownMenuItem>
            <DropdownMenuItem @click="del(h.id)" class="text-red-600">删除</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </li>
    </ul>
  </aside>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from '@/components/ui/dropdown-menu'
import { MoreHorizontal } from 'lucide-vue-next'

defineEmits<{ new: [] }>()

const historyList = inject<HistoryItem[]>('historyList')!
const currentId = inject<string>('currentId')!
const selectSession = inject<(id: string) => void>('selectSession')!

/* 重命名：prompt 简易版，后续可换弹窗 */
const rename = (id: string, oldTitle: string) => {
  const newTitle = prompt('请输入新标题', oldTitle)?.trim()
  if (!newTitle) return
  const idx = historyList.findIndex(i => i.id === id)
  if (idx > -1) historyList[idx].title = newTitle
}

/* 删除 */
const del = (id: string) => {
  const idx = historyList.findIndex(i => i.id === id)
  if (idx > -1) historyList.splice(idx, 1)
  /* 如果删的是当前会话，父级可监听 historyList 变化做兜底，这里简化 */
}
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  font-weight: 600;
  border-bottom: 1px solid #e5e5e5;
}
.new-btn {
  padding: 4px 10px;
  font-size: 13px;
  border: 1px solid #0969da;
  color: #0969da;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.new-btn:hover {
  background: #0969da;
  color: #fff;
}
ul {
  flex: 1;
  margin: 0;
  padding: 8px;
  list-style: none;
  overflow-y: auto;
}
li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 6px;
  cursor: pointer;
}
li:hover {
  background: #f2f2f2;
}
li.active {
  background: #e6f4ff;
  color: #0969da;
}
.title-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.dots {
  margin-left: 8px;
  padding: 4px;
  border-radius: 4px;
  color: #666;
  background: transparent;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.dots:hover {
  background: #e5e5e5;
}
</style>