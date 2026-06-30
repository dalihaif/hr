<template>
  <div class="page-container">
    <el-card>
      <!-- Tab切换 -->
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 工资计算 -->
        <el-tab-pane label="工资计算" name="calculate">
          <!-- 选择职工和月份 -->
          <el-form :inline="true" class="search-form">
            <el-form-item label="选择职工">
              <el-select 
                v-model="selectedEmpId" 
                placeholder="请选择职工" 
                style="width: 200px"
                filterable
              >
                <el-option
                  v-for="emp in employees"
                  :key="emp.id"
                  :label="`${emp.name} (${emp.emp_no})`"
                  :value="emp.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="工资月份">
              <el-date-picker
                v-model="selectedMonth"
                type="month"
                placeholder="选择月份"
                format="YYYY-MM"
                value-format="YYYY-MM"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleCalculate" :disabled="!selectedEmpId">
                <el-icon><Calculator /></el-icon>计算工资
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 工资明细展示 -->
          <el-card v-if="salaryResult" shadow="never" class="salary-result">
            <template #header>
              <div class="card-header">
                <span>工资明细 - {{ salaryResult.name }} ({{ salaryResult.year_month }})</span>
                <el-button type="success" size="small" @click="handleGeneratePDF">
                  <el-icon><Document /></el-icon>生成PDF工资条
                </el-button>
              </div>
            </template>

            <!-- 应发项目 -->
            <h3 class="section-title">应发项目</h3>
            <el-table :data="earningItems" border stripe>
              <el-table-column prop="item_name" label="项目名称" width="150" />
              <el-table-column prop="amount" label="金额(元)" width="150">
                <template #default="{ row }">
                  <span class="amount-positive">{{ row.amount.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="calculation_type" label="计算方式" />
            </el-table>

            <!-- 扣款项目 -->
            <h3 class="section-title" style="margin-top: 20px;">扣款项目</h3>
            <el-table :data="deductionItems" border stripe>
              <el-table-column prop="item_name" label="项目名称" width="150" />
              <el-table-column prop="amount" label="金额(元)" width="150">
                <template #default="{ row }">
                  <span class="amount-negative">{{ row.amount.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="calculation_type" label="计算方式" />
            </el-table>

            <!-- 汇总 -->
            <el-divider />
            <el-descriptions :column="3" border>
              <el-descriptions-item label="应发合计">
                <span class="amount-positive">{{ salaryResult.summary.total_earning.toFixed(2) }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="扣款合计">
                <span class="amount-negative">{{ salaryResult.summary.total_deduction.toFixed(2) }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="实发工资">
                <span class="amount-net">{{ salaryResult.summary.net_salary.toFixed(2) }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-empty v-else description="请选择职工并计算工资" />
        </el-tab-pane>

        <!-- 工资项目管理 -->
        <el-tab-pane label="工资项目管理" name="items">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddItem">
              <el-icon><Plus /></el-icon>新增项目
            </el-button>
            <el-button @click="loadSalaryItems">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
          </div>

          <el-table :data="salaryItems" border stripe>
            <el-table-column prop="item_name" label="项目名称" width="150" />
            <el-table-column prop="item_code" label="项目编码" width="150" />
            <el-table-column prop="category_name" label="分类" width="120">
              <template #default="{ row }">
                <el-tag>{{ row.category_name || '未分类' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="item_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getItemTypeColor(row.item_type)">{{ row.item_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="calculation_type" label="计算方式" width="120" />
            <el-table-column prop="base_value" label="基础值" width="100">
              <template #default="{ row }">
                {{ row.base_value || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="ratio" label="比例" width="100">
              <template #default="{ row }">
                {{ row.ratio ? (row.ratio * 100).toFixed(1) + '%' : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="is_taxable" label="计税" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_taxable ? 'warning' : 'info'">
                  {{ row.is_taxable ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="handleEditItem(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteItem(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 配置信息 -->
        <el-tab-pane label="配置信息" name="config">
          <el-row :gutter="20">
            <!-- 个税税率表 -->
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>个人所得税税率表</span>
                  </div>
                </template>
                <el-table :data="taxBrackets" border stripe>
                  <el-table-column prop="level" label="级数" width="80" />
                  <el-table-column label="应纳税所得额范围">
                    <template #default="{ row }">
                      {{ formatIncomeRange(row.min_income, row.max_income) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="tax_rate" label="税率">
                    <template #default="{ row }">
                      {{ (row.tax_rate * 100).toFixed(0) }}%
                    </template>
                  </el-table-column>
                  <el-table-column prop="quick_deduction" label="速算扣除数" />
                </el-table>
              </el-card>
            </el-col>

            <!-- 社保配置 -->
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>社保缴费配置 ({{ currentYear }}年)</span>
                  </div>
                </template>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="缴费基数范围">
                    {{ ssConfig.base_min }} - {{ ssConfig.base_max }} 元
                  </el-descriptions-item>
                  <el-descriptions-item label="养老保险(个人)">
                    {{ (ssConfig.pension_ratio * 100).toFixed(1) }}%
                  </el-descriptions-item>
                  <el-descriptions-item label="医疗保险(个人)">
                    {{ (ssConfig.medical_ratio * 100).toFixed(1) }}%
                  </el-descriptions-item>
                  <el-descriptions-item label="失业保险(个人)">
                    {{ (ssConfig.unemployment_ratio * 100).toFixed(1) }}%
                  </el-descriptions-item>
                  <el-descriptions-item label="住房公积金(个人)">
                    {{ (ssConfig.housing_fund_ratio * 100).toFixed(1) }}%
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>

          <!-- 工资项目分类 -->
          <el-card shadow="hover" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>工资项目分类</span>
              </div>
            </template>
            <el-table :data="categories" border stripe>
              <el-table-column prop="category_name" label="分类名称" />
              <el-table-column prop="category_code" label="分类编码" />
              <el-table-column prop="description" label="说明" />
            </el-table>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 工资项目编辑对话框 -->
    <el-dialog
      v-model="itemDialogVisible"
      :title="itemDialogTitle"
      width="700px"
    >
      <el-form :model="itemForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目名称" required>
              <el-input v-model="itemForm.item_name" placeholder="如：夜班津贴" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目编码" required>
              <el-input v-model="itemForm.item_code" placeholder="如：night_shift_allowance" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属分类">
              <el-select v-model="itemForm.category_id" clearable placeholder="请选择">
                <el-option
                  v-for="cat in categories"
                  :key="cat.id"
                  :label="cat.category_name"
                  :value="cat.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目类型">
              <el-select v-model="itemForm.item_type">
                <el-option label="固定项" value="固定项" />
                <el-option label="浮动项" value="浮动项" />
                <el-option label="扣款项" value="扣款项" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计算方式">
              <el-select v-model="itemForm.calculation_type">
                <el-option label="固定值" value="固定值" />
                <el-option label="比例" value="比例" />
                <el-option label="公式" value="公式" />
                <el-option label="查表" value="查表" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否计税">
              <el-switch v-model="itemForm.is_taxable" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="基础值" v-if="itemForm.calculation_type === '固定值'">
              <el-input-number v-model="itemForm.base_value" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="比例" v-if="itemForm.calculation_type === '比例'">
              <el-input-number 
                v-model="itemForm.ratio" 
                :min="0" 
                :max="1" 
                :step="0.01"
                style="width: 100%" 
              />
              <div class="form-tip">{{ (itemForm.ratio * 100).toFixed(1) }}%</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="计算公式" v-if="itemForm.calculation_type === '公式'">
          <el-input 
            v-model="itemForm.formula" 
            type="textarea"
            :rows="3"
            placeholder="如：base_salary * 0.4 或 paper_count * 1000"
          />
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number v-model="itemForm.sort_order" :min="0" />
        </el-form-item>

        <el-form-item label="说明">
          <el-input 
            v-model="itemForm.description" 
            type="textarea"
            :rows="2"
            placeholder="项目说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitItemForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('calculate')
const employees = ref([])
const selectedEmpId = ref(null)
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const salaryResult = ref(null)

// 工资项目
const salaryItems = ref([])
const itemDialogVisible = ref(false)
const itemDialogTitle = ref('新增项目')
const itemForm = reactive({
  id: null,
  item_name: '',
  item_code: '',
  category_id: null,
  item_type: '固定项',
  calculation_type: '固定值',
  formula: '',
  base_value: 0,
  ratio: null,
  is_taxable: true,
  sort_order: 0,
  description: ''
})

// 配置数据
const taxBrackets = ref([])
const ssConfig = ref({})
const categories = ref([])
const currentYear = ref(new Date().getFullYear())

// 应发项目
const earningItems = computed(() => {
  if (!salaryResult.value) return []
  return salaryResult.value.items.filter(item => 
    ['position_salary', 'grade_salary', 'performance_bonus', 
     'housing_subsidy', 'transport_allowance', 'night_shift_allowance'].includes(item.item_code)
  )
})

// 扣款项目
const deductionItems = computed(() => {
  if (!salaryResult.value) return []
  return salaryResult.value.items.filter(item => 
    ['pension_insurance', 'medical_insurance', 'unemployment_insurance',
     'housing_fund', 'income_tax'].includes(item.item_code)
  )
})

// 加载职工列表
const loadEmployees = async () => {
  try {
    const response = await request.get('/employees', { params: { limit: 1000 } })
    employees.value = response.data || []
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 计算工资
const handleCalculate = async () => {
  if (!selectedEmpId.value) {
    ElMessage.warning('请选择职工')
    return
  }

  try {
    const response = await request.get(`/salary/calculate/${selectedEmpId.value}`, {
      params: { year_month: selectedMonth.value }
    })
    salaryResult.value = response
    ElMessage.success('工资计算成功')
  } catch (error) {
    ElMessage.error('计算失败: ' + (error.response?.data?.error || error.message))
  }
}

// 重置
const handleReset = () => {
  selectedEmpId.value = null
  salaryResult.value = null
}

// 生成PDF工资条
const handleGeneratePDF = async () => {
  try {
    const response = await request.post('/salary/slips/generate', {
      month: selectedMonth.value,
      emp_ids: [selectedEmpId.value]
    }, { responseType: 'blob' })
    
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `工资条_${salaryResult.value.name}_${selectedMonth.value}.pdf`)
    link.click()
    ElMessage.success('PDF工资条生成成功')
  } catch (error) {
    ElMessage.error('生成失败')
  }
}

// 加载工资项目
const loadSalaryItems = async () => {
  try {
    const response = await request.get('/salary/items/config')
    salaryItems.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 新增项目
const handleAddItem = () => {
  itemDialogTitle.value = '新增项目'
  Object.assign(itemForm, {
    id: null,
    item_name: '',
    item_code: '',
    category_id: null,
    item_type: '固定项',
    calculation_type: '固定值',
    formula: '',
    base_value: 0,
    ratio: null,
    is_taxable: true,
    sort_order: 0,
    description: ''
  })
  itemDialogVisible.value = true
}

// 编辑项目
const handleEditItem = (row) => {
  itemDialogTitle.value = '编辑项目'
  Object.assign(itemForm, row)
  itemDialogVisible.value = true
}

// 提交项目表单
const submitItemForm = async () => {
  if (!itemForm.item_name || !itemForm.item_code) {
    ElMessage.warning('请填写必填字段')
    return
  }

  try {
    if (itemForm.id) {
      await request.put(`/salary/items/config/${itemForm.id}`, itemForm)
      ElMessage.success('更新成功')
    } else {
      await request.post('/salary/items/config', itemForm)
      ElMessage.success('添加成功')
    }
    itemDialogVisible.value = false
    loadSalaryItems()
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.response?.data?.error || error.message))
  }
}

// 删除项目
const handleDeleteItem = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此工资项目吗?', '提示', {
      type: 'warning'
    })
    await request.delete(`/salary/items/config/${id}`)
    ElMessage.success('删除成功')
    loadSalaryItems()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 获取项目类型颜色
const getItemTypeColor = (type) => {
  const colorMap = {
    '固定项': 'success',
    '浮动项': 'warning',
    '扣款项': 'danger'
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

// 加载配置数据
const loadConfigData = async () => {
  try {
    const [taxRes, ssRes, catRes] = await Promise.all([
      request.get('/salary/tax-brackets'),
      request.get('/salary/social-security/config'),
      request.get('/salary/categories')
    ])
    taxBrackets.value = taxRes
    ssConfig.value = ssRes
    categories.value = catRes
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

onMounted(() => {
  loadEmployees()
  loadSalaryItems()
  loadConfigData()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.search-form { margin-bottom: 20px; }
.toolbar { margin-bottom: 20px; }
.salary-result { margin-top: 20px; }
.section-title {
  font-size: 16px;
  font-weight: bold;
  margin: 15px 0 10px 0;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}
.amount-positive {
  color: #67c23a;
  font-weight: bold;
}
.amount-negative {
  color: #f56c6c;
  font-weight: bold;
}
.amount-net {
  color: #409eff;
  font-weight: bold;
  font-size: 18px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
