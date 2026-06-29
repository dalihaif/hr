# 系统设置新功能使用说明

## 新增功能概述

在系统设置页面中新增了三个管理模块:

1. **自定义字段管理** - 管理职工信息的自定义字段
2. **工资项目管理** - 管理工资核算中的各项工资项目
3. **绩效管理分类** - 管理绩效考核的分类和指标

## 访问方式

1. 启动系统: `python app.py`
2. 访问: http://127.0.0.1:5000
3. 登录: admin / admin123
4. 点击左侧菜单"系统设置"

## 功能详细说明

### 1. 自定义字段管理

用于为不同科室/岗位的职工添加自定义信息字段。

#### 字段属性:
- **字段名称**: 显示名称,如"专业特长"
- **字段编码**: 唯一标识,如"specialty"
- **字段类型**: 
  - 文本 (text)
  - 数字 (number)
  - 日期 (date)
  - 下拉选择 (select)
  - 多行文本 (textarea)
- **适用科室**: 留空表示适用于所有科室
- **选项**: 仅下拉选择类型需要,用逗号分隔
- **是否必填**: 是/否
- **排序**: 数字越小越靠前
- **状态**: 启用/禁用

#### 使用场景:
- 为医生添加"执业证书编号"、"专业方向"等字段
- 为护士添加"护理等级"、"专科资质"等字段
- 为行政人员添加"办公地点"、"联系方式(备用)"等字段

### 2. 工资项目管理

管理工资核算中的各个工资项目配置。

#### 项目属性:
- **项目名称**: 显示名称,如"基本工资"
- **项目编码**: 唯一标识,如"base_salary"
- **项目类型**:
  - 固定项: 固定金额,如基本工资
  - 浮动项: 根据情况变化,如绩效奖金
  - 扣款项: 需要扣除的项目,如社保个人部分
- **计算方式**:
  - 固定值: 直接指定金额
  - 公式: 通过公式计算
  - 百分比: 按某个基数的百分比
- **计算公式**: 如"base*1.2"(可选)
- **是否计税**: 是/否
- **是否显示**: 是否在工资条中显示
- **排序**: 显示顺序
- **描述**: 项目说明

#### 默认工资项目示例:
- 基本工资 (固定项)
- 岗位津贴 (固定项)
- 医疗补贴 (固定项)
- 住房补贴 (固定项)
- 夜班补贴 (浮动项)
- 加班费 (浮动项)
- 绩效奖金 (浮动项)
- 养老保险 (扣款项)
- 医疗保险 (扣款项)
- 失业保险 (扣款项)
- 住房公积金 (扣款项)
- 个人所得税 (扣款项)

#### 使用场景:
- 根据不同职称设置不同的基本工资标准
- 为不同科室设置特殊的津贴项目
- 配置新的扣款项目(如企业年金)

### 3. 绩效管理分类

管理绩效考核的分类体系及其下属的考核指标。

#### 分类属性:
- **分类名称**: 如"工作业绩"
- **分类编码**: 如"work_performance"
- **权重**: 该分类在总分中的占比(%)
- **描述**: 分类说明
- **排序**: 显示顺序

#### 指标属性:
- **指标名称**: 如"门诊量"
- **指标编码**: 如"outpatient_count"
- **所属分类**: 归属的分类
- **评分方式**:
  - 百分制: 0-100分
  - 等级制: A/B/C/D/E
  - 定量: 具体数值
- **满分**: 最高分数
- **权重**: 该指标在分类中的占比(%)
- **描述**: 指标说明
- **排序**: 显示顺序

#### 典型绩效分类示例:

**1. 工作业绩 (权重40%)**
- 门诊量 (权重30%)
- 住院患者数 (权重25%)
- 手术台数 (权重25%)
- 病历质量 (权重20%)

**2. 服务质量 (权重30%)**
- 患者满意度 (权重40%)
- 医疗差错率 (权重30%)
- 投诉次数 (权重30%)

**3. 教学科研 (权重20%)**
- 发表论文数 (权重40%)
- 科研项目 (权重30%)
- 带教课时 (权重30%)

**4. 医德医风 (权重10%)**
- 职业道德评价 (权重50%)
- 劳动纪律 (权重50%)

#### 使用场景:
- 为不同岗位(医生/护士/行政)配置不同的考核指标
- 调整各指标的权重以反映工作重点
- 添加新的考核维度(如疫情防控表现)

## API接口清单

### 自定义字段API
- `GET /api/custom-fields` - 获取自定义字段列表
- `POST /api/custom-fields` - 创建自定义字段
- `PUT /api/custom-fields/<id>` - 更新自定义字段
- `DELETE /api/custom-fields/<id>` - 删除自定义字段
- `GET /api/employees/<emp_id>/custom-data` - 获取职工自定义数据
- `PUT /api/employees/<emp_id>/custom-data` - 更新职工自定义数据

### 工资项目API
- `GET /api/salary-items` - 获取工资项目列表
- `POST /api/salary-items` - 创建工资项目
- `PUT /api/salary-items/<id>` - 更新工资项目
- `DELETE /api/salary-items/<id>` - 删除工资项目
- `GET /api/salary-items/<id>/defaults` - 获取项目默认值
- `POST /api/salary-items/<id>/defaults` - 设置项目默认值

### 绩效管理API
- `GET /api/perf-categories` - 获取绩效分类列表
- `POST /api/perf-categories` - 创建绩效分类
- `PUT /api/perf-categories/<id>` - 更新绩效分类
- `DELETE /api/perf-categories/<id>` - 删除绩效分类
- `GET /api/perf-indicators` - 获取绩效指标列表
- `POST /api/perf-indicators` - 创建绩效指标
- `PUT /api/perf-indicators/<id>` - 更新绩效指标
- `DELETE /api/perf-indicators/<id>` - 删除绩效指标

## 数据库表结构

### custom_fields - 自定义字段定义表
```sql
CREATE TABLE custom_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_name TEXT NOT NULL,        -- 字段名称
    field_code TEXT NOT NULL UNIQUE, -- 字段编码
    field_type TEXT NOT NULL,        -- 字段类型
    options TEXT,                    -- 选项(JSON)
    department TEXT,                 -- 适用科室
    is_required INTEGER DEFAULT 0,   -- 是否必填
    sort_order INTEGER DEFAULT 0,    -- 排序
    is_active INTEGER DEFAULT 1,     -- 是否启用
    created_at TEXT                  -- 创建时间
);
```

### employee_custom_data - 职工自定义数据表
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

### salary_items - 工资项目表
```sql
CREATE TABLE salary_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,              -- 项目名称
    item_code TEXT NOT NULL UNIQUE,       -- 项目编码
    item_type TEXT NOT NULL,              -- 项目类型
    calculation_method TEXT,              -- 计算方式
    formula TEXT,                         -- 计算公式
    is_taxable INTEGER DEFAULT 1,         -- 是否计税
    is_visible INTEGER DEFAULT 1,         -- 是否显示
    sort_order INTEGER DEFAULT 0,         -- 排序
    is_active INTEGER DEFAULT 1,          -- 是否启用
    description TEXT,                     -- 描述
    created_at TEXT                       -- 创建时间
);
```

### salary_item_defaults - 工资项目默认值表
```sql
CREATE TABLE salary_item_defaults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,             -- 项目ID
    department TEXT,                      -- 科室
    title_level TEXT,                     -- 职称级别
    default_value REAL DEFAULT 0,         -- 默认值
    FOREIGN KEY (item_id) REFERENCES salary_items(id),
    UNIQUE(item_id, department, title_level)
);
```

### perf_categories - 绩效分类表
```sql
CREATE TABLE perf_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,          -- 分类名称
    category_code TEXT NOT NULL UNIQUE,   -- 分类编码
    weight REAL DEFAULT 0,                -- 权重
    description TEXT,                     -- 描述
    sort_order INTEGER DEFAULT 0,         -- 排序
    is_active INTEGER DEFAULT 1,          -- 是否启用
    created_at TEXT                       -- 创建时间
);
```

### perf_indicators - 绩效指标表
```sql
CREATE TABLE perf_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_name TEXT NOT NULL,         -- 指标名称
    indicator_code TEXT NOT NULL UNIQUE,  -- 指标编码
    category_id INTEGER,                  -- 分类ID
    scoring_method TEXT,                  -- 评分方式
    max_score REAL DEFAULT 100,           -- 满分
    weight REAL DEFAULT 0,                -- 权重
    description TEXT,                     -- 描述
    sort_order INTEGER DEFAULT 0,         -- 排序
    is_active INTEGER DEFAULT 1,          -- 是否启用
    created_at TEXT,                      -- 创建时间
    FOREIGN KEY (category_id) REFERENCES perf_categories(id)
);
```

## 操作建议

### 1. 初始化自定义字段
建议在系统部署后,先为各科室配置常用的自定义字段:

**医生:**
- 执业证书编号 (文本,必填)
- 专业方向 (下拉选择:内科/外科/儿科/...)
- 学术任职 (多行文本)

**护士:**
- 护士执业证号 (文本,必填)
- 护理等级 (下拉选择:N0/N1/N2/N3/N4)
- 专科资质 (多行文本)

**行政:**
- 办公地点 (文本)
- 分管领域 (文本)

### 2. 配置工资项目
根据医院实际工资结构设计工资项目:

1. **收入项目**:
   - 基本工资 (按职称级别设置不同默认值)
   - 岗位津贴 (按岗位设置)
   - 绩效奖金 (浮动,根据考核结果)
   - 各类补贴 (医疗、住房、交通等)

2. **扣款项目**:
   - 五险一金 (按比例计算)
   - 个人所得税 (自动计算)
   - 其他扣款 (考勤扣款等)

### 3. 建立绩效体系
构建完整的绩效考核体系:

1. **确定考核维度**: 工作业绩、服务质量、教学科研、医德医风
2. **设置权重分配**: 根据医院战略重点调整各维度权重
3. **细化考核指标**: 每个维度下设置3-5个具体可量化的指标
4. **定期评估调整**: 根据实际情况调整指标和权重

## 注意事项

1. **权限控制**: 这些功能需要`salary`或`performance`模块的`write`权限
2. **编码唯一性**: 字段编码、项目编码、分类编码、指标编码必须唯一
3. **软删除**: 绩效分类和指标采用软删除(is_active=0),避免历史数据丢失
4. **数据关联**: 删除工资项目时会同时删除其默认值配置
5. **权重总和**: 建议确保同一分类下的指标权重总和为100%

## 下一步扩展

可以考虑以下扩展功能:

1. **工资项目模板**: 预设常见工资项目模板,快速配置
2. **绩效模板管理**: 为不同岗位创建不同的绩效考核模板
3. **字段导入导出**: 支持批量导入自定义字段配置
4. **历史记录**: 记录工资项目和绩效配置的变更历史
5. **统计分析**: 分析各工资项目的分布情况、绩效指标的得分情况等
