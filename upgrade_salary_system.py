"""
事业单位人员信息和工资体系升级脚本
按照国家标准完善人员信息模块和工资构成
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'hospital_hr.db')

def upgrade_database():
    """升级数据库结构"""
    conn = sqlite3.connect(DB_PATH)
    db = conn.cursor()
    
    print("=" * 60)
    print("事业单位人力资源系统升级")
    print("=" * 60)
    
    # 1. 扩展employees表
    print("\n【1】扩展职工信息表...")
    
    new_fields = {
        'position_level': 'TEXT',  # 岗位等级(管理/专技/工勤)
        'professional_title': 'TEXT',  # 专业技术职称
        'title_level': 'TEXT',  # 职称等级
        'post_level': 'TEXT',  # 岗位级别
        'salary_grade': 'INTEGER',  # 薪级
        'work_years': 'INTEGER',  # 工龄
        'service_years': 'INTEGER',  # 本单位工龄
        'education_level': 'TEXT',  # 学历
        'degree_type': 'TEXT',  # 学位
        'personnel_type': 'TEXT',  # 人员类别(在编/合同制等)
        'staff_category': 'TEXT',  # 职工分类
        'appointment_date': 'TEXT',  # 聘任日期
        'social_security_no': 'TEXT',  # 社保号
        'housing_fund_no': 'TEXT',  # 公积金账号
        'bank_account': 'TEXT',  # 银行账号
        'bank_name': 'TEXT',  # 开户银行
    }
    
    for field_name, field_type in new_fields.items():
        try:
            db.execute(f"ALTER TABLE employees ADD COLUMN {field_name} {field_type}")
            print(f"  ✓ {field_name}")
        except sqlite3.OperationalError:
            print(f"  ⊙ {field_name} (已存在)")
    
    # 2. 创建工资配置表
    print("\n【2】创建工资项目配置表...")
    
    # 删除旧表(如果存在)
    db.executescript("""
        DROP TABLE IF EXISTS salary_item_categories;
        DROP TABLE IF EXISTS salary_items_config;
        DROP TABLE IF EXISTS tax_brackets;
        DROP TABLE IF EXISTS social_security_config;
    """)
    
    # 重新创建表
    db.executescript("""
    CREATE TABLE IF NOT EXISTS salary_item_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL,
        category_code TEXT NOT NULL UNIQUE,
        description TEXT,
        sort_order INTEGER DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS salary_items_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        item_code TEXT NOT NULL UNIQUE,
        category_id INTEGER,
        item_type TEXT NOT NULL,
        calculation_type TEXT,
        formula TEXT,
        base_value REAL DEFAULT 0,
        ratio REAL,
        is_taxable INTEGER DEFAULT 1,
        is_visible INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        description TEXT,
        FOREIGN KEY (category_id) REFERENCES salary_item_categories(id)
    );
    
    CREATE TABLE IF NOT EXISTS tax_brackets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level INTEGER NOT NULL,
        min_income REAL NOT NULL,
        max_income REAL,
        tax_rate REAL NOT NULL,
        quick_deduction REAL NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS social_security_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        base_min REAL NOT NULL,
        base_max REAL NOT NULL,
        pension_ratio REAL DEFAULT 0.08,
        medical_ratio REAL DEFAULT 0.02,
        unemployment_ratio REAL DEFAULT 0.005,
        housing_fund_ratio REAL DEFAULT 0.12,
        UNIQUE(year, month)
    );
    """)
    
    print("  ✓ 表结构创建完成")
    
    # 3. 插入默认数据
    print("\n【3】插入默认配置...")
    
    # 工资项目分类
    categories = [
        ('应发项目', 'earning'),
        ('津贴补贴', 'allowance'),
        ('绩效奖金', 'bonus'),
        ('代扣项目', 'deduction'),
    ]
    
    for name, code in categories:
        db.execute("INSERT OR IGNORE INTO salary_item_categories (category_name, category_code) VALUES (?, ?)",
                  (name, code))
    
    # 标准工资项目
    items = [
        ('岗位工资', 'position_salary', 1, '固定项', '查表', None, 0, None, 1, 1, 1, '根据岗位等级'),
        ('薪级工资', 'grade_salary', 1, '固定项', '查表', None, 0, None, 1, 1, 2, '根据薪级'),
        ('绩效工资', 'performance_bonus', 3, '浮动项', '公式', 'base_salary * 0.4', 0, None, 1, 1, 10, '奖励性绩效'),
        ('住房补贴', 'housing_subsidy', 2, '固定项', '固定值', None, 800, None, 1, 1, 20, '住房补贴'),
        ('交通补贴', 'transport_allowance', 2, '固定项', '固定值', None, 500, None, 1, 1, 21, '交通通讯'),
        ('夜班津贴', 'night_shift_allowance', 2, '浮动项', '固定值', None, 50, None, 1, 1, 30, '夜班值班'),
        ('养老保险', 'pension_insurance', 4, '扣款项', '比例', None, 0, 0.08, 0, 1, 50, '个人部分8%'),
        ('医疗保险', 'medical_insurance', 4, '扣款项', '比例', None, 0, 0.02, 0, 1, 51, '个人部分2%'),
        ('失业保险', 'unemployment_insurance', 4, '扣款项', '比例', None, 0, 0.005, 0, 1, 52, '个人部分0.5%'),
        ('住房公积金', 'housing_fund', 4, '扣款项', '比例', None, 0, 0.12, 0, 1, 53, '个人部分12%'),
        ('个人所得税', 'income_tax', 4, '扣款项', '公式', 'calculate_tax', 0, None, 0, 1, 60, '累计预扣法'),
    ]
    
    for item in items:
        db.execute("""INSERT OR IGNORE INTO salary_items_config 
            (item_name, item_code, category_id, item_type, calculation_type, formula, base_value, ratio,
             is_taxable, is_visible, sort_order, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", item)
    
    # 个税税率表
    tax_rates = [
        (1, 0, 36000, 0.03, 0),
        (2, 36000, 144000, 0.10, 2520),
        (3, 144000, 300000, 0.20, 16920),
        (4, 300000, 420000, 0.25, 31920),
        (5, 420000, 660000, 0.30, 52920),
        (6, 660000, 960000, 0.35, 85920),
        (7, 960000, None, 0.45, 181920),
    ]
    
    for rate in tax_rates:
        db.execute("""INSERT OR IGNORE INTO tax_brackets 
            (level, min_income, max_income, tax_rate, quick_deduction)
            VALUES (?, ?, ?, ?, ?)""", rate)
    
    # 社保配置
    db.execute("""INSERT OR IGNORE INTO social_security_config 
        (year, month, base_min, base_max, pension_ratio, medical_ratio, unemployment_ratio, housing_fund_ratio)
        VALUES (2024, 1, 3000, 20000, 0.08, 0.02, 0.005, 0.12)""")
    
    print("  ✓ 配置数据插入完成")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 升级完成!")
    print("=" * 60)
    print("\n新增功能:")
    print("  1. 职工信息扩展字段(17个)")
    print("  2. 事业单位工资项目配置")
    print("  3. 个人所得税税率表(7级)")
    print("  4. 社保缴费比例配置")
    print("\n工资构成:")
    print("  应发 = 岗位工资 + 薪级工资 + 绩效工资 + 津贴补贴")
    print("  扣款 = 养老保险 + 医疗保险 + 失业保险 + 住房公积金 + 个税")
    print("  实发 = 应发 - 扣款")
    print("\n下一步:")
    print("  1. 配置各职工的岗位等级和薪级")
    print("  2. 设置自定义工资项目")
    print("  3. 使用自动计算生成工资")

if __name__ == '__main__':
    upgrade_database()
