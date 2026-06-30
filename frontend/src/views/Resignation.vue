<template>
  <div class="page-container">
    <el-card>
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 离职申请 -->
        <el-tab-pane label="离职申请" name="requests">
          <div class="toolbar">
            <el-button type="primary" @click="handleSubmitRequest">
              <el-icon><Plus /></el-icon>提交离职申请
            </el-button>
          </div>

          <el-table :data="requests" border stripe v-loading="loading">
            <el-table-column prop="emp_name" label="职工姓名" width="120" />
            <el-table-column prop="emp_no" label="工号" width="120" />
            <el-table-column prop="current_dept" label="科室" width="120" />
            <el-table-column prop="resignation_type" label="离职类型" width="120" />
            <el-table-column prop="apply_date" label="申请日期" width="120" />
            <el-table-column prop="expected_last_day" label="预计最后工作日" width="150" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="250">
              <template #default="{ row }">
                <el-button size="small" type="success" @click="approveRequest(row.id, true)" 
                  v-if="row.status === '待审批'">
                  批准
                </el-button>
                <el-button size="small" type="danger" @click="approveRequest(row.id, false)" 
                  v-if="row.status === '待审批'">
                  拒绝
                </el-button>
                <el-button size="small" @click="viewHandover(row.id)">交接清单</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 交接清单 -->
        <el-tab-pane label="交接清单" name="handover">
          <el-form :inline="true" class="search-form">
            <el-form-item label="申请ID">
              <el-input v-model="handoverFilter.resignation_id" placeholder="请输入" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadHandovers">查询</el-button>
              <el-button @click="handleAddHandover">添加交接项</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="handovers" border stripe>
            <el-table-column prop="item_name" label="交接项目" width="200" />
            <el-table-column prop="item_type" label="类型" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '已完成' ? 'success' : 'warning'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="handler_name" label="接收人" width="120" />
            <el-table-column prop="completed_at" label="完成时间" width="180" />
            <el-table-column prop="remarks" label="备注" show-overflow-tooltip />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="completeHandover(row.id)" 
                  v-if="row.status !== '已完成'">
                  完成
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 离职档案 -->
        <el-tab-pane label="离职档案" name="records">
          <el-table :data="resignationRecords" border stripe>
            <el-table-column prop="emp_name" label="职工姓名" width="120" />
            <el-table-column prop="emp_no" label="工号" width="120" />
            <el-table-column prop="resignation_type" label="离职类型" width="120" />
            <el-table-column prop="last_working_day" label="最后工作日" width="120" />
            <el-table-column prop="final_salary" label="最终工资" width="120">
              <template #default="{ row }">
                ¥{{ row.final_salary?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="handover_completed" label="交接完成" width="100">
              <template #default="{ row }">
                <el-tag :type="row.handover_completed ? 'success' : 'info'">
                  {{ row.handover_completed ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="exit_interview_notes" label="离职面谈记录" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>

        <!-- 统计分析 -->
        <el-tab-pane label="统计分析" name="statistics">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>离职类型分布</template>
                <div v-for="stat in typeStats" :key="stat.resignation_type" style="margin-bottom: 10px;">
                  <el-progress 
                    :percentage="getTypePercentage(stat)" 
                    :format="() => `${stat.resignation_type}: ${stat.count}人`" 
                  />
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>离职率统计</template>
                <el-statistic title="年度离职率" :value="turnoverRate">
                  <template #suffix>%</template>
                </el-statistic>
                <div style="margin-top: 20px;">
                  <p>离职人数: {{ resignedCount }} 人</p>
                  <p>在职人数: {{ totalEmployees }} 人</p>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 提交离职申请对话框 -->
    <el-dialog v-model="requestDialogVisible" title="提交离职申请" width="600px">
      <el-form :model="requestForm" label-width="120px">
        <el-form-item label="职工ID" required>
          <el-input v-model="requestForm.emp_id" />
        </el-form-item>
        <el-form-item label="离职类型" required>
          <el-select v-model="requestForm.resignation_type">
            <el-option label="主动辞职" value="主动辞职" />
            <el-option label="合同到期" value="合同到期" />
            <el-option label="辞退" value="辞退" />
            <el-option label="退休" value="退休" />
          </el-select>
        </el-form-item>
        <el-form-item label="离职原因">
          <el-input v-model="requestForm.reason" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="申请日期">
          <el-date-picker v-model="requestForm.apply_date" type="date" />
        </el-form-item>
        <el-form-item label="预计最后工作日">
          <el-date-picker v-model="requestForm.expected_last_day" type="date" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="requestDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRequest">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加交接项对话框 -->
    <el-dialog v-model="handoverDialogVisible" title="添加交接项" width="600px">
      <el-form :model="handoverForm" label-width="100px">
        <el-form-item label="申请ID" required>
          <el-input v-model="handoverForm.resignation_id" />
        </el-form-item>
        <el-form-item label="交接项目" required>
          <el-input v-model="handoverForm.item_name" />
        </el-form-item>
        <el-form-item label="项目类型">
          <el-select v-model="handoverForm.item_type">
            <el-option label="工作文档" value="工作文档" />
            <el-option label="设备" value="设备" />
            <el-option label="账号" value="账号" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="接收人ID">
          <el-input v-model="handoverForm.handler_id" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="handoverForm.remarks" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handoverDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitHandover">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('requests')
const loading = ref(false)

// 离职申请
const requests = ref([])
const requestDialogVisible = ref(false)
const requestForm = reactive({
  emp_id: '',
  resignation_type: '',
  reason: '',
  apply_date: '',
  expected_last_day: ''
})

// 交接清单
const handovers = ref([])
const handoverFilter = reactive({ resignation_id: '' })
const handoverDialogVisible = ref(false)
const handoverForm = reactive({
  resignation_id: '',
  item_name: '',
  item_type: '',
  handler_id: '',
  remarks: ''
})

// 离职档案
const resignationRecords = ref([])

// 统计数据
const typeStats = ref([])
const turnoverRate = ref(0)
const resignedCount = ref(0)
const totalEmployees = ref(0)

// 加载离职申请
const loadRequests = async () => {
  loading.value = true
  try {
    const response = await request.get('/resignation/requests')
    requests.value = response
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载交接清单
const loadHandovers = async () => {
  try {
    const params = {}
    if (handoverFilter.resignation_id) params.resignation_id = handoverFilter.resignation_id
    const response = await request.get('/resignation/handover', { params })
    handovers.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载离职档案
const loadRecords = async () => {
  try {
    const response = await request.get('/resignation/records')
    resignationRecords.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await request.get('/resignation/statistics')
    typeStats.value = response.types || []
    turnoverRate.value = response.turnover_rate || 0
    resignedCount.value = response.resigned_count || 0
    totalEmployees.value = response.total_employees || 0
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 提交离职申请
const handleSubmitRequest = () => {
  Object.assign(requestForm, {
    emp_id: '',
    resignation_type: '',
    reason: '',
    apply_date: '',
    expected_last_day: ''
  })
  requestDialogVisible.value = true
}

const submitRequest = async () => {
  try {
    await request.post('/resignation/requests', requestForm)
    ElMessage.success('申请提交成功')
    requestDialogVisible.value = false
    loadRequests()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

// 审批离职申请
const approveRequest = async (id, approved) => {
  try {
    await request.post('/resignation/approve', {
      request_id: id,
      approved: approved
    })
    ElMessage.success(approved ? '已批准' : '已拒绝')
    loadRequests()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 查看交接清单
const viewHandover = (resignationId) => {
  handoverFilter.resignation_id = resignationId
  activeTab.value = 'handover'
  loadHandovers()
}

// 添加交接项
const handleAddHandover = () => {
  Object.assign(handoverForm, {
    resignation_id: '',
    item_name: '',
    item_type: '',
    handler_id: '',
    remarks: ''
  })
  handoverDialogVisible.value = true
}

const submitHandover = async () => {
  try {
    await request.post('/resignation/handover', handoverForm)
    ElMessage.success('交接项添加成功')
    handoverDialogVisible.value = false
    loadHandovers()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

// 完成交接
const completeHandover = async (id) => {
  try {
    await request.put(`/resignation/handover/${id}`)
    ElMessage.success('交接已完成')
    loadHandovers()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 辅助函数
const getStatusType = (status) => {
  const map = {
    '待审批': '',
    '部门审批': 'warning',
    '人事审批': 'primary',
    '已批准': 'success',
    '已拒绝': 'danger',
    '已办理': 'info'
  }
  return map[status] || ''
}

const getTypePercentage = (stat) => {
  const total = typeStats.value.reduce((sum, s) => sum + s.count, 0)
  return total > 0 ? Math.round(stat.count / total * 100) : 0
}

onMounted(() => {
  loadRequests()
  loadHandovers()
  loadRecords()
  loadStatistics()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 20px; }
.search-form { margin-bottom: 20px; }
</style>
