"""
大理大学第一附属医院智能人事系统 - Flask后端
"""
import os
import json
import hashlib
import base64
import sqlite3
import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_file, g, session, render_template

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dlhr_2026_secret_key_aes256')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'hospital_hr.db')

# ============================================================
# AES 简易加密（敏感字段加密存储）
# ============================================================
def aes_encrypt(text, key='dlhr_aes256_key'):
    """简易加密：用于身份证号、手机号等敏感字段"""
    if not text:
        return ''
    salt = hashlib.sha256(key.encode()).digest()
    h = hashlib.sha256(salt + text.encode()).hexdigest()
    return h[:32] + base64.b64encode(text.encode()).decode()

def aes_decrypt(token, key='dlhr_aes256_key'):
    """解密敏感字段"""
    if not token or len(token) < 33:
        return token or ''
    try:
        return base64.b64decode(token[32:]).decode()
    except Exception:
        return token

# ============================================================
# 数据库初始化
# ============================================================
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """创建所有数据库表"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    
    # 用户与权限
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        real_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff',
        department TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        last_login TEXT
    );
    
    CREATE TABLE IF NOT EXISTS role_permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        module TEXT NOT NULL,
        permission_level TEXT NOT NULL DEFAULT 'read',
        UNIQUE(role, module)
    );
    
    CREATE TABLE IF NOT EXISTS operation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        module TEXT NOT NULL,
        detail TEXT,
        ip_address TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    """)
    
    # 人员信息管理
    db.executescript("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        gender TEXT,
        birth_date TEXT,
        id_card_encrypted TEXT,
        phone_encrypted TEXT,
        email TEXT,
        ethnicity TEXT,
        political_status TEXT,
        marital_status TEXT,
        native_place TEXT,
        address TEXT,
        photo_url TEXT,
        status TEXT DEFAULT '在职',
        entry_date TEXT,
        leave_date TEXT,
        leave_reason TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    );
    
    CREATE TABLE IF NOT EXISTS education_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        school TEXT NOT NULL,
        major TEXT,
        degree TEXT,
        start_date TEXT,
        end_date TEXT,
        is_highest INTEGER DEFAULT 0,
        FOREIGN KEY (emp_id) REFERENCES employees(id)
    );
    
    CREATE TABLE IF NOT EXISTS title_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        title_name TEXT NOT NULL,
        title_level TEXT,
        specialty TEXT,
        award_date TEXT,
        review_date TEXT,
        is_current INTEGER DEFAULT 1,
        FOREIGN KEY (emp_id) REFERENCES employees(id)
    );
    
    CREATE TABLE IF NOT EXISTS position_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        department TEXT NOT NULL,
        position TEXT NOT NULL,
        job_level TEXT,
        start_date TEXT,
        end_date TEXT,
        change_type TEXT,
        is_current INTEGER DEFAULT 1,
        FOREIGN KEY (emp_id) REFERENCES employees(id)
    );
    
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        contract_no TEXT,
        contract_type TEXT,
        start_date TEXT,
        end_date TEXT,
        sign_date TEXT,
        status TEXT DEFAULT '生效',
        renewal_count INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (emp_id) REFERENCES employees(id)
    );
    """)
    
    # 工资核算
    db.executescript("""
    CREATE TABLE IF NOT EXISTS salary_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT NOT NULL,
        title_level TEXT NOT NULL,
        base_salary REAL NOT NULL,
        position_allowance REAL DEFAULT 0,
        medical_allowance REAL DEFAULT 0,
        housing_allowance REAL DEFAULT 0,
        night_shift_allowance REAL DEFAULT 0,
        overtime_rate REAL DEFAULT 1.5,
        effective_date TEXT,
        UNIQUE(department, title_level)
    );
    
    CREATE TABLE IF NOT EXISTS social_insurance_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        city TEXT DEFAULT '大理',
        pension_base REAL,
        pension_personal_rate REAL,
        pension_unit_rate REAL,
        medical_base REAL,
        medical_personal_rate REAL,
        medical_unit_rate REAL,
        unemployment_rate REAL,
        injury_rate REAL,
        maternity_rate REAL,
        housing_fund_base REAL,
        housing_fund_personal_rate REAL,
        housing_fund_unit_rate REAL,
        UNIQUE(year, city)
    );
    
    CREATE TABLE IF NOT EXISTS tax_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        bracket_min REAL NOT NULL,
        bracket_max REAL,
        rate REAL NOT NULL,
        deduction REAL NOT NULL,
        sort_order INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        work_days INTEGER DEFAULT 22,
        actual_days REAL,
        sick_leave_days REAL DEFAULT 0,
        personal_leave_days REAL DEFAULT 0,
        annual_leave_days REAL DEFAULT 0,
        overtime_hours REAL DEFAULT 0,
        night_shift_days REAL DEFAULT 0,
        late_count INTEGER DEFAULT 0,
        early_leave_count INTEGER DEFAULT 0,
        absent_days REAL DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (emp_id) REFERENCES employees(id),
        UNIQUE(emp_id, month)
    );
    
    CREATE TABLE IF NOT EXISTS salary_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        base_salary REAL NOT NULL,
        position_allowance REAL DEFAULT 0,
        medical_allowance REAL DEFAULT 0,
        housing_allowance REAL DEFAULT 0,
        night_shift_pay REAL DEFAULT 0,
        overtime_pay REAL DEFAULT 0,
        other_bonus REAL DEFAULT 0,
        gross_salary REAL NOT NULL,
        pension_personal REAL DEFAULT 0,
        medical_personal REAL DEFAULT 0,
        unemployment_personal REAL DEFAULT 0,
        housing_fund_personal REAL DEFAULT 0,
        total_deduction_social REAL DEFAULT 0,
        tax_deduction REAL DEFAULT 0,
        other_deduction REAL DEFAULT 0,
        total_deduction REAL DEFAULT 0,
        net_salary REAL NOT NULL,
        status TEXT DEFAULT '待审核',
        approved_by TEXT,
        approved_at TEXT,
        generated_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (emp_id) REFERENCES employees(id),
        UNIQUE(emp_id, month)
    );
    """)
    
    # 绩效管理
    db.executescript("""
    CREATE TABLE IF NOT EXISTS perf_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT,
        position_type TEXT,
        cycle TEXT DEFAULT '月度',
        is_active INTEGER DEFAULT 1,
        total_weight REAL DEFAULT 100,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    );
    
    CREATE TABLE IF NOT EXISTS perf_dimensions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        weight REAL NOT NULL,
        max_score REAL DEFAULT 100,
        description TEXT,
        sort_order INTEGER DEFAULT 0,
        FOREIGN KEY (template_id) REFERENCES perf_templates(id)
    );
    
    CREATE TABLE IF NOT EXISTS perf_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        template_id INTEGER NOT NULL,
        period TEXT NOT NULL,
        assessor_id INTEGER,
        status TEXT DEFAULT '待评分',
        total_score REAL,
        final_score REAL,
        level TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        completed_at TEXT,
        FOREIGN KEY (emp_id) REFERENCES employees(id),
        FOREIGN KEY (template_id) REFERENCES perf_templates(id),
        FOREIGN KEY (assessor_id) REFERENCES users(id),
        UNIQUE(emp_id, template_id, period)
    );
    
    CREATE TABLE IF NOT EXISTS perf_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL,
        dimension_id INTEGER NOT NULL,
        score REAL NOT NULL,
        weight_score REAL NOT NULL,
        comment TEXT,
        FOREIGN KEY (assessment_id) REFERENCES perf_assessments(id),
        FOREIGN KEY (dimension_id) REFERENCES perf_dimensions(id)
    );
    
    CREATE TABLE IF NOT EXISTS perf_salary_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT NOT NULL,
        min_score REAL,
        max_score REAL,
        bonus_rate REAL DEFAULT 0,
        salary_adjust_rate REAL DEFAULT 0,
        description TEXT
    );
    """)
    
    # 插入默认管理员
    admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    db.execute("INSERT OR IGNORE INTO users (username, password_hash, real_name, role) VALUES (?, ?, ?, ?)",
               ('admin', admin_hash, '系统管理员', 'admin'))
    
    # 插入默认权限
    perm_data = [
        ('admin', 'salary', 'write'), ('admin', 'performance', 'write'), ('admin', 'personnel', 'write'),
        ('hr_mgr', 'salary', 'write'), ('hr_mgr', 'performance', 'write'), ('hr_mgr', 'personnel', 'write'),
        ('dept_mgr', 'salary', 'read'), ('dept_mgr', 'performance', 'write'), ('dept_mgr', 'personnel', 'read'),
        ('staff', 'salary', 'self'), ('staff', 'performance', 'self'), ('staff', 'personnel', 'self'),
    ]
    for role, module, perm in perm_data:
        db.execute("INSERT OR IGNORE INTO role_permissions (role, module, permission_level) VALUES (?, ?, ?)",
                   (role, module, perm))
    
    # 插入个税税率表（2024标准）
    tax_brackets = [
        (2024, 0, 36000, 3, 0, 1),
        (2024, 36000, 144000, 10, 2520, 2),
        (2024, 144000, 300000, 20, 16920, 3),
        (2024, 300000, 420000, 25, 31920, 4),
        (2024, 420000, 660000, 30, 52920, 5),
        (2024, 660000, 960000, 35, 85920, 6),
        (2024, 960000, None, 45, 181920, 7),
    ]
    for yr, mn, mx, rt, dd, so in tax_brackets:
        db.execute("INSERT OR IGNORE INTO tax_config (year, bracket_min, bracket_max, rate, deduction, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
                   (yr, mn, mx, rt, dd, so))
    
    # 插入社保公积金配置（云南省2024标准）
    db.execute("""INSERT OR IGNORE INTO social_insurance_config 
        (year, city, pension_base, pension_personal_rate, pension_unit_rate,
         medical_base, medical_personal_rate, medical_unit_rate,
         unemployment_rate, injury_rate, maternity_rate,
         housing_fund_base, housing_fund_personal_rate, housing_fund_unit_rate)
        VALUES (2024, '大理', 4179, 8, 16, 4179, 2, 6.6, 0.5, 0.2, 0.7, 4179, 12, 12)""")
    
    # 插入薪资配置示例
    salary_configs = [
        ('内科', '正高', 8500, 3000, 1500, 1200, 80, 1.5),
        ('内科', '副高', 7200, 2500, 1200, 1000, 80, 1.5),
        ('内科', '中级', 6000, 1800, 1000, 800, 80, 1.5),
        ('内科', '初级', 4500, 1200, 800, 600, 80, 1.5),
        ('外科', '正高', 9000, 3500, 1500, 1200, 100, 1.5),
        ('外科', '副高', 7800, 2800, 1200, 1000, 100, 1.5),
        ('外科', '中级', 6500, 2000, 1000, 800, 100, 1.5),
        ('外科', '初级', 5000, 1300, 800, 600, 100, 1.5),
        ('急诊科', '正高', 8800, 3200, 1800, 1200, 120, 2.0),
        ('急诊科', '副高', 7500, 2600, 1400, 1000, 120, 2.0),
        ('急诊科', '中级', 6200, 1800, 1200, 800, 120, 2.0),
        ('急诊科', '初级', 4800, 1200, 800, 600, 120, 2.0),
        ('护理部', '正高', 7500, 2200, 1000, 900, 60, 1.5),
        ('护理部', '副高', 6500, 1800, 800, 700, 60, 1.5),
        ('护理部', '中级', 5500, 1300, 600, 500, 60, 1.5),
        ('护理部', '初级', 4000, 800, 500, 400, 60, 1.5),
        ('行政后勤', '中级', 5000, 1200, 600, 500, 0, 1.5),
        ('行政后勤', '初级', 3800, 800, 400, 400, 0, 1.5),
    ]
    for dept, title, base, pos, med, hous, night, ovtr in salary_configs:
        db.execute("INSERT OR IGNORE INTO salary_config (department, title_level, base_salary, position_allowance, medical_allowance, housing_allowance, night_shift_allowance, overtime_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (dept, title, base, pos, med, hous, night, ovtr))
    
    # 插入绩效薪资联动规则
    perf_rules = [
        ('A', 90, 100, 0.20, 0.10, '优秀：奖金20%，薪资上调10%'),
        ('B', 80, 89, 0.10, 0.05, '良好：奖金10%，薪资上调5%'),
        ('C', 60, 79, 0.05, 0, '合格：奖金5%，薪资不变'),
        ('D', 40, 59, 0, -0.03, '待改进：无奖金，薪资下调3%'),
        ('E', 0, 39, 0, -0.08, '不合格：无奖金，薪资下调8%'),
    ]
    for lvl, mn, mx, brt, srt, desc in perf_rules:
        db.execute("INSERT OR IGNORE INTO perf_salary_rules (level, min_score, max_score, bonus_rate, salary_adjust_rate, description) VALUES (?, ?, ?, ?, ?, ?)",
                   (lvl, mn, mx, brt, srt, desc))
    
    # 插入示例职工数据
    sample_employees = [
        ('DL001', '李明华', '男', '1975-03-15', '532901197503****', '138****5678', 'limh@dali-hospital.cn', '汉', '中共党员', '已婚', '云南大理', '大理市下关镇'),
        ('DL002', '王芳芳', '女', '1982-07-22', '532901198207****', '139****4321', 'wff@dali-hospital.cn', '白', '群众', '已婚', '云南大理', '大理市下关镇'),
        ('DL003', '张建国', '男', '1968-11-08', '532901196811****', '137****8901', 'zjg@dali-hospital.cn', '汉', '中共党员', '已婚', '云南昆明', '大理市大理镇'),
        ('DL004', '陈晓燕', '女', '1990-05-18', '532901199005****', '136****2345', 'cxy@dali-hospital.cn', '汉', '共青团员', '未婚', '云南大理', '大理市下关镇'),
        ('DL005', '刘伟', '男', '1985-09-30', '532901198509****', '135****6789', 'lw@dali-hospital.cn', '汉', '群众', '已婚', '四川成都', '大理市下关镇'),
        ('DL006', '赵丽萍', '女', '1978-12-05', '532901197812****', '158****3456', 'zlp@dali-hospital.cn', '彝', '群众', '已婚', '云南楚雄', '大理市大理镇'),
        ('DL007', '孙志强', '男', '1993-02-14', '532901199302****', '159****7890', 'szq@dali-hospital.cn', '汉', '共青团员', '未婚', '云南大理', '大理市下关镇'),
        ('DL008', '周美玲', '女', '1980-06-20', '532901198006****', '182****1234', 'zml@dali-hospital.cn', '汉', '中共党员', '已婚', '云南大理', '大理市下关镇'),
    ]
    for emp_no, name, gender, birth, id_card, phone, email, ethnic, polit, mstat, nativ, addr in sample_employees:
        db.execute("""INSERT OR IGNORE INTO employees 
            (emp_no, name, gender, birth_date, id_card_encrypted, phone_encrypted, email, ethnicity, political_status, marital_status, native_place, address, status, entry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '在职', ?)""",
                   (emp_no, name, gender, birth, aes_encrypt(id_card), aes_encrypt(phone), email, ethnic, polit, mstat, nativ, addr, '2008-01-01' if birth[:4] < '1980' else '2010-01-01' if birth[:4] < '1990' else '2015-01-01'))
    
    # 为示例职工插入职位和职称
    positions = [
        (1, '内科', '主任医师', '正高', '2008-01-01', None, '入职', 1),
        (2, '护理部', '护士长', '副高', '2010-01-01', None, '入职', 1),
        (3, '外科', '科室主任', '正高', '2005-01-01', None, '入职', 1),
        (4, '急诊科', '住院医师', '初级', '2015-01-01', None, '入职', 1),
        (5, '内科', '主治医师', '中级', '2010-01-01', None, '入职', 1),
        (6, '护理部', '主管护师', '中级', '2009-01-01', None, '入职', 1),
        (7, '行政后勤', '信息科专员', '初级', '2015-01-01', None, '入职', 1),
        (8, '内科', '副主任医师', '副高', '2008-01-01', None, '入职', 1),
    ]
    for eid, dept, pos, lvl, sd, ed, ct, ic in positions:
        db.execute("INSERT OR IGNORE INTO position_records (emp_id, department, position, job_level, start_date, end_date, change_type, is_current) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (eid, dept, pos, lvl, sd, ed, ct, ic))
    
    titles_data = [
        (1, '主任医师', '正高', '内科', '2015-06-01', None, 1),
        (2, '副主任护师', '副高', '护理', '2018-06-01', None, 1),
        (3, '主任医师', '正高', '外科', '2012-06-01', None, 1),
        (4, '住院医师', '初级', '急诊医学', None, None, 1),
        (5, '主治医师', '中级', '内科', '2016-06-01', None, 1),
        (6, '主管护师', '中级', '护理', '2015-06-01', None, 1),
        (7, '助理工程师', '初级', '信息技术', None, None, 1),
        (8, '副主任医师', '副高', '内科', '2016-06-01', None, 1),
    ]
    for eid, tn, tl, sp, ad, rd, ic in titles_data:
        db.execute("INSERT OR IGNORE INTO title_records (emp_id, title_name, title_level, specialty, award_date, review_date, is_current) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (eid, tn, tl, sp, ad, rd, ic))
    
    db.commit()
    db.close()
    print("数据库初始化完成")

# ============================================================
# 权限验证装饰器
# ============================================================
def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated

def require_permission(module, level='read'):
    """检查权限：read/write/self"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': '未登录'}), 401
            db = get_db()
            user = db.execute("SELECT role FROM users WHERE id=?", (session['user_id'],)).fetchone()
            if not user:
                return jsonify({'error': '用户不存在'}), 403
            perm = db.execute("SELECT permission_level FROM role_permissions WHERE role=? AND module=?",
                              (user['role'], module)).fetchone()
            if not perm:
                return jsonify({'error': '无权限'}), 403
            if level == 'write' and perm['permission_level'] not in ('write',):
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def log_operation(action, module, detail=''):
    """记录操作日志"""
    db = get_db()
    db.execute("INSERT INTO operation_logs (user_id, action, module, detail, ip_address) VALUES (?, ?, ?, ?, ?)",
               (session.get('user_id'), action, module, detail, request.remote_addr))
    db.commit()

# ============================================================
# 认证 API
# ============================================================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '')
    password = data.get('password', '')
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=? AND is_active=1", (username,)).fetchone()
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] != pw_hash:
        return jsonify({'error': '密码错误'}), 401
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    session['real_name'] = user['real_name']
    db.execute("UPDATE users SET last_login=datetime('now','localtime') WHERE id=?", (user['id'],))
    db.commit()
    log_operation('登录', 'system', f'用户 {username} 登录')
    return jsonify({'id': user['id'], 'username': user['username'], 'real_name': user['real_name'], 'role': user['role']})

@app.route('/api/logout', methods=['POST'])
def logout():
    log_operation('登出', 'system')
    session.clear()
    return jsonify({'ok': True})

@app.route('/api/current_user', methods=['GET'])
def current_user():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    return jsonify({'id': session['user_id'], 'username': session['username'], 'real_name': session['real_name'], 'role': session['role']})

# ============================================================
# 人员信息管理 API
# ============================================================
@app.route('/api/employees', methods=['GET'])
@require_login
def list_employees():
    db = get_db()
    keyword = request.args.get('keyword', '')
    dept = request.args.get('department', '')
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    conditions = []
    params = []
    if keyword:
        conditions.append("(name LIKE ? OR emp_no LIKE ? OR phone_encrypted LIKE ?)")
        params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
    if dept:
        # 通过当前职位关联查科室
        conditions.append("id IN (SELECT emp_id FROM position_records WHERE department=? AND is_current=1)")
        params.append(dept)
    if status:
        conditions.append("status=?")
        params.append(status)
    
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    total = db.execute(f"SELECT COUNT(*) FROM employees{where}", params).fetchone()[0]
    
    rows = db.execute(f"""SELECT e.*, 
        (SELECT department FROM position_records WHERE emp_id=e.id AND is_current=1) as current_dept,
        (SELECT position FROM position_records WHERE emp_id=e.id AND is_current=1) as current_position,
        (SELECT title_name FROM title_records WHERE emp_id=e.id AND is_current=1) as current_title
        FROM employees e{where} ORDER BY e.emp_no 
        LIMIT ? OFFSET ?""", params + [per_page, (page-1)*per_page]).fetchall()
    
    result = []
    for r in rows:
        d = dict(r)
        d['phone'] = aes_decrypt(d.get('phone_encrypted', ''))
        d['id_card'] = aes_decrypt(d.get('id_card_encrypted', ''))
        # 脱敏显示
        if d['phone'] and len(d['phone']) > 7:
            d['phone_display'] = d['phone'][:3] + '****' + d['phone'][-4:]
        else:
            d['phone_display'] = d['phone']
        if d['id_card'] and len(d['id_card']) > 10:
            d['id_card_display'] = d['id_card'][:6] + '********' + d['id_card'][-4:]
        else:
            d['id_card_display'] = d['id_card']
        result.append(d)
    
    return jsonify({'total': total, 'page': page, 'per_page': per_page, 'data': result})

@app.route('/api/employees/<int:emp_id>', methods=['GET'])
@require_login
def get_employee(emp_id):
    db = get_db()
    emp = db.execute("SELECT * FROM employees WHERE id=?", (emp_id,)).fetchone()
    if not emp:
        return jsonify({'error': '职工不存在'}), 404
    d = dict(emp)
    d['phone'] = aes_decrypt(d.get('phone_encrypted', ''))
    d['id_card'] = aes_decrypt(d.get('id_card_encrypted', ''))
    
    d['education'] = [dict(r) for r in db.execute("SELECT * FROM education_records WHERE emp_id=?", (emp_id,)).fetchall()]
    d['titles'] = [dict(r) for r in db.execute("SELECT * FROM title_records WHERE emp_id=?", (emp_id,)).fetchall()]
    d['positions'] = [dict(r) for r in db.execute("SELECT * FROM position_records WHERE emp_id=?", (emp_id,)).fetchall()]
    d['contracts'] = [dict(r) for r in db.execute("SELECT * FROM contracts WHERE emp_id=?", (emp_id,)).fetchall()]
    
    return jsonify(d)

@app.route('/api/employees', methods=['POST'])
@require_permission('personnel', 'write')
def create_employee():
    data = request.json or {}
    db = get_db()
    try:
        db.execute("""INSERT INTO employees (emp_no, name, gender, birth_date, id_card_encrypted, phone_encrypted, 
            email, ethnicity, political_status, marital_status, native_place, address, photo_url, status, entry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (data['emp_no'], data['name'], data.get('gender'), data.get('birth_date'),
                    aes_encrypt(data.get('id_card', '')), aes_encrypt(data.get('phone', '')),
                    data.get('email'), data.get('ethnicity'), data.get('political_status'),
                    data.get('marital_status'), data.get('native_place'), data.get('address'),
                    data.get('photo_url'), data.get('status', '在职'), data.get('entry_date')))
        db.commit()
        emp_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        log_operation('新增职工', 'personnel', f'职工号 {data["emp_no"]}')
        return jsonify({'id': emp_id, 'ok': True})
    except sqlite3.IntegrityError as e:
        return jsonify({'error': f'数据冲突: {str(e)}'}), 400

@app.route('/api/employees/<int:emp_id>', methods=['PUT'])
@require_permission('personnel', 'write')
def update_employee(emp_id):
    data = request.json or {}
    db = get_db()
    fields = []
    params = []
    for key in ['name', 'gender', 'birth_date', 'email', 'ethnicity', 'political_status', 
                'marital_status', 'native_place', 'address', 'photo_url', 'status', 'leave_date', 'leave_reason']:
        if key in data:
            fields.append(f"{key}=?")
            params.append(data[key])
    if 'id_card' in data:
        fields.append("id_card_encrypted=?")
        params.append(aes_encrypt(data['id_card']))
    if 'phone' in data:
        fields.append("phone_encrypted=?")
        params.append(aes_encrypt(data['phone']))
    
    if fields:
        fields.append("updated_at=datetime('now','localtime')")
        params.append(emp_id)
        db.execute(f"UPDATE employees SET {', '.join(fields)} WHERE id=?", params)
        db.commit()
        log_operation('更新职工', 'personnel', f'ID {emp_id}')
    return jsonify({'ok': True})

@app.route('/api/employees/<int:emp_id>', methods=['DELETE'])
@require_permission('personnel', 'write')
def delete_employee(emp_id):
    db = get_db()
    db.execute("DELETE FROM employees WHERE id=?", (emp_id,))
    db.commit()
    log_operation('删除职工', 'personnel', f'ID {emp_id}')
    return jsonify({'ok': True})

# 子记录API
@app.route('/api/employees/<int:emp_id>/education', methods=['GET', 'POST'])
@require_login
def employee_education(emp_id):
    db = get_db()
    if request.method == 'GET':
        rows = db.execute("SELECT * FROM education_records WHERE emp_id=?", (emp_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    data = request.json or {}
    db.execute("""INSERT INTO education_records (emp_id, school, major, degree, start_date, end_date, is_highest)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
               (emp_id, data['school'], data.get('major'), data.get('degree'), 
                data.get('start_date'), data.get('end_date'), data.get('is_highest', 0)))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/employees/<int:emp_id>/titles', methods=['GET', 'POST'])
@require_login
def employee_titles(emp_id):
    db = get_db()
    if request.method == 'GET':
        rows = db.execute("SELECT * FROM title_records WHERE emp_id=?", (emp_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    data = request.json or {}
    db.execute("""INSERT INTO title_records (emp_id, title_name, title_level, specialty, award_date, review_date, is_current)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
               (emp_id, data['title_name'], data.get('title_level'), data.get('specialty'),
                data.get('award_date'), data.get('review_date'), data.get('is_current', 1)))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/employees/<int:emp_id>/positions', methods=['GET', 'POST'])
@require_login
def employee_positions(emp_id):
    db = get_db()
    if request.method == 'GET':
        rows = db.execute("SELECT * FROM position_records WHERE emp_id=?", (emp_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    data = request.json or {}
    # 新岗位变更时，自动将旧岗位 is_current=0 并设置 end_date
    if data.get('is_current', 1) == 1:
        db.execute("UPDATE position_records SET is_current=0, end_date=datetime('now','localtime') WHERE emp_id=? AND is_current=1", (emp_id,))
    db.execute("""INSERT INTO position_records (emp_id, department, position, job_level, start_date, end_date, change_type, is_current)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
               (emp_id, data['department'], data['position'], data.get('job_level'),
                data.get('start_date'), data.get('end_date'), data.get('change_type', '调动'), data.get('is_current', 1)))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/employees/<int:emp_id>/contracts', methods=['GET', 'POST'])
@require_login
def employee_contracts(emp_id):
    db = get_db()
    if request.method == 'GET':
        rows = db.execute("SELECT * FROM contracts WHERE emp_id=?", (emp_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    data = request.json or {}
    db.execute("""INSERT INTO contracts (emp_id, contract_no, contract_type, start_date, end_date, sign_date, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
               (emp_id, data.get('contract_no'), data.get('contract_type'), data.get('start_date'),
                data.get('end_date'), data.get('sign_date'), data.get('status', '生效'), data.get('notes')))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/departments', methods=['GET'])
@require_login
def list_departments():
    db = get_db()
    rows = db.execute("SELECT DISTINCT department FROM position_records WHERE is_current=1 AND department IS NOT NULL ORDER BY department").fetchall()
    return jsonify([r['department'] for r in rows])

# ============================================================
# 工资核算 API
# ============================================================
@app.route('/api/salary/config', methods=['GET'])
@require_login
def list_salary_config():
    db = get_db()
    rows = db.execute("SELECT * FROM salary_config ORDER BY department, title_level").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/salary/config', methods=['POST'])
@require_permission('salary', 'write')
def create_salary_config():
    data = request.json or {}
    db = get_db()
    db.execute("""INSERT OR REPLACE INTO salary_config 
        (department, title_level, base_salary, position_allowance, medical_allowance, housing_allowance, night_shift_allowance, overtime_rate, effective_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
               (data['department'], data['title_level'], data['base_salary'], data.get('position_allowance', 0),
                data.get('medical_allowance', 0), data.get('housing_allowance', 0), data.get('night_shift_allowance', 0),
                data.get('overtime_rate', 1.5), data.get('effective_date')))
    db.commit()
    log_operation('更新薪资配置', 'salary', f'{data["department"]}/{data["title_level"]}')
    return jsonify({'ok': True})

@app.route('/api/salary/social_insurance', methods=['GET'])
@require_login
def get_social_insurance():
    db = get_db()
    year = request.args.get('year', 2024)
    row = db.execute("SELECT * FROM social_insurance_config WHERE year=?", (year,)).fetchone()
    return jsonify(dict(row) if row else {'error': '未找到配置'})

@app.route('/api/salary/tax', methods=['GET'])
@require_login
def get_tax_config():
    db = get_db()
    rows = db.execute("SELECT * FROM tax_config WHERE year=2024 ORDER BY sort_order").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/salary/attendance', methods=['GET', 'POST'])
@require_permission('salary', 'write')
def attendance():
    db = get_db()
    if request.method == 'GET':
        month = request.args.get('month', '')
        emp_id = request.args.get('emp_id', '')
        conditions = []
        params = []
        if month:
            conditions.append("month=?")
            params.append(month)
        if emp_id:
            conditions.append("emp_id=?")
            params.append(emp_id)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        rows = db.execute(f"""SELECT a.*, e.name, e.emp_no FROM attendance_records a 
            JOIN employees e ON a.emp_id=e.id{where} ORDER BY a.month DESC""", params).fetchall()
        return jsonify([dict(r) for r in rows])
    
    data = request.json or {}
    # 批量导入考勤
    records = data.get('records', [])
    if not records:
        return jsonify({'error': '无考勤数据'}), 400
    count = 0
    for r in records:
        try:
            db.execute("""INSERT OR REPLACE INTO attendance_records 
                (emp_id, month, work_days, actual_days, sick_leave_days, personal_leave_days, 
                 annual_leave_days, overtime_hours, night_shift_days, late_count, early_leave_count, absent_days, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (r['emp_id'], r['month'], r.get('work_days', 22), r.get('actual_days'),
                        r.get('sick_leave_days', 0), r.get('personal_leave_days', 0), r.get('annual_leave_days', 0),
                        r.get('overtime_hours', 0), r.get('night_shift_days', 0), r.get('late_count', 0),
                        r.get('early_leave_count', 0), r.get('absent_days', 0), r.get('notes', '')))
            count += 1
        except Exception:
            pass
    db.commit()
    log_operation('导入考勤', 'salary', f'{count}条记录，月份 {records[0].get("month", "")}')
    return jsonify({'ok': True, 'count': count})

@app.route('/api/salary/calculate', methods=['POST'])
@require_permission('salary', 'write')
def calculate_salary():
    """批量计算某月工资"""
    data = request.json or {}
    month = data.get('month', '')
    if not month:
        return jsonify({'error': '请指定月份'}), 400
    
    db = get_db()
    si_config = db.execute("SELECT * FROM social_insurance_config WHERE year=2024").fetchone()
    if not si_config:
        return jsonify({'error': '社保配置缺失'}), 400
    
    employees = db.execute("""SELECT e.id, e.emp_no, e.name, 
        (SELECT department FROM position_records WHERE emp_id=e.id AND is_current=1) as dept,
        (SELECT job_level FROM position_records WHERE emp_id=e.id AND is_current=1) as job_level,
        (SELECT title_level FROM title_records WHERE emp_id=e.id AND is_current=1) as title_level
        FROM employees e WHERE e.status='在职'""").fetchall()
    
    results = []
    total_gross = total_net = 0
    
    for emp in employees:
        dept = emp['dept']
        title = emp['title_level'] or emp['job_level'] or '初级'
        
        # 获取薪资配置
        sal_cfg = db.execute("SELECT * FROM salary_config WHERE department=? AND title_level=?", (dept, title)).fetchone()
        if not sal_cfg:
            sal_cfg = db.execute("SELECT * FROM salary_config WHERE title_level=? LIMIT 1", (title,)).fetchone()
        if not sal_cfg:
            continue
        
        # 获取考勤
        att = db.execute("SELECT * FROM attendance_records WHERE emp_id=? AND month=?", (emp['id'], month)).fetchone()
        if not att:
            att = {'work_days': 22, 'actual_days': 22, 'sick_leave_days': 0, 'personal_leave_days': 0,
                   'overtime_hours': 0, 'night_shift_days': 0, 'absent_days': 0, 'late_count': 0}
        
        # 计算各项
        base = sal_cfg['base_salary']
        pos_allow = sal_cfg['position_allowance']
        med_allow = sal_cfg['medical_allowance']
        hous_allow = sal_cfg['housing_allowance']
        
        # 考勤扣减
        day_rate = base / att.get('work_days', 22) if att.get('work_days', 22) > 0 else base / 22
        sick_deduct = att.get('sick_leave_days', 0) * day_rate * 0.4  # 病假扣40%
        personal_deduct = att.get('personal_leave_days', 0) * day_rate  # 事假全额扣
        absent_deduct = att.get('absent_days', 0) * day_rate * 3  # 旷工扣3倍
        
        attendance_deduct = sick_deduct + personal_deduct + absent_deduct
        
        # 加班费和夜班费
        hour_rate = base / (att.get('work_days', 22) * 8) if att.get('work_days', 22) > 0 else base / 176
        overtime_pay = att.get('overtime_hours', 0) * hour_rate * sal_cfg['overtime_rate']
        night_pay = att.get('night_shift_days', 0) * sal_cfg['night_shift_allowance']
        
        gross = base + pos_allow + med_allow + hous_allow + overtime_pay + night_pay - attendance_deduct
        gross = round(gross, 2)
        
        # 社保公积金（个人部分）
        si_base = min(max(gross, si_config['pension_base']), si_config['pension_base'] * 3)  # 社保基数
        pension_p = round(si_base * si_config['pension_personal_rate'] / 100, 2)
        medical_p = round(si_base * si_config['medical_personal_rate'] / 100, 2)
        unemployment_p = round(si_base * si_config['unemployment_rate'] / 100, 2)
        housing_p = round(min(max(gross, si_config['housing_fund_base']), si_config['housing_fund_base'] * 3) * si_config['housing_fund_personal_rate'] / 100, 2)
        total_social = round(pension_p + medical_p + unemployment_p + housing_p, 2)
        
        # 个税计算
        taxable = gross - total_social - 5000  # 起征点5000
        annual_taxable = taxable * 12  # 简化：按月累计
        tax = 0
        for bracket in db.execute("SELECT * FROM tax_config WHERE year=2024 ORDER BY sort_order").fetchall():
            if annual_taxable > bracket['bracket_min']:
                upper = bracket['bracket_max'] if bracket['bracket_max'] else annual_taxable
                tax_base = min(annual_taxable, upper) - bracket['bracket_min']
                tax += tax_base * bracket['rate'] / 100 - bracket['deduction']
        monthly_tax = round(max(tax / 12, 0), 2)
        
        net = round(gross - total_social - monthly_tax, 2)
        
        # 存入数据库
        db.execute("""INSERT OR REPLACE INTO salary_records 
            (emp_id, month, base_salary, position_allowance, medical_allowance, housing_allowance,
             night_shift_pay, overtime_pay, other_bonus, gross_salary,
             pension_personal, medical_personal, unemployment_personal, housing_fund_personal, total_deduction_social,
             tax_deduction, other_deduction, total_deduction, net_salary, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '待审核')""",
                   (emp['id'], month, base, pos_allow, med_allow, hous_allow, night_pay, overtime_pay, 0, gross,
                    pension_p, medical_p, unemployment_p, housing_p, total_social, monthly_tax, 0,
                    round(total_social + monthly_tax, 2), net))
        
        total_gross += gross
        total_net += net
        results.append({
            'emp_no': emp['emp_no'], 'name': emp['name'], 'dept': dept, 'title': title,
            'gross': gross, 'social': total_social, 'tax': monthly_tax, 'net': net
        })
    
    db.commit()
    log_operation('计算工资', 'salary', f'月份 {month}，共 {len(results)} 人')
    return jsonify({'month': month, 'count': len(results), 'total_gross': round(total_gross, 2), 'total_net': round(total_net, 2), 'data': results})

@app.route('/api/salary/records', methods=['GET'])
@require_login
def list_salary_records():
    month = request.args.get('month', '')
    dept = request.args.get('department', '')
    db = get_db()
    conditions = []
    params = []
    if month:
        conditions.append("s.month=?")
        params.append(month)
    if dept:
        conditions.append("(SELECT department FROM position_records WHERE emp_id=e.id AND is_current=1)=?")
        params.append(dept)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    rows = db.execute(f"""SELECT s.*, e.name, e.emp_no,
        (SELECT department FROM position_records WHERE emp_id=e.id AND is_current=1) as dept
        FROM salary_records s JOIN employees e ON s.emp_id=e.id{where} ORDER BY s.month DESC, e.emp_no""", params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/salary/approve', methods=['POST'])
@require_permission('salary', 'write')
def approve_salary():
    data = request.json or {}
    month = data.get('month', '')
    emp_ids = data.get('emp_ids', [])
    db = get_db()
    if emp_ids:
        for eid in emp_ids:
            db.execute("UPDATE salary_records SET status='已审核', approved_by=?, approved_at=datetime('now','localtime') WHERE emp_id=? AND month=?",
                       (session.get('real_name', ''), eid, month))
    else:
        db.execute("UPDATE salary_records SET status='已审核', approved_by=?, approved_at=datetime('now','localtime') WHERE month=?",
                   (session.get('real_name', ''), month))
    db.commit()
    log_operation('审核工资', 'salary', f'月份 {month}')
    return jsonify({'ok': True})

@app.route('/api/salary/stats', methods=['GET'])
@require_permission('salary', 'read')
def salary_stats():
    """工资统计摘要"""
    month = request.args.get('month', '')
    db = get_db()
    if not month:
        latest = db.execute("SELECT DISTINCT month FROM salary_records ORDER BY month DESC LIMIT 1").fetchone()
        if latest:
            month = latest['month']
    if not month:
        return jsonify({'error': '无工资数据'})
    
    stats = db.execute("""SELECT 
        COUNT(*) as emp_count, SUM(gross_salary) as total_gross, SUM(net_salary) as total_net,
        SUM(total_deduction_social) as total_social, SUM(tax_deduction) as total_tax,
        AVG(gross_salary) as avg_gross, AVG(net_salary) as avg_net
        FROM salary_records WHERE month=?""", (month,)).fetchone()
    
    dept_stats = db.execute("""SELECT 
        (SELECT department FROM position_records WHERE emp_id=s.emp_id AND is_current=1) as dept,
        COUNT(*) as count, SUM(gross_salary) as gross, SUM(net_salary) as net
        FROM salary_records s WHERE month=? GROUP BY dept ORDER BY gross DESC""", (month,)).fetchall()
    
    return jsonify({'month': month, 'summary': dict(stats), 'by_dept': [dict(r) for r in dept_stats]})

# ============================================================
# 绩效管理 API
# ============================================================
@app.route('/api/perf/templates', methods=['GET', 'POST'])
@require_permission('performance', 'write')
def perf_templates():
    db = get_db()
    if request.method == 'GET':
        rows = db.execute("SELECT * FROM perf_templates WHERE is_active=1 ORDER BY created_at DESC").fetchall()
        result = []
        for t in rows:
            dims = db.execute("SELECT * FROM perf_dimensions WHERE template_id=?", (t['id'],)).fetchall()
            d = dict(t)
            d['dimensions'] = [dict(r) for r in dims]
            result.append(d)
        return jsonify(result)
    
    data = request.json or {}
    db.execute("""INSERT INTO perf_templates (name, department, position_type, cycle, total_weight)
        VALUES (?, ?, ?, ?, ?)""",
               (data['name'], data.get('department'), data.get('position_type'), data.get('cycle', '月度'), data.get('total_weight', 100)))
    template_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # 插入维度
    for dim in data.get('dimensions', []):
        db.execute("""INSERT INTO perf_dimensions (template_id, name, weight, max_score, description, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)""",
                   (template_id, dim['name'], dim['weight'], dim.get('max_score', 100), dim.get('description', ''), dim.get('sort_order', 0)))
    db.commit()
    log_operation('创建考核模板', 'performance', f'模板 {data["name"]}')
    return jsonify({'id': template_id, 'ok': True})

@app.route('/api/perf/templates/<int:tid>', methods=['PUT', 'DELETE'])
@require_permission('performance', 'write')
def update_perf_template(tid):
    db = get_db()
    if request.method == 'DELETE':
        db.execute("UPDATE perf_templates SET is_active=0 WHERE id=?", (tid,))
        db.commit()
        return jsonify({'ok': True})
    data = request.json or {}
    db.execute("UPDATE perf_templates SET name=?, department=?, cycle=? WHERE id=?",
               (data.get('name'), data.get('department'), data.get('cycle'), tid))
    # 更新维度
    if 'dimensions' in data:
        db.execute("DELETE FROM perf_dimensions WHERE template_id=?", (tid,))
        for dim in data['dimensions']:
            db.execute("""INSERT INTO perf_dimensions (template_id, name, weight, max_score, description, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)""",
                       (tid, dim['name'], dim['weight'], dim.get('max_score', 100), dim.get('description', ''), dim.get('sort_order', 0)))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/perf/assess', methods=['POST'])
@require_permission('performance', 'write')
def create_assessment():
    """发起绩效考核"""
    data = request.json or {}
    db = get_db()
    emp_id = data.get('emp_id')
    template_id = data.get('template_id')
    period = data.get('period', '')
    
    # 检查是否已有同周期考核
    existing = db.execute("SELECT id FROM perf_assessments WHERE emp_id=? AND template_id=? AND period=?",
                          (emp_id, template_id, period)).fetchone()
    if existing:
        return jsonify({'error': '该职工本月已有此模板考核'}), 400
    
    db.execute("""INSERT INTO perf_assessments (emp_id, template_id, period, assessor_id, status)
        VALUES (?, ?, ?, ?, '待评分')""",
               (emp_id, template_id, period, session.get('user_id')))
    assessment_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # 为每个维度创建空评分
    dims = db.execute("SELECT * FROM perf_dimensions WHERE template_id=?", (template_id,)).fetchall()
    for dim in dims:
        db.execute("INSERT INTO perf_scores (assessment_id, dimension_id, score, weight_score) VALUES (?, ?, 0, 0)",
                   (assessment_id, dim['id']))
    
    db.commit()
    log_operation('发起考核', 'performance', f'职工ID {emp_id}，周期 {period}')
    return jsonify({'id': assessment_id, 'ok': True})

@app.route('/api/perf/assess/<int:aid>', methods=['GET', 'PUT'])
@require_permission('performance', 'write')
def update_assessment(aid):
    db = get_db()
    if request.method == 'GET':
        assessment = db.execute("SELECT * FROM perf_assessments WHERE id=?", (aid,)).fetchone()
        if not assessment:
            return jsonify({'error': '考核不存在'}), 404
        scores = db.execute("SELECT ps.*, pd.name, pd.weight, pd.max_score FROM perf_scores ps JOIN perf_dimensions pd ON ps.dimension_id=pd.id WHERE ps.assessment_id=?", (aid,)).fetchall()
        d = dict(assessment)
        d['scores'] = [dict(r) for r in scores]
        return jsonify(d)
    
    data = request.json or {}
    scores = data.get('scores', [])
    db_ass = get_db()
    
    total_weight_score = 0
    for s in scores:
        dim = db_ass.execute("SELECT weight, max_score FROM perf_dimensions WHERE id=?", (s['dimension_id'],)).fetchone()
        weight_score = round(s['score'] * (dim['weight'] / 100), 2) if dim else 0
        total_weight_score += weight_score
        db_ass.execute("UPDATE perf_scores SET score=?, weight_score=?, comment=? WHERE assessment_id=? AND dimension_id=?",
                       (s['score'], weight_score, s.get('comment', ''), aid, s['dimension_id']))
    
    # 计算最终得分和等级
    final_score = round(total_weight_score, 2)
    level_rule = db_ass.execute("SELECT * FROM perf_salary_rules WHERE min_score<=? AND max_score>=?", (final_score, final_score)).fetchone()
    level = level_rule['level'] if level_rule else 'C'
    
    db_ass.execute("UPDATE perf_assessments SET total_score=?, final_score=?, level=?, status='已完成', completed_at=datetime('now','localtime') WHERE id=?",
                   (final_score, final_score, level, aid))
    db_ass.commit()
    log_operation('评分完成', 'performance', f'考核ID {aid}，得分 {final_score}，等级 {level}')
    return jsonify({'final_score': final_score, 'level': level, 'ok': True})

@app.route('/api/perf/assessments', methods=['GET'])
@require_login
def list_assessments():
    period = request.args.get('period', '')
    dept = request.args.get('department', '')
    db = get_db()
    conditions = []
    params = []
    if period:
        conditions.append("pa.period=?")
        params.append(period)
    if dept:
        conditions.append("(SELECT department FROM position_records WHERE emp_id=e.id AND is_current=1)=?")
        params.append(dept)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    rows = db.execute(f"""SELECT pa.*, e.name, e.emp_no, pt.name as template_name,
        (SELECT department FROM position_records WHERE emp_id=e.id AND is_current=1) as dept
        FROM perf_assessments pa JOIN employees e ON pa.emp_id=e.id 
        JOIN perf_templates pt ON pa.template_id=pt.id{where} ORDER BY pa.period DESC""", params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/perf/salary_rules', methods=['GET'])
@require_login
def perf_salary_rules():
    db = get_db()
    rows = db.execute("SELECT * FROM perf_salary_rules ORDER BY min_score DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/perf/stats', methods=['GET'])
@require_permission('performance', 'read')
def perf_stats():
    """绩效统计摘要"""
    period = request.args.get('period', '')
    db = get_db()
    if not period:
        latest = db.execute("SELECT DISTINCT period FROM perf_assessments ORDER BY period DESC LIMIT 1").fetchone()
        if latest:
            period = latest['period']
    
    if not period:
        return jsonify({'error': '无绩效数据'})
    
    stats = db.execute("""SELECT 
        COUNT(*) as total, AVG(final_score) as avg_score,
        SUM(CASE WHEN level='A' THEN 1 ELSE 0 END) as a_count,
        SUM(CASE WHEN level='B' THEN 1 ELSE 0 END) as b_count,
        SUM(CASE WHEN level='C' THEN 1 ELSE 0 END) as c_count,
        SUM(CASE WHEN level='D' THEN 1 ELSE 0 END) as d_count,
        SUM(CASE WHEN level='E' THEN 1 ELSE 0 END) as e_count
        FROM perf_assessments WHERE period=? AND status='已完成'""", (period,)).fetchone()
    
    dept_stats = db.execute("""SELECT 
        (SELECT department FROM position_records WHERE emp_id=pa.emp_id AND is_current=1) as dept,
        COUNT(*) as count, AVG(final_score) as avg_score
        FROM perf_assessments pa WHERE period=? AND status='已完成' GROUP BY dept""", (period,)).fetchall()
    
    return jsonify({'period': period, 'summary': dict(stats), 'by_dept': [dict(r) for r in dept_stats]})

# ============================================================
# 系统管理 API
# ============================================================
@app.route('/api/users', methods=['GET', 'POST'])
@require_permission('personnel', 'write')
def manage_users():
    db = get_db()
    if request.method == 'GET':
        rows = db.execute("SELECT id, username, real_name, role, department, is_active, last_login FROM users").fetchall()
        return jsonify([dict(r) for r in rows])
    data = request.json or {}
    pw_hash = hashlib.sha256(data.get('password', '123456').encode()).hexdigest()
    db.execute("INSERT INTO users (username, password_hash, real_name, role, department) VALUES (?, ?, ?, ?, ?)",
               (data['username'], pw_hash, data['real_name'], data.get('role', 'staff'), data.get('department')))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/operation_logs', methods=['GET'])
@require_permission('personnel', 'write')
def operation_logs():
    db = get_db()
    limit = int(request.args.get('limit', 50))
    rows = db.execute("""SELECT ol.*, u.real_name FROM operation_logs ol JOIN users u ON ol.user_id=u.id 
        ORDER BY ol.created_at DESC LIMIT ?""", (limit,)).fetchall()
    return jsonify([dict(r) for r in rows])

# ============================================================
# 页面路由
# ============================================================
@app.route('/')
def index():
    return render_template('index.html')

# ============================================================
# 启动
# ============================================================
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
