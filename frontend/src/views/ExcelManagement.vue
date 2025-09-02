<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { uploadExcel, getUploadHistory, deleteExcelById } from '../api/excel'
import { ElMessage, ElMessageBox, type UploadInstance, type UploadProps, type UploadRawFile } from 'element-plus'

// 模拟数据（结构与后端一致）
const mockHistoryData = {
  total: 5,
  page: 1,
  size: 10,
  items: [
    { id: 1, filename: '销售数据汇总表.xlsx', size: 2048576, uploaded_at: '2025-08-25T10:30:22Z' },
    { id: 2, filename: '员工考勤记录.xls', size: 845200, uploaded_at: '2025-08-24T15:45:10Z' },
    { id: 3, filename: '月度财务报表.xlsx', size: 3125760, uploaded_at: '2025-08-23T09:12:41Z' },
    { id: 4, filename: '用户反馈数据.csv', size: 512300, uploaded_at: '2025-08-22T17:20:05Z' },
    { id: 5, filename: '库存清单表.xlsx', size: 1340200, uploaded_at: '2025-08-21T11:05:33Z' }
  ]
}

// 分页 & 数据
const historyList = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const deletingId = ref<number | null>(null)

// 上传相关
const uploadRef = ref<UploadInstance>()
const showSuccessDialog = ref(false)
const uploadedFileName = ref('')

// 获取历史记录（失败时使用模拟数据）
const fetchHistory = async () => {
  loading.value = true
  try {
    const res = await getUploadHistory(currentPage.value, pageSize.value)
    
    // ✅ 适配后端结构：{ http_status: 0, message: { total, items } }
    if (res.http_status === 0 && res.message?.items) {
      const data = res.message
      historyList.value = data.items
      total.value = data.total
      console.log('✅ 使用真实数据')
    } else {
      throw new Error('Invalid response format')
    }
  } catch (error) {
    console.warn('⚠️ 获取数据失败，正在使用模拟数据...', error)
    ElMessage.warning('无法连接服务器，已加载示例数据')
    
    // 使用模拟数据并模拟分页
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    const paginatedData = mockHistoryData.items.slice(start, end)
    
    historyList.value = paginatedData
    total.value = mockHistoryData.total
  } finally {
    loading.value = false
  }
}

// 分页切换
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchHistory()
}

// 上传前校验
const beforeUpload: UploadProps['beforeUpload'] = (rawFile: UploadRawFile) => {
  const allowedTypes = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
    'application/csv'
  ]
  const isValidType = allowedTypes.includes(rawFile.type)
  const maxSize = 10 * 1024 * 1024 // 10MB
  const isLt10M = rawFile.size <= maxSize
  
  if (!isValidType) {
    ElMessage.error('仅支持上传 .xls, .xlsx, .csv 格式的文件！')
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB！')
  }
  
  return isValidType && isLt10M
}

// 自定义上传方法
const customUpload: UploadProps['httpRequest'] = async (options) => {
  const { file, onSuccess, onError } = options
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await uploadExcel(formData)
    onSuccess(response.data)
  } catch (err) {
    onError(err as any)
  }
}

// 上传成功回调
const handleUploadSuccess = (response: any, file: File) => {
  uploadedFileName.value = file.name
  showSuccessDialog.value = true
  setTimeout(() => {
    fetchHistory() // 刷新列表
  }, 800)
  ElMessage.success('上传成功')
}

// 删除文件
const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该文件吗？此操作不可恢复', '⚠️ 删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    deletingId.value = id
    await deleteExcelById(id)
    ElMessage.success('删除成功')
    fetchHistory() // 刷新
  } catch (error: any) {
    if (error?.__CANCEL__) {
      ElMessage.info('已取消删除')
    } else {
      ElMessage.error('删除失败')
    }
  } finally {
    deletingId.value = null
  }
}

// 时间格式化（处理 ISO 时间，转为本地时间）
const formatTime = (_row: any, _column: any, cellValue: string) => {
  const date = new Date(cellValue)
  return isNaN(date.getTime()) ? '--' : date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 文件大小格式化
const formatFileSize = (bytes: number): string => {
  if (bytes === 0 || isNaN(bytes)) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 初始化
onMounted(() => {
  fetchHistory()
})
</script>

<template>
<div class="excel-manager-container">
  <h2 class="title">📊 Excel 文件管理</h2>
  
  <!-- 上传区域 -->
  <div class="upload-section">
    <el-upload
        ref="uploadRef"
        :auto-upload="true"
        :show-file-list="false"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :http-request="customUpload"
        accept=".xls,.xlsx,.csv"
    >
      <el-button type="primary" size="large" icon="Upload">上传 Excel 文件</el-button>
      <template #tip>
        <div class="el-upload__tip">
          支持格式：.xls, .xlsx, .csv，单文件不超过 10MB
        </div>
      </template>
    </el-upload>
  </div>
  
  <!-- 历史记录表格 -->
  <div class="history-section">
    <el-table
        :data="historyList"
        stripe
        style="width: 100%;min-height: 800px;"
        :header-cell-style="{ background: '#f0f2f5', color: '#333' }"
        v-loading="loading"
    >
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
      <el-table-column
          prop="uploaded_at"
          label="上传时间"
          width="170"
          :formatter="formatTime"
      />
      <el-table-column label="文件大小" width="120">
        <template #default="scope">
          {{ formatFileSize(scope.row.size) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="scope">
          <el-button
              size="small"
              type="danger"
              icon="Delete"
              circle
              @click="handleDelete(scope.row.id)"
              :loading="deletingId === scope.row.id"
          />
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
          @current-change="handlePageChange"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next, jumper"
          background
      />
    </div>
  </div>
  
  <!-- 提示对话框 -->
  <el-dialog v-model="showSuccessDialog" title="✅ 上传成功" width="30%">
    <p>文件 <strong>{{ uploadedFileName }}</strong> 上传成功！</p>
    <p>正在刷新列表...</p>
  </el-dialog>
</div>
</template>

<style scoped>
.excel-manager-container {
  max-width: 850px;
  margin: 40px auto;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  font-family: 'Helvetica Neue', Arial, sans-serif;
  min-height: 1000px;
}

.title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 25px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.upload-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  border: 2px dashed #d9ecff;
  border-radius: 10px;
  background-color: #f8fafd;
  transition: border-color 0.3s;
}

.upload-section:hover {
  border-color: #409eff;
}

.el-upload__tip {
  color: #999;
  font-size: 13px;
  margin-top: 8px;
}

.history-section {
  margin-top: 20px;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .excel-manager-container {
    padding: 20px;
    margin: 15px;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .el-table :deep(td, th) {
    padding: 8px 0;
  }
}
</style>