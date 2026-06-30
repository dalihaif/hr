<template>
  <div class="page-container">
    <el-card>
      <h2>绩效管理</h2>
      <p>此模块正在开发中...</p>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <el-card shadow="hover">
            <el-statistic title="本月待考核" :value="15">
              <template #suffix>人</template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <el-statistic title="已完成考核" :value="142">
              <template #suffix>人</template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <el-statistic title="平均得分" :value="87.5">
              <template #suffix>分</template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>

      <el-alert
        title="提示"
        type="info"
        description="绩效管理模块完整功能正在开发中,包括考核指标设置、评分录入、绩效统计等功能。"
        show-icon
        style="margin-top: 20px;"
      />
    </el-card>
  </div>
</template>

<script setup>
// 绩效管理页面 - 待完善
</script>

<style scoped>
.page-container { padding: 20px; }
</style>
