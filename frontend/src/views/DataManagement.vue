<template>
  <div id="app" class="container mx-auto px-4 py-8">
    <!-- 表格容器 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="flex justify-end p-4">
        <button
            @click="handleAddReport"
            class="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
        >
          添加报告
        </button>
      </div>

      <!-- 表格 -->
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">报告名称</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">生成时间</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
        </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="(report, index) in reports" :key="report.id">
          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ report.name }}</td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(report.date) }}</td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            <button
                @click="handleDelete(report)"
                class="px-4 py-2 bg-red-500 text-white text-xs rounded hover:bg-red-600 transition-colors"
            >
              删除
            </button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 假数据
const reports = ref([
  { id: 1, name: '2023年财务报告', date: new Date('2023-12-15') },
  { id: 2, name: '季度销售分析', date: new Date('2023-11-20') },
  { id: 3, name: '用户行为分析报告', date: new Date('2023-10-05') },
  { id: 4, name: '市场调研报告', date: new Date('2023-09-12') },
  { id: 5, name: '产品性能测试报告', date: new Date('2023-08-28') }
]);

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// 删除处理函数
const handleDelete = (report) => {
  console.log('删除报告:', report);
  // 在实际应用中，这里会调用API进行删除
  // 这里我们只做前端演示，将报告从列表中移除
  reports.value = reports.value.filter(r => r.id !== report.id);
  alert(`已删除报告: ${report.name}`);
};

// 添加报告处理函数
const handleAddReport = () => {
  console.log('添加报告');
  // 在实际应用中，这里会打开一个表单或模态框让用户输入报告信息
  // 这里我们只是演示，添加一个假的新报告
  const newReport = {
    id: reports.value.length ? Math.max(...reports.value.map(r => r.id)) + 1 : 1,
    name: `新添加报告 ${new Date().toLocaleTimeString()}`,
    date: new Date()
  };
  reports.value.push(newReport);
  alert(`已添加新报告: ${newReport.name}`);
};
</script>