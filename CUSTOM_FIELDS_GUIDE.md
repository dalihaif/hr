# 职工管理 - 自定义字段功能使用指南

## 📅 更新日期
2026-06-29 17:30

---

## ✅ 功能概述

职工管理模块现已支持**自定义字段扩展**,允许医院根据不同科室的需求,动态添加职工信息项目,无需修改数据库结构。

---

## 🎯 核心功能

### 1. 自定义字段管理

管理员可以创建、编辑、删除自定义字段,支持以下类型:

| 字段类型 | 说明 | 适用场景 |
|---------|------|---------|
| **文本** | 单行文本输入 | 证书编号、身份证号等 |
| **数字** | 数值输入 | 工龄、职称等级等 |
| **日期** | 日期选择器 | 入职日期、执业日期等 |
| **下拉选择** | 从预设选项中选择 | 学历、专业类别等 |
| **多行文本** | 多行文本域 | 备注、工作经历等 |

### 2. 科室适配

可以为不同科室设置不同的自定义字段:
- **全部科室**: 不设置科室限制,所有职工都显示
- **指定科室**: 仅该科室的职工显示此字段

### 3. 必填控制

可以设置字段是否为必填项,确保关键信息的完整性。

### 4. 排序管理

通过排序值控制字段的显示顺序,重要的字段排在前面。

---

## 📖 使用步骤

### 步骤1: 进入自定义字段管理

1. 登录系统 (http://localhost:5174)
2. 点击左侧菜单 **职工管理**
3. 在职工列表页面,点击 **自定义字段管理** 按钮
4. 或直接切换到 **自定义字段** Tab页

### 步骤2: 创建自定义字段

点击 **新增字段** 按钮,填写表单:

**示例1: 创建"执业证书编号"字段**
```
字段名称: 执业证书编号
字段编码: certificate_no
字段类型: 文本
适用科室: 全部
是否必填: 是
排序: 1
```

**示例2: 创建"学历"字段(下拉选择)**
```
字段名称: 学历
字段编码: education
字段类型: 下拉选择
选项值: 
  大专
  本科
  硕士
  博士
适用科室: 全部
是否必填: 是
排序: 2
```

**示例3: 创建"专科方向"字段(仅内科)**
```
字段名称: 专科方向
字段编码: specialty
字段类型: 下拉选择
选项值:
  心血管内科
  呼吸内科
  消化内科
  神经内科
适用科室: 内科
是否必填: 否
排序: 3
```

**示例4: 创建"执业日期"字段**
```
字段名称: 首次执业日期
字段编码: first_practice_date
字段类型: 日期
适用科室: 全部
是否必填: 否
排序: 4
```

### 步骤3: 为职工填写自定义信息

1. 在职工列表中,找到目标职工
2. 点击 **自定义信息** 按钮
3. 在弹出的对话框中,填写该职工的自定义字段值
4. 点击 **保存**

**注意:**
- 只会显示适用于该职工科室的字段
- 必填字段必须填写才能保存
- 可以随时修改已填写的信息

### 步骤4: 查看和管理

- **查看**: 随时点击职工的"自定义信息"按钮查看
- **编辑**: 在自定义信息对话框中修改后保存
- **删除字段**: 在自定义字段管理中删除字段(不影响已保存的数据)

---

## 💡 应用场景示例

### 场景1: 医生信息管理

**需要添加的字段:**
1. 执业医师证号 (文本, 必填)
2. 执业范围 (下拉: 内科/外科/妇产科/儿科等)
3. 职称取得日期 (日期)
4. 专科方向 (下拉, 根据科室不同而不同)
5. 门诊时间 (多行文本)

### 场景2: 护士信息管理

**需要添加的字段:**
1. 护士执业证号 (文本, 必填)
2. 护理级别 (下拉: N0/N1/N2/N3/N4)
3. 专科护士认证 (下拉: 是/否)
4. 擅长领域 (多行文本)

### 场景3: 医技人员信息

**需要添加的字段:**
1. 技师资格证号 (文本)
2. 设备操作资质 (下拉: CT/MRI/超声/X光等)
3. 工作年限 (数字)

### 场景4: 行政人员信息

**需要添加的字段:**
1. 管理岗位级别 (下拉)
2. 负责部门 (文本)
3. 办公电话 (文本)

---

## 🔧 技术实现

### 数据库设计

**custom_fields 表** - 存储自定义字段定义
```sql
CREATE TABLE custom_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_name TEXT NOT NULL,        -- 字段名称
    field_code TEXT NOT NULL UNIQUE, -- 字段编码(唯一)
    field_type TEXT NOT NULL,        -- 字段类型
    options TEXT,                    -- 选项值(JSON数组)
    department TEXT,                 -- 适用科室(NULL=全部)
    is_required INTEGER DEFAULT 0,   -- 是否必填
    sort_order INTEGER DEFAULT 0,    -- 排序
    is_active INTEGER DEFAULT 1,     -- 是否启用
    created_at TEXT                  -- 创建时间
);
```

**employee_custom_data 表** - 存储职工的自定义字段值
```sql
CREATE TABLE employee_custom_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,         -- 职工ID
    field_id INTEGER NOT NULL,       -- 字段ID
    field_value TEXT,                -- 字段值
    updated_at TEXT,                 -- 更新时间
    FOREIGN KEY (emp_id) REFERENCES employees(id),
    FOREIGN KEY (field_id) REFERENCES custom_fields(id),
    UNIQUE(emp_id, field_id)
);
```

### API接口

**1. 获取自定义字段列表**
```
GET /api/custom-fields?department=内科
```

**2. 创建自定义字段**
```
POST /api/custom-fields
{
  "field_name": "执业证书编号",
  "field_code": "certificate_no",
  "field_type": "text",
  "options": null,
  "department": null,
  "is_required": 1,
  "sort_order": 1
}
```

**3. 更新自定义字段**
```
PUT /api/custom-fields/{id}
{
  "field_name": "新名称",
  "is_required": 0
}
```

**4. 删除自定义字段(软删除)**
```
DELETE /api/custom-fields/{id}
```

**5. 获取职工的自定义数据**
```
GET /api/employees/{emp_id}/custom-data
```

**6. 保存职工的自定义数据**
```
PUT /api/employees/{emp_id}/custom-data
{
  "certificate_no": "123456789",
  "education": "本科",
  "first_practice_date": "2020-01-01"
}
```

---

## ⚠️ 注意事项

### 1. 字段编码规范

- 使用英文小写字母和下划线
- 不能包含空格和特殊字符
- 建议见名知意,如: `certificate_no`, `education`
- 一旦创建,不建议修改编码

### 2. 删除字段的影响

- 删除字段只是**软删除**(设置is_active=0)
- 已保存的自定义数据不会被删除
- 该字段不再显示在新职工或编辑界面
- 历史数据仍然可以通过API查询

### 3. 修改字段类型

- **不建议**修改已有字段的类型
- 可能导致已保存的数据格式不匹配
- 如需修改,建议删除后重新创建

### 4. 科室适配

- 如果字段设置为"全部科室",所有职工都能看到
- 如果指定了科室,只有该科室的职工能看到
- 可以为同一字段创建多个科室版本

### 5. 必填字段

- 必填字段在保存时必须填写
- 建议在创建时就确定是否必填
- 后期修改必填状态不影响已有数据

---

## 🎨 界面截图说明

### 1. 职工列表页面
- 顶部: 搜索栏 + 操作按钮
- 中部: 职工数据表格
- 底部: 分页控件
- 操作列: 编辑 | 自定义信息 | 删除

### 2. 自定义字段管理Tab
- 字段列表表格
- 显示: 名称、编码、类型、适用科室、必填、排序
- 操作: 编辑、删除

### 3. 自定义信息对话框
- 标题: 显示职工姓名
- 表单: 动态生成,根据字段类型显示不同控件
- 底部: 取消、保存按钮

---

## 🚀 最佳实践

### 1. 规划先行

在创建字段前,先规划好:
- 需要哪些字段
- 字段类型是什么
- 哪些科室需要
- 是否必填
- 排序顺序

### 2. 命名规范

**字段名称:** 使用中文,清晰易懂
- ✅ 执业证书编号
- ❌ cert_no

**字段编码:** 使用英文,简洁明了
- ✅ certificate_no
- ❌ zhiye_zhengshu_bianhao

### 3. 分科室管理

不同科室可能有不同的信息需求:
- 医生: 执业信息、专科方向
- 护士: 护理级别、专科认证
- 医技: 设备资质、技术等级
- 行政: 管理级别、职责范围

### 4. 定期维护

- 定期检查字段使用情况
- 清理不再使用的字段
- 根据业务变化调整字段

### 5. 权限控制

- 只有管理员可以管理自定义字段
- 科室主任可以查看本科室职工的自定义信息
- 职工本人可以查看自己的信息

---

## 📊 数据统计

可以通过自定义字段进行统计分析:

**示例SQL查询:**
```sql
-- 统计各学历人数
SELECT ecd.field_value as education, COUNT(*) as count
FROM employee_custom_data ecd
JOIN custom_fields cf ON ecd.field_id = cf.id
WHERE cf.field_code = 'education'
GROUP BY ecd.field_value;

-- 查询某专科方向的医生
SELECT e.name, ecd.field_value as specialty
FROM employees e
JOIN employee_custom_data ecd ON e.id = ecd.emp_id
JOIN custom_fields cf ON ecd.field_id = cf.id
WHERE cf.field_code = 'specialty'
  AND ecd.field_value = '心血管内科';
```

---

## 🔗 相关文档

- [API文档](file://e:\my-web\hospital-hr\API_DOCUMENTATION.md)
- [Vue前端报告](file://e:\my-web\hospital-hr\VUE_COMPLETION_REPORT.md)
- [项目总结](file://e:\my-web\hospital-hr\PROJECT_SUMMARY.md)

---

## ❓ 常见问题

### Q1: 如何批量导入自定义字段值?

目前需要通过API逐个设置,后续可以增加Excel导入功能。

### Q2: 自定义字段会影响性能吗?

不会。自定义字段采用关联表存储,查询效率高。

### Q3: 可以导出包含自定义字段的Excel吗?

可以。后端API已支持,前端可以添加导出选项。

### Q4: 如何备份自定义字段配置?

自定义字段存储在数据库中,随数据库一起备份。

### Q5: 字段编码写错了怎么办?

可以删除后重新创建,但已保存的数据需要重新录入。

---

**文档版本:** v1.0  
**更新时间:** 2026-06-29  
**适用系统:** 医院人事管理系统 Vue前端

🎉 **自定义字段功能已完全实现,可以投入使用!** 🎉
