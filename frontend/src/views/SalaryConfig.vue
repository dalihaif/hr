<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>工资标准配置</span>
          <el-tag type="info">事业单位工资标准管理</el-tag>
        </div>
      </template>

      <!-- Tab切换 -->
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 岗位工资标准 -->
        <el-tab-pane label="岗位工资标准" name="position">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddPosition">
              <el-icon><Plus /></el-icon>新增标准
            </el-button>
            <el-button @click="loadPositionStandards">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
          </div>

          <el-table :data="positionStandards" border stripe>
            <el-table-column prop="position_type" label="岗位类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getPositionTypeColor(row.position_type)">
                  {{ row.position_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="position_level" label="岗位等级" width="150" />
            <el-table-column prop="salary_amount" label="工资金额(元)" width="150">
              <template #default="{ row }">
                <span class="amount">{{ row.salary_amount.toFixed(0) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="effective_date" label="生效日期" width="120" />
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="handleEditPosition(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeletePosition(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="positionStandards.length === 0" description="暂无数据" />
        </el-tab-pane>

        <!-- 薪级工资标准 -->
        <el-tab-pane label="薪级工资标准" name="grade">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddGrade">
              <el-icon><Plus /></el-icon>新增标准
            </el-button>
            <el-button @click="loadGradeStandards">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
          </div>

          <el-table :data="gradeStandards" border stripe>
            <el-table-column prop="education_level" label="学历" width="150">
              <template #default="{ row }">
                <el-tag>{{ row.education_level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="salary_grade" label="薪级" width="100" />
            <el-table-column prop="salary_amount" label="工资金额(元)" width="150">
              <template #default="{ row }">
                <span class="amount">{{ row.salary_amount.toFixed(0) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="effective_date" label="生效日期" width="120" />
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="handleEditGrade(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteGrade(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="gradeStandards.length === 0" description="暂无数据" />
        </el-tab-pane>

        <!-- 社保配置 -->
        <el-tab-pane label="社保缴费配置" name="social">
          <div class="toolbar">
            <el-button type="primary" @click="handleEditSocialConfig">
              <el-icon><Edit /></el-icon>编辑配置
            </el-button>
          </div>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="年份">
              {{ socialConfig.year || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="月份">
              {{ socialConfig.month || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="缴费基数下限">
              {{ socialConfig.base_min || '-' }} 元
            </el-descriptions-item>
            <el-descriptions-item label="缴费基数上限">
              {{ socialConfig.base_max || '-' }} 元
            </el-descriptions-item>
            <el-descriptions-item label="养老保险比例(个人)">
              {{ socialConfig.pension_ratio ? (socialConfig.pension_ratio * 100).toFixed(1) + '%' : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="医疗保险比例(个人)">
              {{ socialConfig.medical_ratio ? (socialConfig.medical_ratio * 100).toFixed(1) + '%' : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="失业保险比例(个人)">
              {{ socialConfig.unemployment_ratio ? (socialConfig.unemployment_ratio * 100).toFixed(1) + '%' : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="住房公积金比例(个人)">
              {{ socialConfig.housing_fund_ratio ? (socialConfig.housing_fund_ratio * 100).toFixed(1) + '%' : '-' }}
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="提示"
            type="info"
            :closable="false"
            style="margin-top: 20px;"
          >
            <template #default>
              <p>社保缴费比例通常为:</p>
              <ul>
                <li>养老保险: 个人8%, 单位16%</li>
                <li>医疗保险: 个人2%, 单位8%</li>
                <li>失业保险: 个人0.5%, 单位0.5%</li>
                <li>住房公积金: 个人12%, 单位12%</li>
              </ul>
              <p>缴费基数范围由当地社保局每年公布。</p>
            </template>
          </el-alert>
        </el-tab-pane>

        <!-- 个税税率表 -->
        <el-tab-pane label="个税税率表" name="tax">
          <el-table :data="taxBrackets" border stripe>
            <el-table-column prop="level" label="级数" width="80" />
            <el-table-column label="全年应纳税所得额范围">
              <template #default="{ row }">
                {{ formatIncomeRange(row.min_income, row.max_income) }}
              </template>
            </el-table-column>
            <el-table-column prop="tax_rate" label="税率">
              <template #default="{ row }">
                <el-tag type="warning">{{ (row.tax_rate * 100).toFixed(0) }}%</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quick_deduction" label="速算扣除数(元)" />
          </el-table>

          <el-alert
            title="说明"
            type="success"
            :closable="false"
            style="margin-top: 20px;"
          >
            <template #default>
              <p>个人所得税采用累计预扣法计算:</p>
              <p><strong>应纳税额 = 应纳税所得额 × 税率 - 速算扣除数</strong></p>
              <p>其中: 应纳税所得额 = 累计收入 - 累计免税收入 - 累计减除费用 - 累计专项扣除 - 累计专项附加扣除 - 累计依法确定的其他扣除</p>
              <p>减除费用: 5000元/月 (60000元/年)</p>
            </template>
          </el-alert>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 岗位工资标准编辑对话框 -->
    <el-dialog
      v-model="positionDialogVisible"
      :title="positionDialogTitle"
      width="600px"
    >
      <el-form :model="positionForm" label-width="120px">
        <el-form-item label="岗位类型" required>
          <el-select v-model="positionForm.position_type" placeholder="请选择">
            <el-option label="管理岗" value="管理" />
            <el-option label="专技岗" value="专技" />
            <el-option label="工勤岗" value="工勤" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位等级" required>
          <el-input v-model="positionForm.position_level" placeholder="如: 一级、二级、专技十级" />
        </el-form-item>
        <el-form-item label="工资金额" required>
          <el-input-number 
            v-model="positionForm.salary_amount" 
            :min="0" 
            :step="100"
            style="width: 100%" 
          />
        </el-form-item>
        <el-form-item label="生效日期">
          <el-date-picker
            v-model="positionForm.effective_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="positionForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="positionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPositionForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 薪级工资标准编辑对话框 -->
    <el-dialog
      v-model="gradeDialogVisible"
      :title="gradeDialogTitle"
      width="600px"
    >
      <el-form :model="gradeForm" label-width="120px">
        <el-form-item label="学历" required>
          <el-select v-model="gradeForm.education_level" placeholder="请选择">
            <el-option label="博士研究生" value="博士研究生" />
            <el-option label="硕士研究生" value="硕士研究生" />
            <el-option label="本科" value="本科" />
            <el-option label="大专" value="大专" />
            <el-option label="中专" value="中专" />
          </el-select>
        </el-form-item>
        <el-form-item label="薪级" required>
          <el-input-number 
            v-model="gradeForm.salary_grade" 
            :min="1" 
            :max="65"
            style="width: 100%" 
          />
        </el-form-item>
        <el-form-item label="工资金额" required>
          <el-input-number 
            v-model="gradeForm.salary_amount" 
            :min="0" 
            :step="50"
            style="width: 100%" 
          />
        </el-form-item>
        <el-form-item label="生效日期">
          <el-date-picker
            v-model="gradeForm.effective_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="gradeForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="gradeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGradeForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 社保配置编辑对话框 -->
    <el-dialog
      v-model="socialDialogVisible"
      title="编辑社保配置"
      width="600px"
    >
      <el-form :model="socialForm" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年份" required>
              <el-input-number 
                v-model="socialForm.year" 
                :min="2020" 
                :max="2030"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="月份" required>
              <el-input-number 
                v-model="socialForm.month" 
                :min="1" 
                :max="12"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="缴费基数下限" required>
              <el-input-number 
                v-model="socialForm.base_min" 
                :min="0" 
                :step="500"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="缴费基数上限" required>
              <el-input-number 
                v-model="socialForm.base_max" 
                :min="0" 
                :step="1000"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">个人缴费比例</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="养老保险">
              <el-input-number 
                v-model="socialForm.pension_ratio" 
                :min="0" 
                :max="1" 
                :step="0.01"
                style="width: 100%" 
              />
              <div class="form-tip">{{ (socialForm.pension_ratio * 100).toFixed(1) }}%</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="医疗保险">
              <el-input-number 
                v-model="socialForm.medical_ratio" 
                :min="0" 
                :max="1" 
                :step="0.01"
                style="width: 100%" 
              />
              <div class="form-tip">{{ (socialForm.medical_ratio * 100).toFixed(1) }}%</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="失业保险">
              <el-input-number 
                v-model="socialForm.unemployment_ratio" 
                :min="0" 
                :max="1" 
                :step="0.001"
                style="width: 100%" 
              />
              <div class="form-tip">{{ (socialForm.unemployment_ratio * 100).toFixed(1) }}%</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="住房公积金">
              <el-input-number 
                v-model="socialForm.housing_fund_ratio" 
                :min="0" 
                :max="1" 
                :step="0.01"
                style="width: 100%" 
              />
              <div class="form-tip">{{ (socialForm.housing_fund_ratio * 100).toFixed(1) }}%</div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="socialDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSocialForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('position')

// 岗位工资标准
const positionStandards = ref([])
const positionDialogVisible = ref(false)
const positionDialogTitle = ref('新增岗位工资标准')
const positionForm = reactive({
  id: null,
  position_type: '',
  position_level: '',
  salary_amount: 0,
  effective_date: new Date().toISOString().slice(0, 10),
  is_active: true
})

// 薪级工资标准
const gradeStandards = ref([])
const gradeDialogVisible = ref(false)
const gradeDialogTitle = ref('新增薪级工资标准')
const gradeForm = reactive({
  id: null,
  education_level: '',
  salary_grade: 1,
  salary_amount: 0,
  effective_date: new Date().toISOString().slice(0, 10),
  is_active: true
})

// 社保配置
const socialConfig = ref({})
const socialDialogVisible = ref(false)
const socialForm = reactive({
  year: new Date().getFullYear(),
  month: 1,
  base_min: 3000,
  base_max: 20000,
  pension_ratio: 0.08,
  medical_ratio: 0.02,
  unemployment_ratio: 0.005,
  housing_fund_ratio: 0.12
})

// 个税税率表
const taxBrackets = ref([])

// 加载岗位工资标准
const loadPositionStandards = async () => {
  try {
    // TODO: 需要后端提供API
    // const response = await request.get('/salary/position-standards')
    // positionStandards.value = response
    
    // 临时模拟数据
    positionStandards.value = [
      { id: 1, position_type: '专技', position_level: '正高', salary_amount: 7500, effective_date: '2024-01-01', is_active: true },
      { id: 2, position_type: '专技', position_level: '副高', salary_amount: 6500, effective_date: '2024-01-01', is_active: true },
      { id: 3, position_type: '专技', position_level: '中级', salary_amount: 5500, effective_date: '2024-01-01', is_active: true },
      { id: 4, position_type: '专技', position_level: '初级', salary_amount: 4500, effective_date: '2024-01-01', is_active: true },
      { id: 5, position_type: '管理', position_level: '一级', salary_amount: 8000, effective_date: '2024-01-01', is_active: true },
      { id: 6, position_type: '管理', position_level: '二级', salary_amount: 7000, effective_date: '2024-01-01', is_active: true },
    ]
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载薪级工资标准
const loadGradeStandards = async () => {
  try {
    // TODO: 需要后端提供API
    // const response = await request.get('/salary/grade-standards')
    // gradeStandards.value = response
    
    // 临时模拟数据
    gradeStandards.value = []
    for (let i = 1; i <= 65; i++) {
      gradeStandards.value.push({
        id: i,
        education_level: '本科',
        salary_grade: i,
        salary_amount: 1000 + i * 50,
        effective_date: '2024-01-01',
        is_active: true
      })
    }
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载社保配置
const loadSocialConfig = async () => {
  try {
    const response = await request.get('/salary/social-security/config')
    socialConfig.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 加载个税税率表
const loadTaxBrackets = async () => {
  try {
    const response = await request.get('/salary/tax-brackets')
    taxBrackets.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 新增岗位标准
const handleAddPosition = () => {
  positionDialogTitle.value = '新增岗位工资标准'
  Object.assign(positionForm, {
    id: null,
    position_type: '',
    position_level: '',
    salary_amount: 0,
    effective_date: new Date().toISOString().slice(0, 10),
    is_active: true
  })
  positionDialogVisible.value = true
}

// 编辑岗位标准
const handleEditPosition = (row) => {
  positionDialogTitle.value = '编辑岗位工资标准'
  Object.assign(positionForm, row)
  positionDialogVisible.value = true
}

// 提交岗位标准表单
const submitPositionForm = async () => {
  if (!positionForm.position_type || !positionForm.position_level || !positionForm.salary_amount) {
    ElMessage.warning('请填写必填字段')
    return
  }

  try {
    // TODO: 需要后端提供API
    // if (positionForm.id) {
    //   await request.put(`/salary/position-standards/${positionForm.id}`, positionForm)
    // } else {
    //   await request.post('/salary/position-standards', positionForm)
    // }
    
    ElMessage.success('保存成功(演示模式)')
    positionDialogVisible.value = false
    loadPositionStandards()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  }
}

// 删除岗位标准
const handleDeletePosition = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此标准吗?', '提示', { type: 'warning' })
    // TODO: 需要后端提供API
    // await request.delete(`/salary/position-standards/${id}`)
    ElMessage.success('删除成功(演示模式)')
    loadPositionStandards()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 新增薪级标准
const handleAddGrade = () => {
  gradeDialogTitle.value = '新增薪级工资标准'
  Object.assign(gradeForm, {
    id: null,
    education_level: '',
    salary_grade: 1,
    salary_amount: 0,
    effective_date: new Date().toISOString().slice(0, 10),
    is_active: true
  })
  gradeDialogVisible.value = true
}

// 编辑薪级标准
const handleEditGrade = (row) => {
  gradeDialogTitle.value = '编辑薪级工资标准'
  Object.assign(gradeForm, row)
  gradeDialogVisible.value = true
}

// 提交薪级标准表单
const submitGradeForm = async () => {
  if (!gradeForm.education_level || !gradeForm.salary_grade || !gradeForm.salary_amount) {
    ElMessage.warning('请填写必填字段')
    return
  }

  try {
    // TODO: 需要后端提供API
    // if (gradeForm.id) {
    //   await request.put(`/salary/grade-standards/${gradeForm.id}`, gradeForm)
    // } else {
    //   await request.post('/salary/grade-standards', gradeForm)
    // }
    
    ElMessage.success('保存成功(演示模式)')
    gradeDialogVisible.value = false
    loadGradeStandards()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  }
}

// 删除薪级标准
const handleDeleteGrade = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此标准吗?', '提示', { type: 'warning' })
    // TODO: 需要后端提供API
    // await request.delete(`/salary/grade-standards/${id}`)
    ElMessage.success('删除成功(演示模式)')
    loadGradeStandards()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 编辑社保配置
const handleEditSocialConfig = () => {
  Object.assign(socialForm, socialConfig.value, {
    year: socialConfig.value.year || new Date().getFullYear(),
    month: socialConfig.value.month || 1,
    base_min: socialConfig.value.base_min || 3000,
    base_max: socialConfig.value.base_max || 20000,
    pension_ratio: socialConfig.value.pension_ratio || 0.08,
    medical_ratio: socialConfig.value.medical_ratio || 0.02,
    unemployment_ratio: socialConfig.value.unemployment_ratio || 0.005,
    housing_fund_ratio: socialConfig.value.housing_fund_ratio || 0.12
  })
  socialDialogVisible.value = true
}

// 提交社保配置表单
const submitSocialForm = async () => {
  try {
    await request.post('/salary/social-security/config', socialForm)
    ElMessage.success('保存成功')
    socialDialogVisible.value = false
    loadSocialConfig()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  }
}

// 获取岗位类型颜色
const getPositionTypeColor = (type) => {
  const colorMap = {
    '管理': 'danger',
    '专技': 'primary',
    '工勤': 'success'
  }
  return colorMap[type] || ''
}

// 格式化收入范围
const formatIncomeRange = (min, max) => {
  if (max === null) {
    return `超过 ${min.toLocaleString()} 元`
  }
  return `${min.toLocaleString()} - ${max.toLocaleString()} 元`
}

onMounted(() => {
  loadPositionStandards()
  loadGradeStandards()
  loadSocialConfig()
  loadTaxBrackets()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.toolbar { margin-bottom: 20px; }
.amount {
  color: #409eff;
  font-weight: bold;
}
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
