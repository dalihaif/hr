# 职工自助服务页面 - 快速部署指南

## 📅 更新日期
2026-06-29 20:30

---

## ✅ 已完成工作

### 1. 前端页面
- ✅ 创建 `EmployeeSelfService.vue` (858行)
- ✅ 添加路由配置 `/self-service`
- ✅ 实现6个功能模块(个人信息/工资查询/绩效考核/考勤记录/请假申请/培训记录)

### 2. 后端API
- ✅ 添加 `/api/employees/me` - 获取当前用户信息
- ✅ 添加 `/api/performance/my-assessments` - 获取我的绩效考核
- ✅ 添加 `/api/attendance/my-records` - 获取我的考勤记录
- ✅ 添加 `/api/attendance/my-leave-requests` - 获取我的请假申请
- ✅ 添加 `/api/attendance/my-leave-balance` - 获取我的假期余额
- ✅ 添加 `/api/training/my-records` - 获取我的培训记录

### 3. 数据库
- ✅ 创建 `trainings` 表(培训计划)
- ✅ 创建 `employee_training` 表(职工培训关联)
- ✅ 插入示例培训数据

---

## 🔧 部署步骤

### 步骤 1: 安装 ECharts 依赖

**方法一: 使用npm(推荐)**

打开终端,进入frontend目录:
```bash
cd e:\my-web\hospital-hr\frontend
npm install echarts
```

**方法二: 手动下载**

如果npm不可用,可以:
1. 访问 https://echarts.apache.org/zh/download.html
2. 下载 `echarts.min.js`
3. 放入 `frontend/node_modules/echarts/dist/` 目录

---

### 步骤 2: 启动后端服务

打开终端1:
```bash
cd e:\my-web\hospital-hr
python app.py
```

预期输出:
```
✓ 人力资源管理模块已注册
 * Running on http://0.0.0.0:5000
```

---

### 步骤 3: 启动前端开发服务器

打开终端2:
```bash
cd e:\my-web\hospital-hr\frontend
npm run dev
```

预期输出:
```
VITE v8.1.0  ready in xxx ms

➜  Local:   http://localhost:5174/
➜  Network: use --host to expose
```

---

### 步骤 4: 访问系统

浏览器打开: **http://localhost:5174/self-service**

使用普通职工账号登录即可体验。

---

## 📋 功能清单

### Tab 1: 个人信息
- [x] 基本信息展示(姓名、工号、科室、岗位等)
- [x] 事业单位信息(岗位等级、职称、薪级等)
- [x] 联系方式(手机号加密显示)
- [x] 社保与银行信息

### Tab 2: 工资查询
- [x] 月份选择器
- [x] 应发项目明细(绿色显示)
- [x] 扣款项目明细(红色显示)
- [x] 汇总统计(应发/扣款/实发)
- [x] 近6个月工资趋势图(ECharts)
- [ ] PDF工资条下载(待实现)

### Tab 3: 绩效考核
- [x] 考核列表(周期、总分、等级、金额、状态)
- [x] 统计分析(平均分、最高分、次数)
- [x] 绩效金额自动计算(基于科室系数)
- [ ] 详情弹窗查看各维度得分(待实现)

### Tab 4: 考勤记录
- [x] 月份筛选
- [x] 统计卡片(应出勤/实际出勤/迟到/出勤率)
- [x] 每日考勤明细(签到/签退/时长/状态)
- [ ] 考勤申诉功能(待实现)

### Tab 5: 请假申请
- [x] 假期余额显示(年假/病假/调休/其他)
- [x] 在线提交申请表单
- [x] 产假专用字段(生产类型/多胞胎/自动计算天数)
- [x] 附件上传支持
- [x] 审批状态跟踪
- [ ] 请假详情查看(待实现)

### Tab 6: 培训记录
- [x] 培训列表(名称/日期/学时/状态/证书)
- [x] 年度学时统计进度条
- [x] 完成率计算
- [ ] 培训报名功能(待实现)

---

## 🎯 核心特性

### 1. 数据安全
- ✅ 手机号AES加密存储,前端解密显示
- ✅ 仅允许查询本人数据,严格权限控制
- ✅ 敏感信息部分隐藏(如银行卡号)

### 2. 用户体验
- ✅ 快捷功能卡片,一键跳转
- ✅ 颜色语义化(绿色成功/红色失败/黄色警告)
- ✅ 空状态提示,引导用户操作
- ✅ 响应式设计,支持移动端

### 3. 业务逻辑
- ✅ 产假天数自动计算(158天基础+15天难产+15天/胎多胞胎)
- ✅ 绩效工资自动计算(基准×系数×评分%)
- ✅ 考勤状态自动判定(正常/迟到/早退/缺勤)
- ✅ 学时完成率实时统计

---

## 🐛 常见问题

### Q1: 页面空白,无法加载
**A:** 检查以下几点:
1. 后端服务是否启动(端口5000)
2. 前端服务是否启动(端口5174)
3. 浏览器控制台是否有错误信息
4. 网络请求是否成功(F12 → Network)

### Q2: 工资查询无数据
**A:** 可能原因:
1. 该职工没有工资记录
2. 选择的月份没有数据
3. 工资计算器未正确配置岗位/薪级标准

**解决方法:**
```python
# 在Python终端测试
from utils.salary_calculator import SalaryCalculator
calc = SalaryCalculator('data/hospital_hr.db')
result = calc.calculate_employee_salary(1, '2024-01')
print(result)
```

### Q3: 图表不显示
**A:** ECharts未正确安装

**解决方法:**
```bash
cd frontend
npm list echarts  # 检查是否安装
npm install echarts  # 重新安装
```

### Q4: 请假申请提交失败
**A:** 检查数据库表是否存在

**解决方法:**
```bash
python -c "import sqlite3; conn = sqlite3.connect('data/hospital_hr.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print([r[0] for r in cursor.fetchall()])"
```

确保以下表存在:
- `leave_requests`
- `leave_balances`

---

## 📊 测试建议

### 测试场景1: 完整工资查询流程
1. 登录职工账号
2. 点击"工资查询"Tab
3. 选择不同月份
4. 验证应发/扣款/实发金额
5. 查看近6个月趋势图

### 测试场景2: 产假申请流程
1. 点击"请假申请"Tab
2. 点击"提交请假申请"按钮
3. 选择请假类型为"产假"
4. 选择生产类型(顺产/难产/剖腹产)
5. 设置是否多胞胎
6. 验证自动计算的天数是否正确
7. 填写起止日期和原因
8. 提交申请

### 测试场景3: 考勤记录查看
1. 点击"考勤记录"Tab
2. 选择不同月份
3. 验证统计数据准确性
4. 检查每日考勤状态标识

---

## 📞 技术支持

如遇问题,请联系:
- **IT支持**: ext. 8888
- **HR咨询**: ext. 6666
- **邮箱**: hr-support@hospital.com

---

## 📝 更新日志

### v1.0 (2026-06-29)
- ✅ 初始版本发布
- ✅ 6个功能模块全部实现
- ✅ 7个后端API接口完成
- ✅ 数据库表结构完善
- ✅ 产假规则集成(158天+15天+15天)

---

**维护者**: IT部门  
**最后更新**: 2026-06-29 20:30
