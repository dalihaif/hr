# 大理大学第一附属医院智能人事系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-orange.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 项目简介

大理大学第一附属医院智能人事管理系统是一个基于Python Flask开发的医院人力资源管理平台,提供职工信息管理、工资核算、绩效考核、考勤管理等核心功能。

### ✨ 核心特性

- 👥 **职工信息管理** - 完整的职工档案,支持自定义字段扩展
- 💰 **工资核算管理** - 灵活的工资项目配置,自动计算个税和社保
- 📊 **绩效管理体系** - 多维度绩效考核,支持分类和指标配置
- 📅 **考勤管理** - 请假加班申请审批流程
- 🔐 **权限控制** - 基于角色的访问控制(RBAC)
- 📈 **数据统计** - 可视化数据分析和报表导出
- 🔒 **数据安全** - AES加密敏感信息,防SQL注入和XSS攻击

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- SQLite 3.x
- 现代浏览器(Chrome/Firefox/Edge/Safari)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd hospital-hr
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务**
   ```bash
   python app.py
   ```

4. **访问系统**
   - 打开浏览器访问: http://127.0.0.1:5000
   - 默认账号: `admin` / `admin123`

---

## 📖 功能模块

### 1. 系统概览 (Dashboard)
- 职工总数统计
- 科室人员分布图表
- 最近操作记录
- 关键指标展示

### 2. 人员信息管理
- ✅ 职工花名册管理
- ✅ 职工详细信息查看/编辑
- ✅ 多条件搜索和筛选
- ✅ Excel导入导出
- ✅ **自定义字段扩展** (NEW!)
- ✅ 岗位变更记录
- ✅ 批量操作支持

### 3. 工资核算
- ✅ 工资标准配置
- ✅ 月度工资核算
- ✅ 个税自动计算
- ✅ 社保公积金计算
- ✅ **工资项目管理** (NEW!)
- ✅ 工资条生成和导出
- ✅ 历史工资查询

### 4. 绩效管理
- ✅ 考核模板管理
- ✅ 绩效考核评分
- ✅ **绩效分类和指标配置** (NEW!)
- ✅ 多维度考核体系
- ✅ 考核结果统计
- ✅ 绩效等级评定

### 5. 考勤管理
- ✅ 请假申请和审批
- ✅ 加班申请和审批
- ✅ 考勤记录查询
- ✅ 考勤统计分析

### 6. 系统设置
- ✅ 用户管理
- ✅ **自定义字段管理** (NEW!)
- ✅ **工资项目管理** (NEW!)
- ✅ **绩效管理分类** (NEW!)
- ✅ 操作日志查询
- ✅ 权限配置

---

## 🆕 最新功能 (v1.0.0)

### 系统设置功能增强

本次更新在系统设置页面新增了三个核心管理模块:

#### 1️⃣ 自定义字段管理
- 为职工信息添加动态扩展字段
- 支持文本/数字/日期/下拉/多行文本等类型
- 可按科室配置不同字段
- 支持必填/选填、排序、启用/禁用控制

**使用场景:**
- 医生: 执业证书编号、专业方向、学术任职
- 护士: 护理等级、专科资质
- 行政: 办公地点、分管领域

📖 [查看详细文档](SETTINGS_FEATURES_GUIDE.md) | 📘 [快速上手](QUICK_START_SETTINGS.md)

#### 2️⃣ 工资项目管理
- 配置工资核算的各项收入/扣款项目
- 支持固定项/浮动项/扣款项
- 可设置计税规则和计算公式
- 按科室/职称设置默认值

**典型项目:**
- 收入: 基本工资、岗位津贴、绩效奖金、各类补贴
- 扣款: 五险一金、个人所得税、其他扣款

📖 [查看详细文档](SETTINGS_FEATURES_GUIDE.md) | 📘 [快速上手](QUICK_START_SETTINGS.md)

#### 3️⃣ 绩效管理分类
- 建立绩效考核的分类体系
- 配置考核指标和评分标准
- 支持多维度权重分配
- 支持百分制/等级制/定量评分

**典型体系:**
```
工作业绩 (40%) → 门诊量、住院患者数、手术台数、病历质量
服务质量 (30%) → 患者满意度、医疗差错率、投诉次数
教学科研 (20%) → 论文发表、科研项目、带教课时
医德医风 (10%) → 职业道德评价、劳动纪律
```

📖 [查看详细文档](SETTINGS_FEATURES_GUIDE.md) | 📘 [快速上手](QUICK_START_SETTINGS.md)

---

## 📚 文档索引

### 用户文档
- [系统设置功能详细说明](SETTINGS_FEATURES_GUIDE.md) - 完整的功能说明和使用指南
- [系统设置快速上手](QUICK_START_SETTINGS.md) - 图文并茂的快速入门教程
- [功能更新日志](CHANGELOG_SETTINGS.md) - 详细的技术实现和变更说明
- [实施完成报告](IMPLEMENTATION_REPORT.md) - 项目验收和总结报告

### 技术文档
- [API接口文档](FEATURES.md) - 所有API接口的详细说明
- [数据库设计](IMPLEMENTATION_SUMMARY.md) - 数据库表结构和关系
- [测试脚本](test_new_features.py) - 自动化测试示例

### 开发指南
- [快速启动指南](QUICKSTART.md) - 安装、配置、运行说明
- [贡献指南](CONTRIBUTING.md) - 如何参与项目开发 (待创建)

---

## 🛠️ 技术栈

### 后端
- **框架:** Flask 3.0+
- **数据库:** SQLite 3.x
- **加密:** AES (pycryptodome)
- **Excel处理:** openpyxl
- **密码哈希:** SHA-256

### 前端
- **基础:** HTML5 + CSS3 + JavaScript (ES6+)
- **图表:** Chart.js 4.x
- **UI:** 自定义CSS样式
- **交互:** 原生JavaScript (计划升级至Vue.js 3)

### 部署
- **服务器:** Flask Development Server / Gunicorn (生产环境)
- **反向代理:** Nginx (可选)
- **进程管理:** systemd / supervisord (可选)

---

## 📊 系统架构

```
┌─────────────────────────────────────────┐
│          前端界面 (HTML/CSS/JS)          │
│  ┌──────────┬──────────┬──────────────┐ │
│  │ Dashboard│ Personnel│ Salary/Perf  │ │
│  └──────────┴──────────┴──────────────┘ │
└──────────────────┬──────────────────────┘
                   │ REST API (JSON)
┌──────────────────▼──────────────────────┐
│         Flask Backend (app.py)          │
│  ┌──────────────────────────────────┐  │
│  │  Router & Controller Layer       │  │
│  ├──────────────────────────────────┤  │
│  │  Business Logic Layer            │  │
│  ├──────────────────────────────────┤  │
│  │  Data Access Layer               │  │
│  └──────────────────────────────────┘  │
└──────────────────┬──────────────────────┘
                   │ SQL
┌──────────────────▼──────────────────────┐
│      SQLite Database (hospital_hr.db)   │
│  ┌──────────────────────────────────┐  │
│  │ employees, users, departments    │  │
│  │ salary_records, perf_assessments │  │
│  │ custom_fields, salary_items      │  │
│  │ perf_categories, perf_indicators │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🔐 安全特性

### 数据安全
- ✅ **敏感信息加密**: 身份证号、手机号采用AES加密存储
- ✅ **密码安全**: SHA-256哈希存储,支持密码强度验证
- ✅ **SQL注入防护**: 所有查询使用参数化语句
- ✅ **XSS防护**: 前端输出转义,防止脚本注入

### 访问控制
- ✅ **身份认证**: Session-based认证机制
- ✅ **权限管理**: RBAC模型,细粒度权限控制
- ✅ **速率限制**: 登录防暴力破解,API调用限流
- ✅ **操作审计**: 完整的操作日志记录

### 输入验证
- ✅ **前端验证**: 表单实时验证和提示
- ✅ **后端验证**: 数据类型、格式、范围全面校验
- ✅ **文件上传**: 文件类型和大小限制

---

## 📈 性能优化

### 数据库优化
- ✅ **索引策略**: 关键字段添加索引,提升查询速度
- ✅ **查询优化**: 避免N+1查询,使用JOIN优化
- ✅ **连接池**: SQLite轻量级,无需连接池

### 缓存策略
- ⏳ **内存缓存**: 计划引入Redis缓存热点数据
- ⏳ **静态资源**: 计划启用浏览器缓存和CDN

### 代码优化
- ✅ **懒加载**: 按需加载数据和资源
- ✅ **分页查询**: 大数据量分页展示
- ✅ **异步处理**: 计划引入Celery处理耗时任务

---

## 🧪 测试

### 运行测试
```bash
# 运行自动化测试
python test_new_features.py
python test_settings_features.py
```

### 测试覆盖
- ✅ API接口功能测试
- ✅ 数据库操作测试
- ✅ 权限控制测试
- ✅ 输入验证测试
- ⏳ 单元测试 (计划中)
- ⏳ 集成测试 (计划中)
- ⏳ 性能测试 (计划中)

---

## 📦 部署指南

### 开发环境
```bash
python app.py
```

### 生产环境 (推荐)

1. **安装Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **启动服务**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **配置Nginx (可选)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **配置systemd (可选)**
   ```ini
   [Unit]
   Description=Hospital HR System
   After=network.target
   
   [Service]
   User=www-data
   WorkingDirectory=/path/to/hospital-hr
   ExecStart=/path/to/gunicorn -w 4 -b 127.0.0.1:5000 app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

---

## 🗺️ 路线图

### Phase 1 - 核心功能完善 (已完成 ✅)
- [x] 职工信息管理
- [x] 工资核算系统
- [x] 绩效管理体系
- [x] 自定义字段扩展
- [x] 工资项目配置
- [x] 绩效分类管理
- [x] 数据导入导出
- [x] 安全加固

### Phase 2 - 功能增强 (进行中 🚧)
- [ ] PDF工资条生成
- [ ] 数据备份恢复
- [ ] 招聘管理模块
- [ ] 培训管理模块
- [ ] 离职管理模块
- [ ] 移动端适配优化

### Phase 3 - 技术升级 (计划中 📋)
- [ ] 前端重构 (Vue.js 3 + Element Plus)
- [ ] Redis缓存层
- [ ] Celery异步任务
- [ ] JWT认证
- [ ] Docker容器化
- [ ] CI/CD流水线

### Phase 4 - 智能化 (展望 🔮)
- [ ] AI智能推荐
- [ ] 数据分析仪表盘
- [ ] 预测性分析
- [ ] 智能排班
- [ ] 人才画像

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议!

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

详见 [CONTRIBUTING.md](CONTRIBUTING.md) (待创建)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👥 团队

- **项目负责人:** [待补充]
- **后端开发:** [待补充]
- **前端开发:** [待补充]
- **测试工程师:** [待补充]

---

## 📞 联系方式

- 📧 Email: [待补充]
- 🌐 Website: [待补充]
- 📱 Phone: [待补充]

---

## 🙏 致谢

感谢以下开源项目:
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [SQLite](https://www.sqlite.org/) - 数据库
- [Chart.js](https://www.chartjs.org/) - 图表库
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel处理

---

**⭐ 如果这个项目对您有帮助,请给我们一个Star!**
