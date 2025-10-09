<script setup lang="ts">
import { marked } from 'marked'
import markedKatex from 'marked-katex-extension'   // ① 扩展
import DOMPurify from 'dompurify'
import { ref, watchEffect } from 'vue'
import 'katex/dist/katex.min.css'

/* 把扩展注册到 marked */
marked.use(markedKatex({
  throwOnError: false,   // 公式写错也不抛错
  output: 'html'         // 输出 HTML
}))

const props = defineProps<{ content: string }>()
const html = ref('')

watchEffect(async () => {
  const raw = await marked.parse(props.content, { breaks: true })
  html.value = DOMPurify.sanitize(raw)
})
</script>

<template>
  <div class="bubble assistant" v-html="html"></div>
</template>