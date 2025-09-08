<script setup lang="ts">
import Demo1 from '@/Test/component/demo1.vue'
import Demo2 from '@/Test/component/Demo2(柱状图方差累计贡献).vue'
import Demo3 from '@/Test/component/Demo3(肘部法轮廓系数).vue'
import Demo4 from '@/Test/component/Demo4(学生类型柱状图).vue'
import Demo5 from '@/Test/component/Demo5(二维主成分影响图).vue'
import Demo6 from '@/Test/component/Demo6(三维主成分影响图).vue'
import Demo7 from '@/Test/component/Demo7(各个方面的满意度).vue'
import Demo8 from '@/Test/component/Demo8(热力图).vue'
import Demo9 from '@/Test/component/Demo9(整体满意度).vue'
import Demo10 from '@/Test/component/Demo10(整体满意分布).vue'
import Demo11 from '@/Test/component/Demo11(满意度贡献值).vue'
</script>

<template>
<!-- 根容器，通常包含全局布局（如导航栏、页脚） -->
<div id="app">
  <Demo1/>
  <Demo2/>
  <Demo3/>

  <Demo4/>
  <Demo5/>
  <Demo6/>
  
  <Demo7/>
  <Demo8/>
  
  <Demo9/>
  <Demo10/>
  <Demo11/>
  <!--    <router-view/>-->
</div>
</template>
