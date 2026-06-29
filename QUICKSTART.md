# 快速启动指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 启动系统

```bash
python app.py
```

系统会自动:
- 创建数据库文件 (`data/hospital_hr.db`)
- 初始化所有表结构
- 插入默认管理员账号
- 插入示例数据

## 3. 访问系统

浏览器打开: http://127.0.0.1:5000

**默认管理员账号:**
- 用户名: `admin`
- 密码: `admin123`

## 4. 测试新功能

### 方法一: 使用测试脚本

```bash
# 先确保系统已启动
python test_new_features.py
```

### 方法二: 手动测试API

#### 测试自定义字段
```bash
# 1. 登录获取session
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# 2. 创建自定义字段
curl -X POST http://127.0.0.1:5000/api/custom-fields \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "执业证书号",
    "field_code": "license_no",
    "field_type": "text",
    "department": "内科",
    "is_required": 1
  }'

# 3. 查询自定义字段
curl http://127.0.0.1:5000/api/custom-fields -b cookies.txt
```

#### 测试请假申请
```bash
# 提交请假申请
curl -X POST http://127.0.0.1:5000/api/leave/request \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type": "病假",
    "start_date": "2026-07-01",
    "end_date": "2026-07-03",
    "days": 3,
    "reason": "身体不适"
  }'

# 查询请假记录
curl http://127.0.0.1:5000/api/leave/list -b cookies.txt
```

#### 测试职工自助服务
```bash
# 获取个人信息
curl http://127.0.0.1:5000/api/self/profile -b cookies.txt

# 查询工资记录
curl "http://127.0.0.1:5000/api/self/salary?month=2026-06" -b cookies.txt
```

#### 测试Excel导出
```bash
# 导出职工花名册
curl http://127.0.0.1:5000/api/employees/export \
  -b cookies.txt \
  -o employees.xlsx

# 导出工资表
curl "http://127.0.0.1:5000/api/salary/records/export?month=2026-06" \
  -b cookies.txt \
  -o salary_2026-06.xlsx
```

## 5. 常见问题

### Q: 启动时提示模块未找到?
A: 运行 `pip install -r requirements.txt` 安装依赖

### Q: 数据库文件在哪里?
A: `data/hospital_hr.db`

### Q: 如何重置数据库?
A: 删除 `data/hospital_hr.db` 文件,重启系统会自动重建

### Q: 如何查看API日志?
A: 所有操作都会记录到 `operation_logs` 表,可通过系统设置查看

### Q: Excel导入失败?
A: 检查Excel格式是否正确,确保包含必填列(工号、姓名)

## 6. 下一步

- 阅读 [FEATURES.md](FEATURES.md) 了解详细功能说明
- 阅读 [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) 了解实施详情
- 开始前端开发,集成Vue.js组件

---

**祝使用愉快!** 🎉
