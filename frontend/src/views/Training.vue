<template>
  <div class="page-container">
    <el-card>
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 培训计划 -->
        <el-tab-pane label="培训计划" name="plans">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddPlan">
              <el-icon><Plus /></el-icon>创建培训计划
            </el-button>
          </div>

          <el-table :data="plans" border stripe v-loading="loading">
            <el-table-column prop="title" label="培训标题" width="200" />
            <el-table-column prop="training_type" label="培训类型" width="120" />
            <el-table-column prop="trainer" label="培训师" width="120" />
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column prop="location" label="地点" width="150" />
            <el-table-column label="参与人数" width="120">
              <template #default="{ row }">
                {{ row.enrolled_count }}/{{ row.max_participants }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getPlanStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="viewEnrollments(row.id)">查看报名</el-button>
                <el-button size="small" type="danger" @click="cancelPlan(row.id)">取消</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 我的培训 -->
        <el-tab-pane label="我的培训" name="myTraining">
          <el-table :data="myEnrollments" border stripe>
            <el-table-column prop="plan_title" label="培训名称" width="200" />
            <el-table-column prop="training_type" label="类型" width="120" />
            <el-table-column prop="start_date" label="开始时间" width="120" />
            <el-table-column prop="location" label="地点" width="150" />
            <el-table-column prop="enrollment_status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.enrollment_status === '已参加' ? 'success' : ''">
                  {{ row.enrollment_status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="成绩" width="80" />
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="enrollPlan(row.plan_id)" 
                  v-if="row.enrollment_status !== '已报名'">
                  报名参加
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 培训档案 -->
        <el-tab-pane label="培训档案" name="records">
          <el-form :inline="true" class="search-form">
            <el-form-item label="职工姓名">
              <el-input v-model="recordFilter.emp_name" placeholder="请输入" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadRecords">查询</el-button>
              <el-button @click="handleAddRecord">录入记录</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="records" border stripe>
            <el-table-column prop="emp_name" label="职工姓名" width="120" />
            <el-table-column prop="emp_no" label="工号" width="120" />
            <el-table-column prop="training_name" label="培训名称" width="200" />
            <el-table-column prop="training_type" label="类型" width="120" />
            <el-table-column prop="training_date" label="培训日期" width="120" />
            <el-table-column prop="hours" label="学时" width="80" />
            <el-table-column prop="score" label="成绩" width="80" />
            <el-table-column prop="certificate_no" label="证书编号" width="150" />
          </el-table>
        </el-tab-pane>

        <!-- 统计分析 -->
        <el-tab-pane label="统计分析" name="statistics">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>培训计划统计</template>
                <div v-for="stat in planStats" :key="stat.status" style="margin-bottom: 10px;">
                  <el-progress 
                    :percentage="getPlanPercentage(stat)" 
                    :format="() => `${stat.status}: ${stat.count}个`" 
                  />
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>培训概况</template>
                <el-statistic title="人均培训时长" :value="avgHours">
                  <template #suffix>小时</template>
                </el-statistic>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 创建培训计划对话框 -->
    <el-dialog v-model="planDialogVisible" title="创建培训计划" width="600px">
      <el-form :model="planForm" label-width="100px">
        <el-form-item label="培训标题" required>
          <el-input v-model="planForm.title" />
        </el-form-item>
        <el-form-item label="培训类型">
          <el-select v-model="planForm.training_type">
            <el-option label="内部培训" value="内部培训" />
            <el-option label="外部培训" value="外部培训" />
            <el-option label="在线学习" value="在线学习" />
          </el-select>
        </el-form-item>
        <el-form-item label="培训师">
          <el-input v-model="planForm.trainer" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="planForm.start_date" type="date" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="planForm.end_date" type="date" />
        </el-form-item>
        <el-form-item label="培训地点">
          <el-input v-model="planForm.location" />
        </el-form-item>
        <el-form-item label="最大人数">
          <el-input-number v-model="planForm.max_participants" :min="1" />
        </el-form-item>
        <el-form-item label="培训说明">
          <el-input v-model="planForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPlan">确定</el-button>
      </template>
    </el-dialog>

    <!-- 录入培训记录对话框 -->
    <el-dialog v-model="recordDialogVisible" title="录入培训记录" width="600px">
      <el-form :model="recordForm" label-width="100px">
        <el-form-item label="职工ID" required>
          <el-input v-model="recordForm.emp_id" />
        </el-form-item>
        <el-form-item label="培训名称" required>
          <el-input v-model="recordForm.training_name" />
        </el-form-item>
        <el-form-item label="培训类型">
          <el-select v-model="recordForm.training_type">
            <el-option label="内部培训" value="内部培训" />
            <el-option label="外部培训" value="外部培训" />
            <el-option label="在线学习" value="在线学习" />
          </el-select>
        </el-form-item>
        <el-form-item label="培训日期">
          <el-date-picker v-model="recordForm.training_date" type="date" />
        </el-form-item>
        <el-form-item label="学时">
          <el-input-number v-model="recordForm.hours" :min="0" :step="0.5" />
        </el-form-item>
        <el-form-item label="成绩">
          <el-input-number v-model="recordForm.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="证书编号">
          <el-input v-model="recordForm.certificate_no" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="recordForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRecord">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('plans')
const loading = ref(false)

// 培训计划
const plans = ref([])
const planDialogVisible = ref(false)
const planForm = reactive({
  title: '',
  training_type: '',
  trainer: '',
  start_date: '',
  end_date: '',
  location: '',
  max_participants: 30,
  description: ''
})

// 我的培训
const myEnrollments = ref([])

// 培训档案
const records = ref([])
const recordFilter = reactive({ emp_name: '' })
const recordDialogVisible = ref(false)
const recordForm = reactive({
  emp_id: '',
  training_name: '',
  training_type: '',
  training_date: '',
  hours: 0,
  score: 0,
  certificate_no: '',
  description: ''
})

// 统计数据
const planStats = ref([])
const avgHours = ref(0)

// 加载培训计划
const loadPlans = async () => {
  try {
    const response = await request.get('/training/plans')
    plans.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载我的培训
const loadMyEnrollments = async () => {
  try {
    const response = await request.get('/training/enrollments')
    myEnrollments.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载培训档案
const loadRecords = async () => {
  try {
    const params = {}
    if (recordFilter.emp_name) params.emp_name = recordFilter.emp_name
    const response = await request.get('/training/records', { params })
    records.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await request.get('/training/statistics')
    planStats.value = response.plans || []
    avgHours.value = response.avg_training_hours || 0
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 创建培训计划
const handleAddPlan = () => {
  Object.assign(planForm, {
    title: '',
    training_type: '',
    trainer: '',
    start_date: '',
    end_date: '',
    location: '',
    max_participants: 30,
    description: ''
  })
  planDialogVisible.value = true
}

// 提交培训计划
const submitPlan = async () => {
  try {
    await request.post('/training/plans', planForm)
    ElMessage.success('培训计划创建成功')
    planDialogVisible.value = false
    loadPlans()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 取消培训计划
const cancelPlan = async (id) => {
  try {
    await request.delete(`/training/plans/${id}`)
    ElMessage.success('计划已取消')
    loadPlans()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 查看报名
const viewEnrollments = (planId) => {
  activeTab.value = 'myTraining'
  // 实际应该过滤显示该计划的报名
}

// 报名参加
const enrollPlan = async (planId) => {
  try {
    await request.post('/training/enroll', { plan_id: planId })
    ElMessage.success('报名成功')
    loadMyEnrollments()
  } catch (error) {
    ElMessage.error('报名失败,可能已报名')
  }
}

// 录入培训记录
const handleAddRecord = () => {
  Object.assign(recordForm, {
    emp_id: '',
    training_name: '',
    training_type: '',
    training_date: '',
    hours: 0,
    score: 0,
    certificate_no: '',
    description: ''
  })
  recordDialogVisible.value = true
}

// 提交培训记录
const submitRecord = async () => {
  try {
    await request.post('/training/records', recordForm)
    ElMessage.success('记录录入成功')
    recordDialogVisible.value = false
    loadRecords()
  } catch (error) {
    ElMessage.error('录入失败')
  }
}

// 辅助函数
const getPlanStatusType = (status) => {
  const map = { '计划中': '', '进行中': 'warning', '已完成': 'success', '已取消': 'info' }
  return map[status] || ''
}

const getPlanPercentage = (stat) => {
  const total = planStats.value.reduce((sum, s) => sum + s.count, 0)
  return total > 0 ? Math.round(stat.count / total * 100) : 0
}

onMounted(() => {
  loadPlans()
  loadMyEnrollments()
  loadRecords()
  loadStatistics()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 20px; }
.search-form { margin-bottom: 20px; }
</style>
