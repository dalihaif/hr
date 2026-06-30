<template>
  <div class="page-container">
    <el-card>
      <!-- Tab切换 -->
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 岗位管理 -->
        <el-tab-pane label="岗位管理" name="positions">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddPosition">
              <el-icon><Plus /></el-icon>发布岗位
            </el-button>
          </div>

          <el-table :data="positions" border stripe v-loading="loading">
            <el-table-column prop="position_name" label="岗位名称" width="150" />
            <el-table-column prop="department" label="科室" width="120" />
            <el-table-column prop="headcount" label="招聘人数" width="100" />
            <el-table-column prop="hired_count" label="已录用" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="deadline" label="截止日期" width="120" />
            <el-table-column label="操作" fixed="right" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="viewApplicants(row.id)">查看应聘者</el-button>
                <el-button size="small" type="danger" @click="closePosition(row.id)">关闭</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 应聘者管理 -->
        <el-tab-pane label="应聘者管理" name="applicants">
          <el-form :inline="true" class="search-form">
            <el-form-item label="岗位">
              <el-select v-model="applicantFilter.position_id" placeholder="请选择" clearable>
                <el-option
                  v-for="pos in positions"
                  :key="pos.id"
                  :label="pos.position_name"
                  :value="pos.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="applicantFilter.status" placeholder="请选择" clearable>
                <el-option label="待筛选" value="待筛选" />
                <el-option label="初试" value="初试" />
                <el-option label="复试" value="复试" />
                <el-option label="录用" value="录用" />
                <el-option label="拒绝" value="拒绝" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadApplicants">查询</el-button>
              <el-button @click="handleAddApplicant">录入应聘者</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="applicants" border stripe v-loading="loading">
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="gender" label="性别" width="80" />
            <el-table-column prop="education" label="学历" width="100" />
            <el-table-column prop="major" label="专业" width="150" />
            <el-table-column prop="experience_years" label="工作年限" width="100" />
            <el-table-column prop="position_name" label="应聘岗位" width="150" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getApplicantStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="250">
              <template #default="{ row }">
                <el-button size="small" @click="updateApplicantStatus(row)">更新状态</el-button>
                <el-button size="small" type="primary" @click="addInterview(row)">面试记录</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 面试记录 -->
        <el-tab-pane label="面试记录" name="interviews">
          <el-table :data="interviews" border stripe>
            <el-table-column prop="applicant_name" label="应聘者" width="120" />
            <el-table-column prop="interview_type" label="面试类型" width="100" />
            <el-table-column prop="interviewer_name" label="面试官" width="120" />
            <el-table-column prop="interview_date" label="面试时间" width="180" />
            <el-table-column prop="score" label="评分" width="80" />
            <el-table-column prop="result" label="结果" width="100">
              <template #default="{ row }">
                <el-tag :type="row.result === '通过' ? 'success' : 'danger'">{{ row.result }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="comments" label="评价" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>

        <!-- 统计分析 -->
        <el-tab-pane label="统计分析" name="statistics">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>岗位状态统计</template>
                <div v-for="stat in positionStats" :key="stat.status" style="margin-bottom: 10px;">
                  <el-progress :percentage="getPositionPercentage(stat)" :format="() => `${stat.status}: ${stat.count}个`" />
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>应聘者状态统计</template>
                <div v-for="stat in applicantStats" :key="stat.status" style="margin-bottom: 10px;">
                  <el-progress :percentage="getApplicantPercentage(stat)" :format="() => `${stat.status}: ${stat.count}人`" />
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新增岗位对话框 -->
    <el-dialog v-model="positionDialogVisible" title="发布招聘岗位" width="600px">
      <el-form :model="positionForm" label-width="100px">
        <el-form-item label="岗位名称" required>
          <el-input v-model="positionForm.position_name" />
        </el-form-item>
        <el-form-item label="科室" required>
          <el-select v-model="positionForm.department">
            <el-option label="内科" value="内科" />
            <el-option label="外科" value="外科" />
            <el-option label="护理部" value="护理部" />
            <el-option label="医技科" value="医技科" />
          </el-select>
        </el-form-item>
        <el-form-item label="招聘人数">
          <el-input-number v-model="positionForm.headcount" :min="1" />
        </el-form-item>
        <el-form-item label="岗位要求">
          <el-input v-model="positionForm.requirements" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="发布日期">
          <el-date-picker v-model="positionForm.publish_date" type="date" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="positionForm.deadline" type="date" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="positionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPosition">确定</el-button>
      </template>
    </el-dialog>

    <!-- 录入应聘者对话框 -->
    <el-dialog v-model="applicantDialogVisible" title="录入应聘者" width="600px">
      <el-form :model="applicantForm" label-width="100px">
        <el-form-item label="应聘岗位" required>
          <el-select v-model="applicantForm.position_id">
            <el-option
              v-for="pos in positions"
              :key="pos.id"
              :label="pos.position_name"
              :value="pos.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="applicantForm.name" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="applicantForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="applicantForm.birth_date" type="date" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="applicantForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="applicantForm.email" />
        </el-form-item>
        <el-form-item label="学历">
          <el-select v-model="applicantForm.education">
            <el-option label="大专" value="大专" />
            <el-option label="本科" value="本科" />
            <el-option label="硕士" value="硕士" />
            <el-option label="博士" value="博士" />
          </el-select>
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="applicantForm.major" />
        </el-form-item>
        <el-form-item label="工作年限">
          <el-input-number v-model="applicantForm.experience_years" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="applicantDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApplicant">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('positions')
const loading = ref(false)

// 岗位数据
const positions = ref([])
const positionDialogVisible = ref(false)
const positionForm = reactive({
  position_name: '',
  department: '',
  headcount: 1,
  requirements: '',
  publish_date: '',
  deadline: ''
})

// 应聘者数据
const applicants = ref([])
const applicantFilter = reactive({
  position_id: '',
  status: ''
})
const applicantDialogVisible = ref(false)
const applicantForm = reactive({
  position_id: '',
  name: '',
  gender: '男',
  birth_date: '',
  phone: '',
  email: '',
  education: '',
  major: '',
  experience_years: 0
})

// 面试数据
const interviews = ref([])

// 统计数据
const positionStats = ref([])
const applicantStats = ref([])

// 加载岗位列表
const loadPositions = async () => {
  try {
    const response = await request.get('/recruitment/positions')
    positions.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载应聘者列表
const loadApplicants = async () => {
  loading.value = true
  try {
    const params = {}
    if (applicantFilter.position_id) params.position_id = applicantFilter.position_id
    if (applicantFilter.status) params.status = applicantFilter.status
    
    const response = await request.get('/recruitment/applicants', { params })
    applicants.value = response
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载面试记录
const loadInterviews = async () => {
  try {
    const response = await request.get('/recruitment/interviews')
    interviews.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await request.get('/recruitment/statistics')
    positionStats.value = response.positions || []
    applicantStats.value = response.applicants || []
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 新增岗位
const handleAddPosition = () => {
  Object.assign(positionForm, {
    position_name: '',
    department: '',
    headcount: 1,
    requirements: '',
    publish_date: '',
    deadline: ''
  })
  positionDialogVisible.value = true
}

// 提交岗位
const submitPosition = async () => {
  try {
    await request.post('/recruitment/positions', positionForm)
    ElMessage.success('岗位发布成功')
    positionDialogVisible.value = false
    loadPositions()
  } catch (error) {
    ElMessage.error('发布失败')
  }
}

// 关闭岗位
const closePosition = async (id) => {
  try {
    await request.delete(`/recruitment/positions/${id}`)
    ElMessage.success('岗位已关闭')
    loadPositions()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 查看应聘者
const viewApplicants = (positionId) => {
  applicantFilter.position_id = positionId
  activeTab.value = 'applicants'
  loadApplicants()
}

// 录入应聘者
const handleAddApplicant = () => {
  Object.assign(applicantForm, {
    position_id: '',
    name: '',
    gender: '男',
    birth_date: '',
    phone: '',
    email: '',
    education: '',
    major: '',
    experience_years: 0
  })
  applicantDialogVisible.value = true
}

// 提交应聘者
const submitApplicant = async () => {
  try {
    await request.post('/recruitment/applicants', applicantForm)
    ElMessage.success('录入成功')
    applicantDialogVisible.value = false
    loadApplicants()
  } catch (error) {
    ElMessage.error('录入失败')
  }
}

// 更新应聘者状态
const updateApplicantStatus = async (row) => {
  // 简化版,实际应该弹出选择框
  const newStatus = prompt('请输入新状态(待筛选/初试/复试/录用/拒绝):', row.status)
  if (newStatus) {
    try {
      await request.put(`/recruitment/applicants/${row.id}`, { status: newStatus })
      ElMessage.success('状态更新成功')
      loadApplicants()
    } catch (error) {
      ElMessage.error('更新失败')
    }
  }
}

// 添加面试记录
const addInterview = (applicant) => {
  const score = prompt('请输入面试评分(0-100):', '85')
  const result = confirm('是否通过?') ? '通过' : '不通过'
  
  if (score) {
    request.post('/recruitment/interviews', {
      applicant_id: applicant.id,
      interview_type: '初试',
      interview_date: new Date().toISOString().slice(0, 19).replace('T', ' '),
      score: parseFloat(score),
      result: result,
      comments: '面试评价'
    }).then(() => {
      ElMessage.success('面试记录已添加')
      loadInterviews()
    })
  }
}

// 辅助函数
const getStatusType = (status) => {
  const map = { '招聘中': 'success', '已招满': 'warning', '已关闭': 'info' }
  return map[status] || ''
}

const getApplicantStatusType = (status) => {
  const map = { '待筛选': '', '初试': 'warning', '复试': 'primary', '录用': 'success', '拒绝': 'danger' }
  return map[status] || ''
}

const getPositionPercentage = (stat) => {
  const total = positionStats.value.reduce((sum, s) => sum + s.count, 0)
  return total > 0 ? Math.round(stat.count / total * 100) : 0
}

const getApplicantPercentage = (stat) => {
  const total = applicantStats.value.reduce((sum, s) => sum + s.count, 0)
  return total > 0 ? Math.round(stat.count / total * 100) : 0
}

onMounted(() => {
  loadPositions()
  loadApplicants()
  loadInterviews()
  loadStatistics()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 20px; }
.search-form { margin-bottom: 20px; }
</style>
