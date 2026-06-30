<template>
  <div class="page-container">
    <el-card>
      <h2>{{ title }}</h2>
      <p>此模块正在开发中...</p>
    </el-card>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '页面' }
})
</script>

<style scoped>
.page-container { padding: 20px; }
</style>
