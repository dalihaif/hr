# 医院人事系统 API 文档 (第二、三、四阶段新增功能)

## 📋 目录
- [PDF工资条生成](#pdf工资条生成)
- [数据备份管理](#数据备份管理)
- [招聘管理](#招聘管理)
- [培训管理](#培训管理)
- [离职管理](#离职管理)

---

## PDF工资条生成

### 1. 生成工资条PDF/ZIP

**接口:** `POST /api/salary/slips/generate`

**权限:** salary.write

**请求参数:**
```json
{
  "month": "2026-06",           // 必填,工资月份
  "emp_ids": [1, 2, 3]          // 可选,指定职工ID列表,不传则生成所有
}
```

**响应:**
- 单个职工: 返回PDF文件下载
- 多个职工: 返回ZIP压缩包下载

**示例:**
```bash
curl -X POST http://localhost:5000/api/salary/slips/generate \
  -H "Content-Type: application/json" \
  -d '{"month": "2026-06"}' \
  --output salary_slips.zip
```

---

## 数据备份管理

### 2. 创建备份

**接口:** `POST /api/backup/create`

**权限:** system.admin

**请求参数:**
```json
{
  "type": "full"  // full=完整备份, incremental=增量备份
}
```

**响应:**
```json
{
  "ok": true,
  "backup_file": "full_backup_20260629_150718.db.gz",
  "size": 10240
}
```

### 3. 获取备份列表

**接口:** `GET /api/backup/list`

**权限:** system.admin

**响应:**
```json
[
  {
    "filename": "full_backup_20260629_150718.db.gz",
    "size_mb": 0.01,
    "created_at": "2026-06-29 15:07:18",
    "type": "full"
  }
]
```

### 4. 恢复备份

**接口:** `POST /api/backup/restore`

**权限:** system.admin

**请求参数:**
```json
{
  "filename": "full_backup_20260629_150718.db.gz"
}
```

**响应:**
```json
{
  "ok": true,
  "message": "数据恢复成功"
}
```

### 5. 下载备份

**接口:** `GET /api/backup/download/<filename>`

**权限:** system.admin

**响应:** 文件下载

### 6. 清理过期备份

**接口:** `POST /api/backup/cleanup`

**权限:** system.admin

**请求参数:**
```json
{
  "keep_days": 30  // 保留天数
}
```

**响应:**
```json
{
  "ok": true,
  "deleted_count": 5
}
```

---

## 招聘管理

### 7. 获取招聘岗位列表

**接口:** `GET /api/recruitment/positions`

**权限:** personnel.write

**查询参数:**
- `status`: 岗位状态(招聘中/已招满/已关闭)
- `department`: 科室筛选

**响应:**
```json
[
  {
    "id": 1,
    "position_name": "内科医师",
    "department": "内科",
    "headcount": 2,
    "hired_count": 0,
    "requirements": "本科及以上学历",
    "status": "招聘中",
    "publish_date": "2026-06-01",
    "deadline": "2026-07-31",
    "creator_name": "张主任",
    "created_at": "2026-06-29 10:00:00"
  }
]
```

### 8. 创建招聘岗位

**接口:** `POST /api/recruitment/positions`

**权限:** personnel.write

**请求参数:**
```json
{
  "position_name": "内科医师",
  "department": "内科",
  "headcount": 2,
  "requirements": "本科及以上学历,有执业医师证",
  "status": "招聘中",
  "publish_date": "2026-06-01",
  "deadline": "2026-07-31"
}
```

### 9. 更新/关闭岗位

**接口:** 
- `PUT /api/recruitment/positions/<id>` - 更新
- `DELETE /api/recruitment/positions/<id>` - 关闭

**权限:** personnel.write

### 10. 获取应聘者列表

**接口:** `GET /api/recruitment/applicants`

**权限:** personnel.write

**查询参数:**
- `position_id`: 岗位ID
- `status`: 状态(待筛选/初试/复试/录用/拒绝)

### 11. 录入应聘者信息

**接口:** `POST /api/recruitment/applicants`

**权限:** personnel.write

**请求参数:**
```json
{
  "position_id": 1,
  "name": "李明",
  "gender": "男",
  "birth_date": "1995-05-20",
  "phone": "13800138000",
  "email": "liming@example.com",
  "education": "本科",
  "major": "临床医学",
  "experience_years": 3,
  "resume_path": "/uploads/resume_001.pdf"
}
```

### 12. 更新应聘者状态

**接口:** `PUT /api/recruitment/applicants/<id>`

**权限:** personnel.write

**请求参数:**
```json
{
  "status": "初试"  // 待筛选/初试/复试/录用/拒绝
}
```

### 13. 面试记录管理

**接口:** 
- `GET /api/recruitment/interviews?applicant_id=<id>` - 获取面试记录
- `POST /api/recruitment/interviews` - 创建面试记录

**权限:** personnel.write

**POST请求参数:**
```json
{
  "applicant_id": 1,
  "interview_type": "初试",
  "interviewer_id": 2,
  "interview_date": "2026-07-01 14:00:00",
  "score": 85.5,
  "comments": "表现良好,专业扎实",
  "result": "通过"
}
```

### 14. 招聘统计分析

**接口:** `GET /api/recruitment/statistics`

**权限:** personnel.read

**响应:**
```json
{
  "positions": [
    {"status": "招聘中", "count": 5},
    {"status": "已招满", "count": 2}
  ],
  "applicants": [
    {"status": "待筛选", "count": 10},
    {"status": "初试", "count": 5},
    {"status": "录用", "count": 2}
  ]
}
```

---

## 培训管理

### 15. 获取培训计划列表

**接口:** `GET /api/training/plans`

**权限:** personnel.write

**查询参数:**
- `status`: 状态(计划中/进行中/已完成/已取消)

### 16. 创建培训计划

**接口:** `POST /api/training/plans`

**权限:** personnel.write

**请求参数:**
```json
{
  "title": "心肺复苏技能培训",
  "training_type": "内部培训",
  "trainer": "王医生",
  "start_date": "2026-07-10",
  "end_date": "2026-07-10",
  "location": "会议室A",
  "max_participants": 30,
  "description": "基础生命支持技能培训"
}
```

### 17. 更新/取消培训计划

**接口:**
- `PUT /api/training/plans/<id>` - 更新
- `DELETE /api/training/plans/<id>` - 取消

**权限:** personnel.write

### 18. 职工报名培训

**接口:** `POST /api/training/enroll`

**权限:** require_login (任意登录用户)

**请求参数:**
```json
{
  "plan_id": 1
}
```

### 19. 获取培训报名记录

**接口:** `GET /api/training/enrollments`

**权限:** personnel.read

**查询参数:**
- `plan_id`: 培训计划ID

### 20. 培训档案管理

**接口:**
- `GET /api/training/records?emp_id=<id>` - 获取培训档案
- `POST /api/training/records` - 录入培训记录

**权限:** personnel.write

**POST请求参数:**
```json
{
  "emp_id": 1,
  "training_name": "心肺复苏技能培训",
  "training_type": "内部培训",
  "training_date": "2026-07-10",
  "hours": 4,
  "score": 90,
  "certificate_no": "CERT20260710001",
  "description": "考核优秀"
}
```

### 21. 培训统计分析

**接口:** `GET /api/training/statistics`

**权限:** personnel.read

**响应:**
```json
{
  "plans": [
    {"status": "计划中", "count": 3},
    {"status": "已完成", "count": 10}
  ],
  "avg_training_hours": 24.5
}
```

---

## 离职管理

### 22. 获取离职申请列表

**接口:** `GET /api/resignation/requests`

**权限:** personnel.write

**查询参数:**
- `status`: 状态(待审批/部门审批/人事审批/已批准/已拒绝/已办理)
- `emp_id`: 职工ID

### 23. 提交离职申请

**接口:** `POST /api/resignation/requests`

**权限:** personnel.write

**请求参数:**
```json
{
  "emp_id": 1,
  "resignation_type": "主动辞职",
  "reason": "个人发展原因",
  "apply_date": "2026-07-01",
  "expected_last_day": "2026-07-31"
}
```

### 24. 更新离职申请状态

**接口:** `PUT /api/resignation/requests/<id>`

**权限:** personnel.write

**请求参数:**
```json
{
  "status": "部门审批"
}
```

### 25. 审批离职申请

**接口:** `POST /api/resignation/approve`

**权限:** personnel.write

**请求参数:**
```json
{
  "request_id": 1,
  "approved": true  // true=批准, false=拒绝
}
```

### 26. 离职交接清单管理

**接口:**
- `GET /api/resignation/handover?resignation_id=<id>` - 获取交接清单
- `POST /api/resignation/handover` - 创建交接项
- `PUT /api/resignation/handover/<item_id>` - 完成交接

**权限:** personnel.write

**POST请求参数:**
```json
{
  "resignation_id": 1,
  "item_name": "工作文档移交",
  "item_type": "工作文档",
  "handler_id": 2,
  "remarks": "包括病历档案、患者资料等"
}
```

### 27. 离职档案管理

**接口:**
- `GET /api/resignation/records?emp_id=<id>` - 获取离职档案
- `POST /api/resignation/records` - 创建离职档案

**权限:** personnel.write

**POST请求参数:**
```json
{
  "emp_id": 1,
  "resignation_type": "主动辞职",
  "last_working_day": "2026-07-31",
  "final_salary": 8500.00,
  "handover_completed": 1,
  "exit_interview_notes": "员工表示对工作环境满意,因家庭原因离职"
}
```

### 28. 离职统计分析

**接口:** `GET /api/resignation/statistics`

**权限:** personnel.read

**响应:**
```json
{
  "types": [
    {"resignation_type": "主动辞职", "count": 5},
    {"resignation_type": "合同到期", "count": 2}
  ],
  "turnover_rate": 8.5,
  "resigned_count": 7,
  "total_employees": 82
}
```

---

## 🔐 权限说明

| 权限代码 | 说明 | 适用角色 |
|---------|------|---------|
| salary.write | 工资管理写入 | admin, hr_manager |
| system.admin | 系统管理 | admin |
| personnel.write | 人事管理写入 | admin, hr_manager |
| personnel.read | 人事管理读取 | admin, hr_manager, department_head |
| require_login | 仅需登录 | 所有登录用户 |

---

## 📝 使用示例

### Python requests示例

```python
import requests

BASE_URL = 'http://localhost:5000'

# 登录获取session
session = requests.Session()
session.post(f'{BASE_URL}/api/login', json={
    'username': 'admin',
    'password': 'admin123'
})

# 1. 生成工资条
response = session.post(f'{BASE_URL}/api/salary/slips/generate', json={
    'month': '2026-06'
})
with open('salary_slips.zip', 'wb') as f:
    f.write(response.content)

# 2. 创建备份
response = session.post(f'{BASE_URL}/api/backup/create', json={'type': 'full'})
print(response.json())

# 3. 创建招聘岗位
response = session.post(f'{BASE_URL}/api/recruitment/positions', json={
    'position_name': '护士',
    'department': '护理部',
    'headcount': 5,
    'requirements': '护理专业大专以上'
})
print(response.json())

# 4. 创建培训计划
response = session.post(f'{BASE_URL}/api/training/plans', json={
    'title': '急救技能培训',
    'training_type': '内部培训',
    'trainer': '李医生',
    'start_date': '2026-07-15',
    'max_participants': 20
})
print(response.json())

# 5. 提交离职申请
response = session.post(f'{BASE_URL}/api/resignation/requests', json={
    'emp_id': 1,
    'resignation_type': '主动辞职',
    'reason': '个人原因',
    'expected_last_day': '2026-08-31'
})
print(response.json())
```

---

## ⚠️ 注意事项

1. **PDF生成**: 需要安装reportlab库,中文字体可能需要额外配置
2. **数据备份**: 建议定期执行备份,并设置合理的保留策略
3. **敏感信息**: 手机号等敏感字段会自动加密存储
4. **权限控制**: 所有API都有权限验证,请确保用户有相应权限
5. **数据库表**: 新模块的表会在首次启动时自动创建

---

**文档版本:** v1.0  
**更新时间:** 2026-06-29
