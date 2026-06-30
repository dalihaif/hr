<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" :color="stat.color">
              <component :is="stat.icon" />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card class="quick-actions" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>快捷操作</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="12" :sm="8" :md="4" v-for="action in quickActions" :key="action.title">
          <div class="action-item" @click="handleAction(action.path)">
            <el-icon :size="30" color="#409EFF">
              <component :is="action.icon" />
            </el-icon>
            <div class="action-title">{{ action.title }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近动态 -->
    <el-card class="recent-activities" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近动态</span>
        </div>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="activity in activities"
          :key="activity.id"
          :timestamp="activity.time"
          placement="top"
        >
          <el-card>
            <h4>{{ activity.title }}</h4>
            <p>{{ activity.content }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Money, TrendCharts, Calendar } from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref([
  { title: '在职职工', value: 156, icon: User, color: '#409EFF' },
  { title: '本月工资', value: '¥128万', icon: Money, color: '#67C23A' },
  { title: '待审批', value: 8, icon: TrendCharts, color: '#E6A23C' },
  { title: '今日考勤', value: '98%', icon: Calendar, color: '#F56C6C' }
])

const quickActions = [
  { title: '职工管理', icon: 'User', path: '/employees' },
  { title: '工资管理', icon: 'Money', path: '/salary' },
  { title: '招聘管理', icon: 'Briefcase', path: '/recruitment' },
  { title: '培训管理', icon: 'Reading', path: '/training' },
  { title: '离职管理', icon: 'SwitchButton', path: '/resignation' },
  { title: '数据备份', icon: 'FolderOpened', path: '/backup' }
]

const activities = ref([
  { id: 1, title: '新职工入职', content: '张三明天办理入职手续', time: '2026-06-29 14:30' },
  { id: 2, title: '工资发放', content: '6月份工资已生成', time: '2026-06-29 10:00' },
  { id: 3, title: '培训计划', content: '心肺复苏技能培训报名中', time: '2026-06-28 16:00' },
  { id: 4, title: '离职申请', content: '李四提交离职申请', time: '2026-06-28 09:30' }
])

const handleAction = (path) => {
  router.push(path)
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  font-weight: bold;
}

.action-item {
  text-align: center;
  padding: 20px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
}

.action-item:hover {
  background-color: #f5f7fa;
  transform: translateY(-5px);
}

.action-title {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .stat-value {
    font-size: 24px;
  }
  
  .action-item {
    padding: 15px;
  }
}
</style>
