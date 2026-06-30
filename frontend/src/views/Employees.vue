<template>
  <div class="page-container">
    <el-card>
      <!-- Tab切换 -->
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 职工列表 -->
        <el-tab-pane label="职工列表" name="employees">
          <!-- 搜索栏 -->
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="姓名">
              <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
            </el-form-item>
            <el-form-item label="科室">
              <el-select v-model="searchForm.department" placeholder="请选择科室" clearable>
                <el-option label="内科" value="内科" />
                <el-option label="外科" value="外科" />
                <el-option label="护理部" value="护理部" />
                <el-option label="医技科" value="医技科" />
                <el-option label="行政" value="行政" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 操作按钮 -->
          <div class="toolbar">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>新增职工
            </el-button>
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon>导出Excel
            </el-button>
            <el-button type="warning" @click="showCustomFieldManager">
              <el-icon><Setting /></el-icon>自定义字段管理
            </el-button>
          </div>

          <!-- 数据表格 -->
          <el-table
            :data="tableData"
            border
            stripe
            style="width: 100%"
            v-loading="loading"
          >
            <el-table-column prop="emp_no" label="工号" width="120" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="gender" label="性别" width="80" />
            <el-table-column prop="current_dept" label="科室" width="150" />
            <el-table-column prop="current_position" label="岗位" width="150" />
            <el-table-column prop="current_title" label="职称" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '在职' ? 'success' : 'info'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="250">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
                <el-button size="small" @click="viewCustomData(row)">自定义信息</el-button>
                <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-tab-pane>

        <!-- 自定义字段管理 -->
        <el-tab-pane label="自定义字段" name="customFields">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddCustomField">
              <el-icon><Plus /></el-icon>新增字段
            </el-button>
          </div>

          <el-table :data="customFields" border stripe>
            <el-table-column prop="field_name" label="字段名称" width="150" />
            <el-table-column prop="field_code" label="字段编码" width="150" />
            <el-table-column prop="field_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.field_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="department" label="适用科室" width="120">
              <template #default="{ row }">
                {{ row.department || '全部' }}
              </template>
            </el-table-column>
            <el-table-column prop="is_required" label="必填" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_required ? 'danger' : 'info'">
                  {{ row.is_required ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sort_order" label="排序" width="80" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="handleEditCustomField(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteCustomField(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 职工编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
    >
      <el-form :model="formData" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" required>
              <el-input v-model="formData.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-radio-group v-model="formData.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="科室">
              <el-select v-model="formData.current_dept">
                <el-option label="内科" value="内科" />
                <el-option label="外科" value="外科" />
                <el-option label="护理部" value="护理部" />
                <el-option label="医技科" value="医技科" />
                <el-option label="行政" value="行政" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="岗位">
              <el-input v-model="formData.current_position" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职称">
              <el-input v-model="formData.current_title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="formData.status">
                <el-option label="在职" value="在职" />
                <el-option label="离职" value="离职" />
                <el-option label="退休" value="退休" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 自定义字段编辑对话框 -->
    <el-dialog
      v-model="customFieldDialogVisible"
      :title="customFieldDialogTitle"
      width="600px"
    >
      <el-form :model="customFieldForm" label-width="100px">
        <el-form-item label="字段名称" required>
          <el-input v-model="customFieldForm.field_name" placeholder="如：执业证书编号" />
        </el-form-item>
        <el-form-item label="字段编码" required>
          <el-input v-model="customFieldForm.field_code" placeholder="如：certificate_no" />
        </el-form-item>
        <el-form-item label="字段类型" required>
          <el-select v-model="customFieldForm.field_type">
            <el-option label="文本" value="text" />
            <el-option label="数字" value="number" />
            <el-option label="日期" value="date" />
            <el-option label="下拉选择" value="select" />
            <el-option label="多行文本" value="textarea" />
          </el-select>
        </el-form-item>
        <el-form-item label="选项值" v-if="customFieldForm.field_type === 'select'">
          <el-input
            v-model="customFieldForm.options_text"
            type="textarea"
            :rows="3"
            placeholder="每行一个选项，如：&#10;医师&#10;护士&#10;药师"
          />
        </el-form-item>
        <el-form-item label="适用科室">
          <el-select v-model="customFieldForm.department" clearable placeholder="不选则适用全部">
            <el-option label="内科" value="内科" />
            <el-option label="外科" value="外科" />
            <el-option label="护理部" value="护理部" />
            <el-option label="医技科" value="医技科" />
            <el-option label="行政" value="行政" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否必填">
          <el-switch v-model="customFieldForm.is_required" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="customFieldForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="customFieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCustomField">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看/编辑自定义数据对话框 -->
    <el-dialog
      v-model="customDataDialogVisible"
      :title="`自定义信息 - ${currentEmployee?.name || ''}`"
      width="700px"
    >
      <el-form :model="customDataForm" label-width="150px">
        <el-form-item
          v-for="field in applicableCustomFields"
          :key="field.field_code"
          :label="field.field_name"
          :required="field.is_required"
        >
          <!-- 文本输入 -->
          <el-input
            v-if="field.field_type === 'text'"
            v-model="customDataForm[field.field_code]"
            :placeholder="`请输入${field.field_name}`"
          />
          
          <!-- 数字输入 -->
          <el-input-number
            v-else-if="field.field_type === 'number'"
            v-model="customDataForm[field.field_code]"
            style="width: 100%"
          />
          
          <!-- 日期选择 -->
          <el-date-picker
            v-else-if="field.field_type === 'date'"
            v-model="customDataForm[field.field_code]"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
          
          <!-- 下拉选择 -->
          <el-select
            v-else-if="field.field_type === 'select'"
            v-model="customDataForm[field.field_code]"
            placeholder="请选择"
            style="width: 100%"
          >
            <el-option
              v-for="opt in parseOptions(field.options)"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
          
          <!-- 多行文本 -->
          <el-input
            v-else-if="field.field_type === 'textarea'"
            v-model="customDataForm[field.field_code]"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        
        <el-empty v-if="applicableCustomFields.length === 0" description="暂无自定义字段" />
      </el-form>
      <template #footer>
        <el-button @click="customDataDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCustomData">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('employees')
const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增职工')

// 搜索表单
const searchForm = reactive({
  name: '',
  department: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 职工表单
const formData = reactive({
  id: null,
  name: '',
  gender: '男',
  current_dept: '',
  current_position: '',
  current_title: '',
  status: '在职'
})

// 自定义字段
const customFields = ref([])
const customFieldDialogVisible = ref(false)
const customFieldDialogTitle = ref('新增字段')
const customFieldForm = reactive({
  id: null,
  field_name: '',
  field_code: '',
  field_type: 'text',
  options_text: '',
  department: '',
  is_required: false,
  sort_order: 0
})

// 自定义数据
const customDataDialogVisible = ref(false)
const currentEmployee = ref(null)
const customDataForm = reactive({})

// 获取当前科室适用的自定义字段
const applicableCustomFields = computed(() => {
  if (!currentEmployee.value) return []
  const dept = currentEmployee.value.current_dept
  return customFields.value.filter(f => {
    return !f.department || f.department === dept
  })
})

// 加载职工列表
const loadData = async () => {
  loading.value = true
  try {
    const response = await request.get('/employees', {
      params: {
        ...searchForm,
        page: pagination.page,
        limit: pagination.pageSize
      }
    })
    tableData.value = response.data || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载自定义字段
const loadCustomFields = async () => {
  try {
    const response = await request.get('/custom-fields')
    customFields.value = response
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.department = ''
  handleSearch()
}

// 新增职工
const handleAdd = () => {
  dialogTitle.value = '新增职工'
  Object.assign(formData, {
    id: null,
    name: '',
    gender: '男',
    current_dept: '',
    current_position: '',
    current_title: '',
    status: '在职'
  })
  dialogVisible.value = true
}

// 编辑职工
const handleEdit = (row) => {
  dialogTitle.value = '编辑职工'
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除职工
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该职工吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/employees/${row.id}`)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交职工
const handleSubmit = async () => {
  try {
    if (formData.id) {
      await request.put(`/employees/${formData.id}`, formData)
      ElMessage.success('更新成功')
    } else {
      await request.post('/employees', formData)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 导出Excel
const handleExport = async () => {
  try {
    const response = await request.get('/employees/export', {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `职工列表_${new Date().getTime()}.xlsx`)
    link.click()
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 分页
const handleSizeChange = () => {
  loadData()
}

const handlePageChange = () => {
  loadData()
}

// 显示自定义字段管理
const showCustomFieldManager = () => {
  activeTab.value = 'customFields'
  loadCustomFields()
}

// 新增自定义字段
const handleAddCustomField = () => {
  customFieldDialogTitle.value = '新增字段'
  Object.assign(customFieldForm, {
    id: null,
    field_name: '',
    field_code: '',
    field_type: 'text',
    options_text: '',
    department: '',
    is_required: false,
    sort_order: 0
  })
  customFieldDialogVisible.value = true
}

// 编辑自定义字段
const handleEditCustomField = (row) => {
  customFieldDialogTitle.value = '编辑字段'
  Object.assign(customFieldForm, {
    ...row,
    options_text: Array.isArray(row.options) ? row.options.join('\n') : ''
  })
  customFieldDialogVisible.value = true
}

// 删除自定义字段
const handleDeleteCustomField = async (id) => {
  ElMessageBox.confirm('确定要删除该字段吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/custom-fields/${id}`)
      ElMessage.success('删除成功')
      loadCustomFields()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交自定义字段
const submitCustomField = async () => {
  try {
    // 解析选项
    let options = []
    if (customFieldForm.field_type === 'select' && customFieldForm.options_text) {
      options = customFieldForm.options_text.split('\n').filter(o => o.trim())
    }
    
    const data = {
      field_name: customFieldForm.field_name,
      field_code: customFieldForm.field_code,
      field_type: customFieldForm.field_type,
      options: options.length > 0 ? options : null,
      department: customFieldForm.department || null,
      is_required: customFieldForm.is_required ? 1 : 0,
      sort_order: customFieldForm.sort_order
    }
    
    if (customFieldForm.id) {
      await request.put(`/custom-fields/${customFieldForm.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await request.post('/custom-fields', data)
      ElMessage.success('添加成功')
    }
    customFieldDialogVisible.value = false
    loadCustomFields()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 查看自定义数据
const viewCustomData = async (row) => {
  currentEmployee.value = row
  
  // 加载该职工的自定义数据
  try {
    const response = await request.get(`/employees/${row.id}/custom-data`)
    // 填充表单
    Object.keys(customDataForm).forEach(key => delete customDataForm[key])
    for (const [code, data] of Object.entries(response)) {
      customDataForm[code] = data.field_value
    }
  } catch (error) {
    console.error('加载失败:', error)
  }
  
  customDataDialogVisible.value = true
}

// 保存自定义数据
const saveCustomData = async () => {
  if (!currentEmployee.value) return
  
  try {
    await request.put(`/employees/${currentEmployee.value.id}/custom-data`, customDataForm)
    ElMessage.success('保存成功')
    customDataDialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 解析选项
const parseOptions = (options) => {
  if (!options) return []
  return Array.isArray(options) ? options : []
}

onMounted(() => {
  loadData()
  loadCustomFields()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.search-form { margin-bottom: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
