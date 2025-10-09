<script setup lang="ts">
import { onMounted } from 'vue'
import type {DocItem} from "@/types/document.ts";
import DocList from '@/components/layout/DocList.vue'
import { useDocStore } from '@/store/useDocStore'
import {ElMessage} from "element-plus";

const store = useDocStore()
onMounted(async () => {
  await store.fetchDocs()
  const { ready,kb } = await store.initKnowledgeBase()

})

function handleRemoveFailedLocal(id: string) {
  store.docs = store.docs.filter(d => d.id !== id)
  store.total--
}
</script>

<template>
  <div class="container mx-auto p-6">
    <h1 class="text-2xl font-semibold mb-4">知识库文档管理</h1>
    <DocList
        :list="store.docs"
        :loading="store.loading"
        :page="store.page"
        :total-pages="store.totalPages"
        @upload="store.addDoc"
        @remove="store.removeDoc"
        @change-page="store.changePage"
        @remove-failed="handleRemoveFailedLocal"
    />
  </div>
</template>