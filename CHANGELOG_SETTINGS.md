# 系统设置功能更新日志

## 📅 更新日期
2026-06-29

## 🎯 更新概述

在系统设置页面新增了三个核心管理模块,用于配置和管理系统的自定义字段、工资项目和绩效管理项目。

---

## ✨ 新增功能

### 1. 自定义字段管理

**功能描述:**
允许管理员为职工信息添加动态扩展字段,支持不同科室/岗位配置不同的自定义字段。

**主要特性:**
- ✅ 支持5种字段类型: 文本、数字、日期、下拉选择、多行文本
- ✅ 可按科室配置字段适用范围
- ✅ 支持必填/选填设置
- ✅ 支持字段排序和启用/禁用控制
- ✅ 下拉选择字段支持自定义选项列表

**数据库表:**
- `custom_fields` - 自定义字段定义表
- `employee_custom_data` - 职工自定义数据表

**API接口:**
- `GET /api/custom-fields` - 获取自定义字段列表
- `POST /api/custom-fields` - 创建自定义字段
- `PUT /api/custom-fields/<id>` - 更新自定义字段
- `DELETE /api/custom-fields/<id>` - 删除自定义字段
- `GET /api/employees/<emp_id>/custom-data` - 获取职工自定义数据
- `PUT /api/employees/<emp_id>/custom-data` - 更新职工自定义数据

**使用场景:**
- 为医生添加"执业证书编号"、"专业方向"等字段
- 为护士添加"护理等级"、"专科资质"等字段
- 为行政人员添加"办公地点"、"分管领域"等字段

---

### 2. 工资项目管理

**功能描述:**
管理工资核算中的各项工资项目配置,支持固定项、浮动项、扣款项等多种类型。

**主要特性:**
- ✅ 支持3种项目类型: 固定项、浮动项、扣款项
- ✅ 支持3种计算方式: 固定值、公式、百分比
- ✅ 可配置是否计税、是否在工资条显示
- ✅ 支持按科室/职称设置默认值
- ✅ 支持项目排序和启用/禁用控制

**数据库表:**
- `salary_items` - 工资项目表
- `salary_item_defaults` - 工资项目默认值表

**API接口:**
- `GET /api/salary-items` - 获取工资项目列表(含默认值)
- `POST /api/salary-items` - 创建工资项目
- `PUT /api/salary-items/<id>` - 更新工资项目
- `DELETE /api/salary-items/<id>` - 删除工资项目
- `GET /api/salary-items/<id>/defaults` - 获取项目默认值
- `POST /api/salary-items/<id>/defaults` - 设置项目默认值

**典型工资项目:**
```
收入项目:
- 基本工资 (固定项)
- 岗位津贴 (固定项)
- 医疗补贴 (固定项)
- 住房补贴 (固定项)
- 夜班补贴 (浮动项)
- 加班费 (浮动项)
- 绩效奖金 (浮动项)

扣款项目:
- 养老保险 (扣款项)
- 医疗保险 (扣款项)
- 失业保险 (扣款项)
- 住房公积金 (扣款项)
- 个人所得税 (扣款项)
```

---

### 3. 绩效管理分类

**功能描述:**
建立绩效考核的分类体系,支持多维度、多指标的量化考核。

**主要特性:**
- ✅ 支持创建多个绩效分类(如工作业绩、服务质量等)
- ✅ 每个分类下可配置多个考核指标
- ✅ 支持分类和指标的权重分配
- ✅ 支持3种评分方式: 百分制、等级制、定量
- ✅ 采用软删除机制,保留历史数据

**数据库表:**
- `perf_categories` - 绩效分类表
- `perf_indicators` - 绩效指标表

**API接口:**
- `GET /api/perf-categories` - 获取绩效分类列表(含指标)
- `POST /api/perf-categories` - 创建绩效分类
- `PUT /api/perf-categories/<id>` - 更新绩效分类
- `DELETE /api/perf-categories/<id>` - 删除绩效分类(软删除)
- `GET /api/perf-indicators` - 获取绩效指标列表
- `POST /api/perf-indicators` - 创建绩效指标
- `PUT /api/perf-indicators/<id>` - 更新绩效指标
- `DELETE /api/perf-indicators/<id>` - 删除绩效指标(软删除)

**典型绩效体系:**
```
📊 医生绩效考核体系 (总分100分)

├─ 工作业绩 (40%)
│  ├─ 门诊量 (30%)
│  ├─ 住院患者数 (25%)
│  ├─ 手术台数 (25%)
│  └─ 病历质量 (20%)
│
├─ 服务质量 (30%)
│  ├─ 患者满意度 (40%)
│  ├─ 医疗差错率 (30%)
│  └─ 投诉次数 (30%)
│
├─ 教学科研 (20%)
│  ├─ 发表论文数 (40%)
│  ├─ 科研项目 (30%)
│  └─ 带教课时 (30%)
│
└─ 医德医风 (10%)
   ├─ 职业道德评价 (50%)
   └─ 劳动纪律 (50%)
```

---

## 📝 代码变更统计

### 后端变更 (app.py)

**新增数据库表:** 6个
- `custom_fields` - 自定义字段定义
- `employee_custom_data` - 职工自定义数据
- `salary_items` - 工资项目
- `salary_item_defaults` - 工资项目默认值
- `perf_categories` - 绩效分类
- `perf_indicators` - 绩效指标

**新增API路由:** 18个
- 自定义字段: 6个接口
- 工资项目: 6个接口
- 绩效管理: 6个接口

**代码行数:** 约 +240行

### 前端变更 (main.js)

**新增函数:** 15个
- `loadCustomFields()` - 加载自定义字段列表
- `showAddCustomField()` - 显示新增字段对话框
- `saveCustomField()` - 保存自定义字段
- `editCustomField()` - 编辑自定义字段
- `deleteCustomField()` - 删除自定义字段
- `loadSalaryItems()` - 加载工资项目列表
- `showAddSalaryItem()` - 显示新增项目对话框
- `saveSalaryItem()` - 保存工资项目
- `editSalaryItem()` - 编辑工资项目
- `deleteSalaryItem()` - 删除工资项目
- `loadPerfCategories()` - 加载绩效分类列表
- `showAddPerfCategory()` - 显示新增分类对话框
- `savePerfCategory()` - 保存绩效分类
- `editPerfCategory()` - 编辑绩效分类
- `deletePerfCategory()` - 删除绩效分类
- `showAddPerfIndicator()` - 显示新增指标对话框
- `savePerfIndicator()` - 保存绩效指标

**修改函数:** 1个
- `loadSettings()` - 增加三个新模块的UI和初始化调用

**代码行数:** 约 +420行

### 文档新增

- `SETTINGS_FEATURES_GUIDE.md` - 详细功能说明文档 (316行)
- `QUICK_START_SETTINGS.md` - 快速上手指南 (347行)
- `CHANGELOG_SETTINGS.md` - 本更新日志

### 测试脚本

- `test_settings_features.py` - API功能测试脚本 (144行)

---

## 🔧 技术实现细节

### 1. 数据库设计原则

**唯一性约束:**
- `field_code` - 字段编码唯一
- `item_code` - 项目编码唯一
- `category_code` - 分类编码唯一
- `indicator_code` - 指标编码唯一

**外键关联:**
- `employee_custom_data.emp_id` → `employees.id`
- `employee_custom_data.field_id` → `custom_fields.id`
- `salary_item_defaults.item_id` → `salary_items.id`
- `perf_indicators.category_id` → `perf_categories.id`

**软删除策略:**
- 绩效分类和指标使用 `is_active` 字段标记状态
- 删除时设置为0而非物理删除,保留历史数据

### 2. 权限控制

所有新增API都使用了 `@require_permission` 装饰器:
- 自定义字段: `personnel.write`
- 工资项目: `salary.write`
- 绩效管理: `performance.write`

### 3. 输入验证

- 必填字段检查 (名称、编码)
- 编码唯一性检查 (捕获IntegrityError)
- 数值范围验证 (权重0-100)
- 数据类型转换 (int/float)

### 4. 前端交互

**模态框表单:**
- 统一的 `showModal()` 函数
- 动态生成表单HTML
- 实时数据绑定

**列表展示:**
- 表格形式展示
- 状态标签化显示 (tag-success/tag-warning/tag-danger)
- 操作按钮 (编辑/删除)

**错误处理:**
- API错误提示 (alert)
- 确认对话框 (confirm)
- 成功自动刷新列表

---

## 📊 性能优化

### 1. 数据库索引

虽然没有为新增表添加额外索引,但以下字段已隐含索引:
- `PRIMARY KEY` - 主键自动索引
- `UNIQUE` - 唯一约束自动索引
- `FOREIGN KEY` - 外键在某些情况下有索引

### 2. 查询优化

**自定义字段查询:**
```sql
-- 按科室过滤
SELECT * FROM custom_fields 
WHERE (department=? OR department IS NULL) AND is_active=1 
ORDER BY sort_order
```

**工资项目查询:**
```sql
-- 一次性加载项目和默认值
SELECT * FROM salary_items ORDER BY sort_order, id;
SELECT * FROM salary_item_defaults WHERE item_id=?;
```

**绩效分类查询:**
```sql
-- 嵌套查询加载指标
SELECT * FROM perf_categories WHERE is_active=1 ORDER BY sort_order, id;
SELECT * FROM perf_indicators WHERE category_id=? AND is_active=1 ORDER BY sort_order;
```

---

## ⚠️ 注意事项

### 1. 数据完整性

- **编码唯一性**: 确保 field_code、item_code、category_code、indicator_code 全局唯一
- **外键约束**: 删除父记录前需确认子记录已处理
- **权重总和**: 建议同一分类下的指标权重总和为100%

### 2. 兼容性

- **向后兼容**: 现有功能不受影响
- **数据迁移**: 无需迁移现有数据
- **API版本**: 当前为v1版本,未来可能升级

### 3. 安全性

- **SQL注入防护**: 所有查询使用参数化语句
- **XSS防护**: 前端使用 escHtml() 转义输出
- **权限验证**: 所有写操作需要相应权限

### 4. 已知限制

- ❌ 工资项目默认值设置暂不支持前端界面,需通过API
- ❌ 自定义字段暂不支持批量导入
- ❌ 绩效模板管理尚未实现
- ❌ 缺少配置变更历史记录

---

## 🚀 后续计划

### 短期计划 (1-2周)

1. **前端优化:**
   - [ ] 添加工资项目默认值设置界面
   - [ ] 优化表单验证和错误提示
   - [ ] 添加加载状态和进度提示

2. **功能增强:**
   - [ ] 自定义字段批量导入/导出
   - [ ] 工资项目预设模板
   - [ ] 绩效模板管理

### 中期计划 (1-2月)

1. **数据分析:**
   - [ ] 工资项目统计分析
   - [ ] 绩效指标得分分析
   - [ ] 自定义字段使用情况统计

2. **高级功能:**
   - [ ] 配置变更历史记录
   - [ ] 配置版本管理
   - [ ] 配置导入/导出 (Excel)

### 长期计划 (3-6月)

1. **智能化:**
   - [ ] 基于历史数据的智能推荐
   - [ ] 异常配置检测
   - [ ] 自动化配置优化建议

2. **集成扩展:**
   - [ ] 与考勤系统集成
   - [ ] 与财务系统集成
   - [ ] 与HIS系统集成

---

## 📞 反馈与支持

如有问题或建议,请:
1. 查看完整文档: `SETTINGS_FEATURES_GUIDE.md`
2. 参考快速指南: `QUICK_START_SETTINGS.md`
3. 运行测试脚本: `python test_settings_features.py`

---

**更新完成时间:** 2026-06-29  
**版本号:** v1.0.0  
**更新人员:** AI Assistant
