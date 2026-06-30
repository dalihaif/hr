<template>
  <div class="page-container">
    <el-card>
      <h2>考勤管理</h2>
      <p>此模块正在开发中...</p>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="今日出勤率" :value="98">
              <template #suffix>%</template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="请假申请" :value="5">
              <template #suffix>个</template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="加班申请" :value="8">
              <template #suffix>个</template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="异常考勤" :value="3">
              <template #suffix>条</template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>

      <el-alert
        title="提示"
        type="info"
        description="考勤管理模块完整功能正在开发中,包括请假申请、加班申请、考勤统计等功能。"
        show-icon
        style="margin-top: 20px;"
      />
    </el-card>
  </div>
</template>

<script setup>
// 考勤管理页面 - 待完善
</script>

<style scoped>
.page-container { padding: 20px; }
</style>
