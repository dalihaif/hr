-- ============================================================
-- 职工自助服务 - 数据库补充脚本
-- 创建培训相关表
-- ============================================================

-- 培训计划表
CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_name TEXT NOT NULL,           -- 培训名称
    training_type TEXT NOT NULL,           -- 培训类型(内部/外部/在线)
    category TEXT NOT NULL,                -- 分类(临床技能/院感防控/医患沟通/管理能力等)
    start_date TEXT NOT NULL,              -- 开始日期
    end_date TEXT NOT NULL,                -- 结束日期
    hours REAL NOT NULL,                   -- 学时
    location TEXT,                         -- 培训地点
    instructor TEXT,                       -- 讲师
    max_participants INTEGER,              -- 最大人数
    description TEXT,                      -- 培训描述
    status TEXT DEFAULT '计划中',           -- 状态(计划中/报名中/进行中/已完成/已取消)
    created_by INTEGER,                    -- 创建人ID
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 职工培训关联表
CREATE TABLE IF NOT EXISTS employee_training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,               -- 职工ID
    training_id INTEGER NOT NULL,          -- 培训ID
    enrollment_date TEXT,                  -- 报名日期
    attendance_status TEXT DEFAULT '未参加',-- 参与状态(未参加/已参加/缺勤)
    score REAL,                            -- 考核成绩
    certificate TEXT,                      -- 证书编号
    certificate_date TEXT,                 -- 获证日期
    remarks TEXT,                          -- 备注
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(emp_id, training_id),
    FOREIGN KEY (emp_id) REFERENCES employees(id),
    FOREIGN KEY (training_id) REFERENCES trainings(id)
);

-- 插入示例培训数据
INSERT OR IGNORE INTO trainings (training_name, training_type, category, start_date, end_date, hours, location, instructor, max_participants, description, status) VALUES
('心肺复苏(CPR)培训', '内部', '临床技能', '2024-01-10', '2024-01-12', 8.0, '教学楼3楼会议室', '张医生', 50, '基础生命支持技能培训,含实操演练', '已完成'),
('医院感染防控培训', '内部', '院感防控', '2023-12-05', '2023-12-07', 6.0, '学术报告厅', '李护士长', 100, '手卫生、医疗废物处理、隔离技术等', '已完成'),
('医患沟通技巧提升', '外部', '医患沟通', '2023-11-20', '2023-11-22', 4.0, '外聘专家讲座', '王教授', 80, '有效沟通、冲突化解、患者满意度提升', '已完成'),
('电子病历系统操作', '内部', '信息化', '2024-02-15', '2024-02-16', 4.0, '信息科培训室', '赵工程师', 60, 'EMR系统新功能操作培训', '计划中'),
('医疗质量管理培训', '外部', '质量管理', '2024-03-10', '2024-03-12', 12.0, '省人民医院', '刘主任', 30, 'PDCA循环、持续质量改进方法', '计划中');

-- 插入示例职工培训记录
INSERT OR IGNORE INTO employee_training (emp_id, training_id, enrollment_date, attendance_status, score, certificate, certificate_date) VALUES
(1, 1, '2024-01-05', '已参加', 95.0, 'CPR20240110001', '2024-01-12'),
(1, 2, '2023-12-01', '已参加', 88.0, 'IC20231207001', '2023-12-07'),
(1, 3, '2023-11-15', '已参加', NULL, NULL, NULL),
(2, 1, '2024-01-05', '已参加', 92.0, 'CPR20240110002', '2024-01-12'),
(2, 2, '2023-12-01', '已参加', 90.0, 'IC20231207002', '2023-12-07');
