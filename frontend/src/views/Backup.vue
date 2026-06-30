<template>
  <div class="page-container">
    <el-card>
      <h2>数据备份</h2>
      <el-button type="primary" @click="handleBackup">创建备份</el-button>
      <el-table :data="backups" border style="margin-top: 20px;">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="size_mb" label="大小(MB)" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="handleDownload(row)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const backups = ref([])

const loadBackups = async () => {
  try {
    const response = await request.get('/backup/list')
    backups.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

const handleBackup = async () => {
  try {
    await request.post('/backup/create', { type: 'full' })
    ElMessage.success('备份成功')
    loadBackups()
  } catch (error) {
    ElMessage.error('备份失败')
  }
}

const handleDownload = (row) => {
  window.open(`/api/backup/download/${row.filename}`)
}

onMounted(() => {
  loadBackups()
})
</script>

<style scoped>
.page-container { padding: 20px; }
</style>
