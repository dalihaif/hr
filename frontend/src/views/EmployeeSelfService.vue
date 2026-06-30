<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>职工自助服务</span>
          <el-tag type="success">欢迎, {{ userInfo.real_name }}</el-tag>
        </div>
      </template>

      <!-- 快捷功能卡片 -->
      <el-row :gutter="20" class="quick-access">
        <el-col :xs="12" :sm="6" :md="4">
          <el-card shadow="hover" class="access-card" @click="activeTab = 'profile'">
            <el-icon size="40" color="#409EFF"><User /></el-icon>
            <div class="card-title">个人信息</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-card shadow="hover" class="access-card" @click="activeTab = 'salary'">
            <el-icon size="40" color="#67C23A"><Money /></el-icon>
            <div class="card-title">工资查询</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-card shadow="hover" class="access-card" @click="activeTab = 'performance'">
            <el-icon size="40" color="#E6A23C"><TrendCharts /></el-icon>
            <div class="card-title">绩效考核</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-card shadow="hover" class="access-card" @click="activeTab = 'attendance'">
            <el-icon size="40" color="#F56C6C"><Calendar /></el-icon>
            <div class="card-title">考勤记录</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-card shadow="hover" class="access-card" @click="activeTab = 'leave'">
            <el-icon size="40" color="#909399"><Document /></el-icon>
            <div class="card-title">请假申请</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-card shadow="hover" class="access-card" @click="activeTab = 'training'">
            <el-icon size="40" color="#409EFF"><Reading /></el-icon>
            <div class="card-title">培训记录</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Tab切换 -->
      <el-tabs v-model="activeTab" type="border-card" style="margin-top: 20px;">
        
        <!-- Tab 1: 个人信息 -->
        <el-tab-pane label="个人信息" name="profile">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名">{{ userInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="工号">{{ userInfo.emp_no }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ userInfo.gender }}</el-descriptions-item>
            <el-descriptions-item label="科室">{{ userInfo.current_dept }}</el-descriptions-item>
            <el-descriptions-item label="岗位">{{ userInfo.current_position }}</el-descriptions-item>
            <el-descriptions-item label="职称">{{ userInfo.current_title }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="userInfo.status === '在职' ? 'success' : 'info'">
                {{ userInfo.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="入职日期">{{ userInfo.entry_date }}</el-descriptions-item>
            
            <!-- 事业单位信息 -->
            <el-descriptions-item label="岗位等级">{{ userInfo.position_level || '-' }}</el-descriptions-item>
            <el-descriptions-item label="专业技术职称">{{ userInfo.professional_title || '-' }}</el-descriptions-item>
            <el-descriptions-item label="职称等级">{{ userInfo.title_level || '-' }}</el-descriptions-item>
            <el-descriptions-item label="薪级">{{ userInfo.salary_grade || '-' }}</el-descriptions-item>
            <el-descriptions-item label="学历">{{ userInfo.education_level || '-' }}</el-descriptions-item>
            <el-descriptions-item label="学位">{{ userInfo.degree_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="工龄">{{ userInfo.work_years ? userInfo.work_years + '年' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="本单位工龄">{{ userInfo.service_years ? userInfo.service_years + '年' : '-' }}</el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">联系方式</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="手机号">{{ userInfo.phone_encrypted || '-' }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ userInfo.email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="住址" :span="2">{{ userInfo.address || '-' }}</el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">社保与银行信息</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="社保号">{{ userInfo.social_security_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="公积金账号">{{ userInfo.housing_fund_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="银行账号">{{ userInfo.bank_account || '-' }}</el-descriptions-item>
            <el-descriptions-item label="开户银行">{{ userInfo.bank_name || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <!-- Tab 2: 工资查询 -->
        <el-tab-pane label="工资查询" name="salary">
          <!-- 选择月份 -->
          <el-form :inline="true" class="search-form">
            <el-form-item label="选择月份">
              <el-date-picker
                v-model="selectedSalaryMonth"
                type="month"
                placeholder="选择月份"
                format="YYYY-MM"
                value-format="YYYY-MM"
                @change="loadSalaryDetail"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleGeneratePDF">
                <el-icon><Document /></el-icon>下载工资条
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 工资明细 -->
          <el-card v-if="salaryDetail" shadow="never">
            <template #header>
              <div class="card-header">
                <span>{{ selectedSalaryMonth }} 工资明细</span>
                <el-tag type="success">实发: ¥{{ salaryDetail.summary.net_salary.toFixed(2) }}</el-tag>
              </div>
            </template>

            <!-- 应发项目 -->
            <h4 class="section-title">应发项目</h4>
            <el-table :data="salaryEarnings" border stripe>
              <el-table-column prop="item_name" label="项目名称" width="200" />
              <el-table-column prop="amount" label="金额(元)" align="right">
                <template #default="{ row }">
                  <span class="amount-positive">¥{{ row.amount.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="calculation_type" label="计算方式" />
            </el-table>

            <!-- 扣款项目 -->
            <h4 class="section-title" style="margin-top: 20px;">扣款项目</h4>
            <el-table :data="salaryDeductions" border stripe>
              <el-table-column prop="item_name" label="项目名称" width="200" />
              <el-table-column prop="amount" label="金额(元)" align="right">
                <template #default="{ row }">
                  <span class="amount-negative">-¥{{ row.amount.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="calculation_type" label="计算方式" />
            </el-table>

            <!-- 汇总 -->
            <el-divider />
            <el-descriptions :column="3" border>
              <el-descriptions-item label="应发合计">
                <span class="amount-positive">¥{{ salaryDetail.summary.total_earning.toFixed(2) }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="扣款合计">
                <span class="amount-negative">¥{{ salaryDetail.summary.total_deduction.toFixed(2) }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="实发工资">
                <span class="amount-net">¥{{ salaryDetail.summary.net_salary.toFixed(2) }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-empty v-else description="请选择月份查看工资明细" />

          <!-- 工资趋势图 -->
          <el-card shadow="hover" style="margin-top: 20px;">
            <template #header>
              <span>近6个月工资趋势</span>
            </template>
            <div ref="salaryChartRef" style="height: 300px;"></div>
          </el-card>
        </el-tab-pane>

        <!-- Tab 3: 绩效考核 -->
        <el-tab-pane label="绩效考核" name="performance">
          <!-- 考核列表 -->
          <el-table :data="performanceList" border stripe>
            <el-table-column prop="period_name" label="考核周期" width="150" />
            <el-table-column prop="total_score" label="总分" width="100">
              <template #default="{ row }">
                <el-tag :type="getScoreType(row.total_score)">{{ row.total_score }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="grade" label="等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getGradeType(row.grade)">{{ row.grade }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="performance_amount" label="绩效金额" width="120">
              <template #default="{ row }">
                ¥{{ row.performance_amount?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" @click="viewPerformanceDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 绩效统计 -->
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="8">
              <el-card shadow="hover">
                <el-statistic title="平均分" :value="perfStats.avgScore" />
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover">
                <el-statistic title="最高分" :value="perfStats.maxScore" />
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover">
                <el-statistic title="考核次数" :value="perfStats.count" />
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- Tab 4: 考勤记录 -->
        <el-tab-pane label="考勤记录" name="attendance">
          <!-- 选择月份 -->
          <el-form :inline="true" class="search-form">
            <el-form-item label="选择月份">
              <el-date-picker
                v-model="selectedAttendanceMonth"
                type="month"
                placeholder="选择月份"
                format="YYYY-MM"
                value-format="YYYY-MM"
                @change="loadAttendanceRecords"
              />
            </el-form-item>
          </el-form>

          <!-- 考勤统计卡片 -->
          <el-row :gutter="20" v-if="attendanceStats">
            <el-col :xs="12" :sm="6">
              <el-card shadow="hover">
                <el-statistic title="应出勤" :value="attendanceStats.work_days">
                  <template #suffix>天</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :xs="12" :sm="6">
              <el-card shadow="hover">
                <el-statistic title="实际出勤" :value="attendanceStats.actual_days">
                  <template #suffix>天</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :xs="12" :sm="6">
              <el-card shadow="hover">
                <el-statistic title="迟到次数" :value="attendanceStats.late_count">
                  <template #suffix>次</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :xs="12" :sm="6">
              <el-card shadow="hover">
                <el-statistic title="出勤率" :value="attendanceStats.attendance_rate">
                  <template #suffix>%</template>
                </el-statistic>
              </el-card>
            </el-col>
          </el-row>

          <!-- 考勤明细 -->
          <el-table :data="attendanceRecords" border stripe style="margin-top: 20px;">
            <el-table-column prop="attendance_date" label="日期" width="120" />
            <el-table-column prop="check_in_time" label="签到时间" width="120" />
            <el-table-column prop="check_out_time" label="签退时间" width="120" />
            <el-table-column prop="work_hours" label="工作时长" width="100">
              <template #default="{ row }">
                {{ row.work_hours ? row.work_hours.toFixed(1) + 'h' : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getAttendanceStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remarks" label="备注" />
          </el-table>
        </el-tab-pane>

        <!-- Tab 5: 请假申请 -->
        <el-tab-pane label="请假申请" name="leave">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddLeave">
              <el-icon><Plus /></el-icon>提交请假申请
            </el-button>
          </div>

          <!-- 假期余额 -->
          <el-card shadow="hover" class="balance-card">
            <template #header>
              <span>我的假期余额</span>
            </template>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-statistic title="年假" :value="leaveBalance.annual || 0">
                  <template #suffix>天</template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="病假" :value="leaveBalance.sick || 0">
                  <template #suffix>天</template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="调休" :value="leaveBalance.compensatory || 0">
                  <template #suffix>天</template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="其他" :value="leaveBalance.other || 0">
                  <template #suffix>天</template>
                </el-statistic>
              </el-col>
            </el-row>
          </el-card>

          <!-- 请假记录 -->
          <el-table :data="leaveRequests" border stripe style="margin-top: 20px;">
            <el-table-column prop="leave_type" label="请假类型" width="100" />
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column prop="days" label="天数" width="80" />
            <el-table-column prop="reason" label="请假原因" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getLeaveStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" @click="viewLeaveDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Tab 6: 培训记录 -->
        <el-tab-pane label="培训记录" name="training">
          <el-table :data="trainingRecords" border stripe>
            <el-table-column prop="training_name" label="培训名称" />
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column prop="hours" label="学时" width="80" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '已完成' ? 'success' : 'warning'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="certificate" label="证书" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.certificate" type="success">已获取</el-tag>
                <el-tag v-else type="info">未获取</el-tag>
              </template>
            </el-table-column>
          </el-table>

          <!-- 学时统计 -->
          <el-card shadow="hover" style="margin-top: 20px;">
            <template #header>
              <span>年度学时统计</span>
            </template>
            <el-progress 
              :percentage="trainingStats.completionRate" 
              :format="() => `${trainingStats.completedHours}/${trainingStats.requiredHours}学时`"
            />
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 请假申请对话框 -->
    <el-dialog
      v-model="leaveDialogVisible"
      title="提交请假申请"
      width="600px"
    >
      <el-form :model="leaveForm" label-width="100px">
        <el-form-item label="请假类型" required>
          <el-select v-model="leaveForm.leave_type" @change="handleLeaveTypeChange">
            <el-option label="事假" value="事假" />
            <el-option label="病假" value="病假" />
            <el-option label="年假" value="年假" />
            <el-option label="婚假" value="婚假" />
            <el-option label="产假" value="产假" />
            <el-option label="丧假" value="丧假" />
            <el-option label="调休" value="调休" />
          </el-select>
        </el-form-item>

        <!-- 产假专用字段 -->
        <template v-if="leaveForm.leave_type === '产假'">
          <el-form-item label="生产类型" required>
            <el-radio-group v-model="leaveForm.birth_type">
              <el-radio label="顺产">顺产</el-radio>
              <el-radio label="难产">难产</el-radio>
              <el-radio label="剖腹产">剖腹产</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="是否多胞胎">
            <el-switch v-model="leaveForm.is_multiple_birth" />
          </el-form-item>
          
          <el-form-item 
            label="胎儿数量" 
            v-if="leaveForm.is_multiple_birth"
            required
          >
            <el-input-number 
              v-model="leaveForm.multiple_count" 
              :min="2" 
              :max="10"
            />
          </el-form-item>
          
          <el-alert 
            v-if="maternityCalculation"
            type="success"
            :closable="false"
          >
            <template #default>
              <p><strong>产假天数计算:</strong></p>
              <p>基础产假: {{ maternityCalculation.base_days }}天</p>
              <p v-if="maternityCalculation.extra_days > 0">
                额外天数: +{{ maternityCalculation.extra_days }}天
                ({{ maternityCalculation.reasons.join(', ') }})
              </p>
              <p style="font-size: 18px; font-weight: bold; color: #409eff;">
                总计: {{ maternityCalculation.total_days }}天
              </p>
            </template>
          </el-alert>
        </template>

        <el-form-item label="起止日期" required>
          <el-date-picker
            v-model="leaveForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="calculateLeaveDays"
          />
        </el-form-item>

        <el-form-item label="请假天数">
          <el-input-number 
            v-model="leaveForm.days" 
            :min="0.5" 
            :step="0.5"
            disabled
          />
        </el-form-item>

        <el-form-item label="请假原因" required>
          <el-input 
            v-model="leaveForm.reason" 
            type="textarea"
            :rows="3"
            placeholder="请详细说明请假原因"
          />
        </el-form-item>

        <el-form-item label="证明材料">
          <el-upload
            action="/api/upload"
            :limit="3"
            :on-success="handleUploadSuccess"
          >
            <el-button type="primary">上传文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持jpg/png/pdf,不超过3个文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="leaveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitLeaveRequest">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import * as echarts from 'echarts'

const activeTab = ref('profile')
const userInfo = ref({})

// 工资相关
const selectedSalaryMonth = ref(new Date().toISOString().slice(0, 7))
const salaryDetail = ref(null)
const salaryChartRef = ref(null)

// 绩效相关
const performanceList = ref([])
const perfStats = reactive({ avgScore: 0, maxScore: 0, count: 0 })

// 考勤相关
const selectedAttendanceMonth = ref(new Date().toISOString().slice(0, 7))
const attendanceRecords = ref([])
const attendanceStats = ref(null)

// 请假相关
const leaveRequests = ref([])
const leaveBalance = reactive({ annual: 0, sick: 0, compensatory: 0, other: 0 })
const leaveDialogVisible = ref(false)
const leaveForm = reactive({
  leave_type: '',
  birth_type: '顺产',
  is_multiple_birth: false,
  multiple_count: 1,
  dateRange: [],
  days: 0,
  reason: '',
  attachments: []
})

// 培训相关
const trainingRecords = ref([])
const trainingStats = reactive({ completedHours: 0, requiredHours: 0, completionRate: 0 })

// 计算属性
const salaryEarnings = computed(() => {
  if (!salaryDetail.value) return []
  return salaryDetail.value.items.filter(item => 
    ['position_salary', 'grade_salary', 'performance_bonus', 
     'housing_subsidy', 'transport_allowance'].includes(item.item_code)
  )
})

const salaryDeductions = computed(() => {
  if (!salaryDetail.value) return []
  return salaryDetail.value.items.filter(item => 
    ['pension_insurance', 'medical_insurance', 'unemployment_insurance',
     'housing_fund', 'income_tax'].includes(item.item_code)
  )
})

const maternityCalculation = computed(() => {
  if (leaveForm.leave_type !== '产假') return null
  
  let baseDays = 158
  let extraDays = 0
  let reasons = []
  
  if (leaveForm.birth_type in ['难产', '剖腹产']) {
    extraDays += 15
    reasons.push('难产/剖腹产+15天')
  }
  
  if (leaveForm.is_multiple_birth && leaveForm.multiple_count > 1) {
    const additional = (leaveForm.multiple_count - 1) * 15
    extraDays += additional
    reasons.push(`多胞胎(${leaveForm.multiple_count}胎)+${additional}天`)
  }
  
  return {
    base_days: baseDays,
    extra_days: extraDays,
    total_days: baseDays + extraDays,
    reasons: reasons
  }
})

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const response = await request.get('/employees/me')
    userInfo.value = response
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  }
}

// 加载工资明细
const loadSalaryDetail = async () => {
  try {
    const empId = userInfo.value.id
    const response = await request.get(`/salary/calculate/${empId}`, {
      params: { year_month: selectedSalaryMonth.value }
    })
    salaryDetail.value = response
    renderSalaryChart()
  } catch (error) {
    ElMessage.error('加载工资明细失败')
  }
}

// 渲染工资趋势图
const renderSalaryChart = async () => {
  if (!salaryChartRef.value) return
  
  await nextTick()
  
  try {
    // 获取近6个月工资数据
    const empId = userInfo.value.id
    const months = []
    const amounts = []
    
    for (let i = 5; i >= 0; i--) {
      const date = new Date()
      date.setMonth(date.getMonth() - i)
      const monthStr = date.toISOString().slice(0, 7)
      months.push(monthStr)
      
      const response = await request.get(`/salary/calculate/${empId}`, {
        params: { year_month: monthStr }
      })
      amounts.push(response.summary.net_salary)
    }
    
    const chart = echarts.init(salaryChartRef.value)
    chart.setOption({
      title: { text: '近6个月实发工资趋势' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: months },
      yAxis: { type: 'value', name: '金额(元)' },
      series: [{
        data: amounts,
        type: 'line',
        smooth: true,
        itemStyle: { color: '#409EFF' },
        areaStyle: { opacity: 0.3 }
      }]
    })
  } catch (error) {
    console.error('渲染图表失败:', error)
  }
}

// 加载绩效列表
const loadPerformanceList = async () => {
  try {
    const response = await request.get('/performance/my-assessments')
    performanceList.value = response
    
    // 计算统计
    if (response.length > 0) {
      const scores = response.map(p => p.total_score).filter(s => s)
      perfStats.avgScore = scores.reduce((a, b) => a + b, 0) / scores.length
      perfStats.maxScore = Math.max(...scores)
      perfStats.count = response.length
    }
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载考勤记录
const loadAttendanceRecords = async () => {
  try {
    const response = await request.get('/attendance/my-records', {
      params: { month: selectedAttendanceMonth.value }
    })
    attendanceRecords.value = response.data || []
    attendanceStats.value = response.stats || null
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载请假记录
const loadLeaveRequests = async () => {
  try {
    const [requestsRes, balanceRes] = await Promise.all([
      request.get('/attendance/my-leave-requests'),
      request.get('/attendance/my-leave-balance')
    ])
    leaveRequests.value = requestsRes
    Object.assign(leaveBalance, balanceRes)
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载培训记录
const loadTrainingRecords = async () => {
  try {
    const response = await request.get('/training/my-records')
    trainingRecords.value = response
    
    // 计算学时统计
    const currentYear = new Date().getFullYear()
    const yearRecords = response.filter(r => r.year === currentYear)
    const completedHours = yearRecords.reduce((sum, r) => sum + (r.hours || 0), 0)
    const requiredHours = 40 // 年度要求学时
    
    trainingStats.completedHours = completedHours
    trainingStats.requiredHours = requiredHours
    trainingStats.completionRate = Math.min(100, (completedHours / requiredHours) * 100)
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 提交请假申请
const submitLeaveRequest = async () => {
  if (!leaveForm.leave_type || !leaveForm.dateRange || !leaveForm.reason) {
    ElMessage.warning('请填写必填字段')
    return
  }

  try {
    const data = {
      ...leaveForm,
      start_date: leaveForm.dateRange[0],
      end_date: leaveForm.dateRange[1]
    }
    
    await request.post('/attendance/leave-requests', data)
    ElMessage.success('提交成功')
    leaveDialogVisible.value = false
    loadLeaveRequests()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

// 辅助方法
const handleLeaveTypeChange = () => {
  leaveForm.days = 0
  leaveForm.dateRange = []
}

const calculateLeaveDays = () => {
  if (!leaveForm.dateRange || leaveForm.dateRange.length !== 2) return
  
  const start = new Date(leaveForm.dateRange[0])
  const end = new Date(leaveForm.dateRange[1])
  const days = (end - start) / (1000 * 60 * 60 * 24) + 1
  
  leaveForm.days = days
}

const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 75) return ''
  if (score >= 60) return 'warning'
  return 'danger'
}

const getGradeType = (grade) => {
  const map = { '优秀': 'success', '良好': '', '合格': 'warning', '不合格': 'danger' }
  return map[grade] || ''
}

const getStatusType = (status) => {
  const map = { '已发布': '', '填报中': 'warning', '审核中': 'warning', '已审核': 'success', '已发放': 'success' }
  return map[status] || ''
}

const getAttendanceStatusType = (status) => {
  const map = { '正常': 'success', '迟到': 'warning', '早退': 'warning', '缺勤': 'danger', '请假': 'info' }
  return map[status] || ''
}

const getLeaveStatusType = (status) => {
  const map = { '待审批': 'warning', '已批准': 'success', '已拒绝': 'danger', '已销假': 'info' }
  return map[status] || ''
}

const handleAddLeave = () => {
  leaveDialogVisible.value = true
}

const viewPerformanceDetail = (row) => {
  ElMessage.info('查看详情功能开发中')
}

const viewLeaveDetail = (row) => {
  ElMessage.info('查看详情功能开发中')
}

const handleGeneratePDF = () => {
  ElMessage.info('下载工资条功能开发中')
}

const handleUploadSuccess = (response) => {
  leaveForm.attachments.push(response.url)
}

onMounted(() => {
  loadUserInfo()
  loadSalaryDetail()
  loadPerformanceList()
  loadAttendanceRecords()
  loadLeaveRequests()
  loadTrainingRecords()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.quick-access { margin-bottom: 20px; }
.access-card {
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}
.access-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.card-title {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}
.search-form { margin-bottom: 20px; }
.toolbar { margin-bottom: 20px; }
.section-title {
  font-size: 16px;
  font-weight: bold;
  margin: 15px 0 10px 0;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}
.amount-positive { color: #67c23a; font-weight: bold; }
.amount-negative { color: #f56c6c; font-weight: bold; }
.amount-net { 
  color: #409eff; 
  font-weight: bold; 
  font-size: 18px;
}
.balance-card { margin-bottom: 20px; }
</style>
