# 🚀 快速启动指南 - 解决502/500错误

## ❌ 当前问题

根据错误日志,您遇到了以下问题:

1. **502 Bad Gateway** - 后端服务未运行
2. **500 Internal Server Error** - EmployeeSelfService.vue加载失败(可能因后端未启动导致)

---

## ✅ 解决方案

### 步骤1: 启动后端服务

打开**终端1**,执行:

```bash
cd e:\my-web\hospital-hr
python app.py
```

**预期输出:**
```
✓ 人力资源管理模块已注册
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

⚠️ **保持此终端窗口开启,不要关闭!**

---

### 步骤2: 确认前端服务运行

打开**终端2**,检查前端是否运行:

```bash
cd e:\my-web\hospital-hr\frontend
npm run dev
```

**预期输出:**
```
VITE v8.1.0  ready in xxx ms

➜  Local:   http://localhost:5174/
➜  Network: use --host to expose
```

如果前端未运行,执行上述命令启动。

⚠️ **保持此终端窗口开启,不要关闭!**

---

### 步骤3: 验证服务状态

#### 方法1: 浏览器访问

1. 打开浏览器
2. 访问: http://localhost:5000/api/current_user
   - 如果返回JSON或401错误 → ✅ 后端正常
   - 如果无法连接 → ❌ 后端未启动

3. 访问: http://localhost:5174
   - 如果显示登录页面 → ✅ 前端正常
   - 如果无法连接 → ❌ 前端未启动

#### 方法2: 使用测试脚本

```bash
cd e:\my-web\hospital-hr
python check_backend.py
```

---

### 步骤4: 访问职工自助服务

在浏览器中访问:
```
http://localhost:5174/self-service
```

使用普通职工账号登录即可体验。

---

## 🔧 常见问题排查

### Q1: 后端启动失败

**症状:**
```
ModuleNotFoundError: No module named 'xxx'
```

**解决:**
```bash
pip install flask flask-cors openpyxl reportlab cryptography
```

---

### Q2: 端口被占用

**症状:**
```
OSError: [WinError 10048] 通常每个套接字地址只允许使用一次
```

**解决:**

查找占用端口的进程:
```bash
netstat -ano | findstr :5000
```

终止进程(替换PID为实际进程ID):
```bash
taskkill /F /PID <PID>
```

---

### Q3: 前端加载EmployeeSelfService.vue失败

**症状:**
```
Failed to fetch dynamically imported module
```

**可能原因:**
1. 后端未启动(最常见)
2. ECharts未安装
3. Vue组件语法错误

**解决:**
```bash
# 1. 确保后端已启动
python app.py

# 2. 检查ECharts
cd frontend
npm list echarts

# 3. 重新安装依赖
npm install
npm install echarts

# 4. 重启前端
npm run dev
```

---

### Q4: API返回502错误

**症状:**
```
api/resignation/handover - 502 Bad Gateway
api/backup/list - 502 Bad Gateway
```

**原因:** 后端服务未运行

**解决:** 启动后端服务(见步骤1)

---

## 📋 完整启动流程

### 推荐方式: 使用两个终端窗口

```
┌─────────────────────────┐    ┌─────────────────────────┐
│   终端1 - 后端服务       │    │   终端2 - 前端服务       │
│                         │    │                         │
│ cd hospital-hr          │    │ cd hospital-hr/frontend │
│ python app.py           │    │ npm run dev             │
│                         │    │                         │
│ ✓ 人力资源管理模块已注册 │    │ VITE ready in xxx ms    │
│ * Running on :5000      │    │ ➜ Local: :5174          │
└─────────────────────────┘    └─────────────────────────┘
```

### 访问系统

浏览器打开: **http://localhost:5174**

---

## ✅ 验证清单

启动后,请检查以下项目:

- [ ] 后端服务正在运行(终端1无报错)
- [ ] 前端服务正在运行(终端2无报错)
- [ ] 可以访问 http://localhost:5174
- [ ] 可以成功登录
- [ ] 侧边栏显示"自助服务"菜单
- [ ] 点击"自助服务"可以正常加载页面
- [ ] 各个Tab页数据正常显示

---

## 🎯 下一步

服务启动成功后:

1. **测试职工自助服务功能**
   - 查看个人信息
   - 查询工资明细
   - 查看绩效考核
   - 提交请假申请

2. **阅读相关文档**
   - [EMPLOYEE_SELF_SERVICE_GUIDE.md](EMPLOYEE_SELF_SERVICE_GUIDE.md) - 详细功能说明
   - [SELF_SERVICE_DEPLOY.md](SELF_SERVICE_DEPLOY.md) - 部署指南

3. **反馈问题**
   - 如遇到问题,提供完整的错误日志
   - 截图显示具体问题界面

---

## 📞 技术支持

如需帮助:
- IT支持: ext. 8888
- HR咨询: ext. 6666
- 邮箱: hr-support@hospital.com

---

**最后更新**: 2026-06-29 21:00
