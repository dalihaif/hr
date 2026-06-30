<template>
  <div class="page-container">
    <el-card>
      <h2>工资管理</h2>
      <p>此模块正在开发中...</p>
      <el-button type="primary" @click="handleGeneratePDF">生成工资条PDF</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const handleGeneratePDF = async () => {
  try {
    const response = await request.post('/salary/slips/generate', {
      month: '2026-06'
    }, { responseType: 'blob' })
    
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `工资条_2026-06.pdf`)
    link.click()
    ElMessage.success('工资条生成成功')
  } catch (error) {
    ElMessage.error('生成失败')
  }
}
</script>

<style scoped>
.page-container { padding: 20px; }
</style>
