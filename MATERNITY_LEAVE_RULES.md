# 产假规则说明(医院专用)

## 📅 更新日期
2026-06-29 19:30

---

## 🎯 产假天数计算规则

### 基础规定

根据《女职工劳动保护特别规定》和云南省地方政策:

| 项目 | 天数 | 说明 |
|------|------|------|
| **基础产假** | **158天** | 国家标准98天 + 云南省奖励60天 |
| **难产/剖腹产** | **+15天** | 增加产假15天 |
| **多胞胎** | **+15天/胎** | 每多生育1个婴儿,增加产假15天 |

---

## 📊 计算公式

```
总产假天数 = 基础产假(158天) + 额外天数

额外天数 = 难产奖励(0或15天) + 多胞胎奖励((胎儿数-1) × 15天)
```

---

## 💡 计算示例

### 示例1: 顺产单胎
```
生产类型: 顺产
胎儿数量: 1胎

计算:
- 基础产假: 158天
- 难产奖励: 0天
- 多胞胎奖励: 0天
━━━━━━━━━━━━━━━━━━━━━
总计: 158天
```

### 示例2: 剖腹产单胎
```
生产类型: 剖腹产
胎儿数量: 1胎

计算:
- 基础产假: 158天
- 难产奖励: +15天 (剖腹产)
- 多胞胎奖励: 0天
━━━━━━━━━━━━━━━━━━━━━
总计: 173天
```

### 示例3: 顺产双胞胎
```
生产类型: 顺产
胎儿数量: 2胎

计算:
- 基础产假: 158天
- 难产奖励: 0天
- 多胞胎奖励: +15天 (第2胎)
━━━━━━━━━━━━━━━━━━━━━
总计: 173天
```

### 示例4: 剖腹产双胞胎
```
生产类型: 剖腹产
胎儿数量: 2胎

计算:
- 基础产假: 158天
- 难产奖励: +15天 (剖腹产)
- 多胞胎奖励: +15天 (第2胎)
━━━━━━━━━━━━━━━━━━━━━
总计: 188天
```

### 示例5: 顺产三胞胎
```
生产类型: 顺产
胎儿数量: 3胎

计算:
- 基础产假: 158天
- 难产奖励: 0天
- 多胞胎奖励: +30天 (第2胎+第3胎)
━━━━━━━━━━━━━━━━━━━━━
总计: 188天
```

### 示例6: 剖腹产三胞胎
```
生产类型: 剖腹产
胎儿数量: 3胎

计算:
- 基础产假: 158天
- 难产奖励: +15天 (剖腹产)
- 多胞胎奖励: +30天 (第2胎+第3胎)
━━━━━━━━━━━━━━━━━━━━━
总计: 203天
```

---

## 🔧 系统实现

### 数据库字段

**表:** `leave_requests` (请假申请表)

**新增字段:**
```sql
birth_type TEXT,                     -- 生产类型(顺产/难产/剖腹产)
is_multiple_birth INTEGER DEFAULT 0, -- 是否多胞胎(0/1)
multiple_count INTEGER DEFAULT 1,    -- 胎儿数量
extra_days REAL DEFAULT 0,           -- 额外天数
```

### Python计算函数

**文件:** `utils/attendance_calculator.py`

```python
def calculate_maternity_leave_days(birth_type, is_multiple_birth, multiple_count):
    """
    计算产假天数(医院专用)
    
    Args:
        birth_type: 生产类型(顺产/难产/剖腹产)
        is_multiple_birth: 是否多胞胎(0/1)
        multiple_count: 胎儿数量
    
    Returns:
        dict: {
            'base_days': 158,          # 基础产假
            'extra_days': 15,          # 额外天数
            'total_days': 173,         # 总天数
            'calculation': '158+15',   # 计算说明
            'reasons': ['难产/剖腹产+15天']  # 原因列表
        }
    """
    base_days = 158  # 基础产假
    extra_days = 0
    reasons = []
    
    # 难产/剖腹产 +15天
    if birth_type in ['难产', '剖腹产']:
        extra_days += 15
        reasons.append('难产/剖腹产+15天')
    
    # 多胞胎 每多一胎 +15天
    if is_multiple_birth and multiple_count > 1:
        additional = (multiple_count - 1) * 15
        extra_days += additional
        reasons.append(f'多胞胎({multiple_count}胎)+{additional}天')
    
    total_days = base_days + extra_days
    
    calculation = f"{base_days}"
    if extra_days > 0:
        calculation += f"+{extra_days}"
    
    return {
        'base_days': base_days,
        'extra_days': extra_days,
        'total_days': total_days,
        'calculation': calculation,
        'reasons': reasons
    }
```

### 前端表单逻辑

**文件:** `frontend/src/views/Attendance.vue`

**Tab 2: 请假管理**

```vue
<!-- 选择请假类型 -->
<el-form-item label="请假类型">
  <el-select v-model="leaveForm.leave_type" @change="handleLeaveTypeChange">
    <el-option label="事假" value="事假" />
    <el-option label="病假" value="病假" />
    <el-option label="年假" value="年假" />
    <el-option label="婚假" value="婚假" />
    <el-option label="产假" value="产假" />
    <el-option label="丧假" value="丧假" />
  </el-select>
</el-form-item>

<!-- 产假专用字段(仅当选择"产假"时显示) -->
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
  
  <!-- 自动计算结果显示 -->
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
        ({{ maternityCalculation.calculation }})
      </p>
    </template>
  </el-alert>
</template>
```

**计算方法:**
```javascript
const maternityCalculation = computed(() => {
  if (leaveForm.leave_type !== '产假') return null
  
  return calculateMaternityLeaveDays(
    leaveForm.birth_type,
    leaveForm.is_multiple_birth,
    leaveForm.multiple_count || 1
  )
})

// 自动填充请假天数
watch(maternityCalculation, (calc) => {
  if (calc) {
    leaveForm.days = calc.total_days
  }
})
```

---

## ✅ 验证规则

### 前端验证

1. **生产类型必填**
   - 必须选择: 顺产 / 难产 / 剖腹产

2. **胎儿数量验证**
   - 如果选择"多胞胎",胎儿数量必须 ≥ 2
   - 最大值限制为10

3. **请假天数验证**
   - 自动计算的起止日期天数应与产假天数一致
   - 允许误差: ±1天(考虑跨月情况)

### 后端验证

```python
def validate_maternity_leave(data):
    """验证产假申请"""
    errors = []
    
    # 验证生产类型
    if data['birth_type'] not in ['顺产', '难产', '剖腹产']:
        errors.append('生产类型无效')
    
    # 验证胎儿数量
    if data['is_multiple_birth'] and data['multiple_count'] < 2:
        errors.append('多胞胎胎儿数量必须≥2')
    
    # 计算预期天数
    calc = calculate_maternity_leave_days(
        data['birth_type'],
        data['is_multiple_birth'],
        data['multiple_count']
    )
    
    # 验证请假天数
    actual_days = (end_date - start_date).days + 1
    if abs(actual_days - calc['total_days']) > 1:
        errors.append(f'请假天数({actual_days}天)与产假天数({calc["total_days"]}天)不符')
    
    return errors
```

---

## 📋 审批流程

### 产假审批特殊要求

1. **必须上传证明材料**
   - 医院诊断证明
   - 出生医学证明(产后补交)
   - 剖腹产手术记录(如适用)

2. **审批人权限**
   - 科室主任: 初审
   - 人事科: 复核假期天数计算
   - 院领导: 最终审批(超过180天需院领导审批)

3. **假期余额检查**
   - 产假不计入年假余额
   - 产假期间工资按国家规定发放
   - 社保正常缴纳

---

## 📊 统计报表

### 产假统计维度

1. **月度统计**
   - 当月休产假人数
   - 平均产假天数
   - 各科室分布

2. **年度统计**
   - 全年休产假总人次
   - 顺产/剖腹产比例
   - 多胞胎比例

3. **趋势分析**
   - 月度产假人数趋势图
   - 产假天数分布直方图

---

## ⚠️ 注意事项

### 法律合规

1. **产假期间待遇**
   - 工资照发(基本工资+绩效工资)
   - 社保正常缴纳
   - 不影响年终考核

2. **返岗安排**
   - 产假结束后应按时返岗
   - 如需延长,需提交延期申请
   - 哺乳时间按规定执行

3. **特殊情况**
   - 流产: 怀孕未满4个月流产的,享受15天产假
   - 怀孕满4个月流产的,享受42天产假
   - 死胎、死产参照流产处理

---

## 🔗 相关文档

- [考勤管理模块实施计划](./PERFORMANCE_ATTENDANCE_PLAN.md)
- [请假管理规定](待补充)
- [女职工劳动保护规定](国家法规)

---

**版本:** v1.0  
**更新日期:** 2026-06-29  
**适用范围:** 大理大学第一附属医院
