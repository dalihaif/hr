"""
事业单位工资自动计算工具
支持岗位工资、薪级工资、绩效工资、津贴补贴等
自动计算社保和个人所得税
"""

import sqlite3
from datetime import datetime

class SalaryCalculator:
    """工资计算器"""
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def calculate_employee_salary(self, emp_id, year_month=None):
        """
        计算指定职工的工资
        
        Args:
            emp_id: 职工ID
            year_month: 年月字符串(如"2024-01"),默认为当前月
            
        Returns:
            dict: 包含各项工资明细和汇总
        """
        if not year_month:
            year_month = datetime.now().strftime('%Y-%m')
        
        conn = self._get_connection()
        db = conn.cursor()
        
        try:
            # 获取职工信息
            emp = db.execute("SELECT * FROM employees WHERE id = ?", (emp_id,)).fetchone()
            if not emp:
                return None
            
            result = {
                'emp_id': emp_id,
                'emp_no': emp['emp_no'],
                'name': emp['name'],
                'year_month': year_month,
                'items': [],
                'summary': {}
            }
            
            # 1. 计算应发项目
            earnings = self._calculate_earnings(db, emp)
            result['items'].extend(earnings)
            
            # 2. 计算扣款项目
            deductions = self._calculate_deductions(db, emp, earnings)
            result['items'].extend(deductions)
            
            # 3. 计算汇总
            total_earning = sum(item['amount'] for item in earnings)
            total_deduction = sum(item['amount'] for item in deductions)
            net_salary = total_earning - total_deduction
            
            result['summary'] = {
                'total_earning': round(total_earning, 2),
                'total_deduction': round(total_deduction, 2),
                'net_salary': round(net_salary, 2)
            }
            
            return result
            
        finally:
            conn.close()
    
    def _calculate_earnings(self, db, emp):
        """计算应发项目"""
        earnings = []
        
        # 岗位工资(根据岗位等级查表)
        position_salary = self._get_position_salary(db, emp['position_level'], emp['post_level'])
        if position_salary > 0:
            earnings.append({
                'item_name': '岗位工资',
                'item_code': 'position_salary',
                'amount': position_salary,
                'calculation_type': '查表'
            })
        
        # 薪级工资(根据薪级查表)
        grade_salary = self._get_grade_salary(db, emp['education_level'], emp['salary_grade'])
        if grade_salary > 0:
            earnings.append({
                'item_name': '薪级工资',
                'item_code': 'grade_salary',
                'amount': grade_salary,
                'calculation_type': '查表'
            })
        
        # 绩效工资(公式计算)
        base_salary = position_salary + grade_salary
        if base_salary > 0:
            performance = base_salary * 0.4  # 绩效系数0.4
            earnings.append({
                'item_name': '绩效工资',
                'item_code': 'performance_bonus',
                'amount': round(performance, 2),
                'calculation_type': '公式'
            })
        
        # 固定津贴补贴
        allowances = [
            ('住房补贴', 'housing_subsidy', 800),
            ('交通补贴', 'transport_allowance', 500),
        ]
        
        for name, code, amount in allowances:
            earnings.append({
                'item_name': name,
                'item_code': code,
                'amount': amount,
                'calculation_type': '固定值'
            })
        
        return earnings
    
    def _calculate_deductions(self, db, emp, earnings):
        """计算扣款项目"""
        deductions = []
        
        # 计算社保缴费基数(通常为岗位工资+薪级工资)
        base_salary = sum(e['amount'] for e in earnings if e['item_code'] in ['position_salary', 'grade_salary'])
        
        # 获取社保配置
        current_year = datetime.now().year
        current_month = datetime.now().month
        ss_config = db.execute("""
            SELECT * FROM social_security_config 
            WHERE year = ? AND month = ?
        """, (current_year, current_month)).fetchone()
        
        if ss_config:
            # 养老保险(个人8%)
            pension = base_salary * ss_config['pension_ratio']
            deductions.append({
                'item_name': '养老保险',
                'item_code': 'pension_insurance',
                'amount': round(pension, 2),
                'calculation_type': '比例'
            })
            
            # 医疗保险(个人2%)
            medical = base_salary * ss_config['medical_ratio']
            deductions.append({
                'item_name': '医疗保险',
                'item_code': 'medical_insurance',
                'amount': round(medical, 2),
                'calculation_type': '比例'
            })
            
            # 失业保险(个人0.5%)
            unemployment = base_salary * ss_config['unemployment_ratio']
            deductions.append({
                'item_name': '失业保险',
                'item_code': 'unemployment_insurance',
                'amount': round(unemployment, 2),
                'calculation_type': '比例'
            })
            
            # 住房公积金(个人12%)
            housing_fund = base_salary * ss_config['housing_fund_ratio']
            deductions.append({
                'item_name': '住房公积金',
                'item_code': 'housing_fund',
                'amount': round(housing_fund, 2),
                'calculation_type': '比例'
            })
        
        # 个人所得税
        taxable_income = sum(e['amount'] for e in earnings) - sum(d['amount'] for d in deductions)
        tax = self._calculate_income_tax(db, taxable_income)
        if tax > 0:
            deductions.append({
                'item_name': '个人所得税',
                'item_code': 'income_tax',
                'amount': round(tax, 2),
                'calculation_type': '累计预扣法'
            })
        
        return deductions
    
    def _get_position_salary(self, db, position_level, post_level):
        """查询岗位工资标准"""
        if not position_level or not post_level:
            return 0
        
        # 这里简化处理,实际应该从position_salary_standard表查询
        # 根据不同岗位等级返回不同工资
        salary_map = {
            ('管理', '一级'): 8000,
            ('管理', '二级'): 7000,
            ('管理', '三级'): 6000,
            ('专技', '正高'): 7500,
            ('专技', '副高'): 6500,
            ('专技', '中级'): 5500,
            ('专技', '初级'): 4500,
            ('工勤', '高级'): 5000,
            ('工勤', '中级'): 4000,
            ('工勤', '初级'): 3500,
        }
        
        return salary_map.get((position_level, post_level), 4000)
    
    def _get_grade_salary(self, db, education_level, salary_grade):
        """查询薪级工资标准"""
        if not salary_grade:
            return 0
        
        # 简化处理,实际应该从grade_salary_standard表查询
        # 薪级工资 = 基数 + 薪级 * 级差
        base = 1000
        step = 50
        
        return base + salary_grade * step
    
    def _calculate_income_tax(self, db, taxable_income):
        """计算个人所得税(累计预扣法)"""
        if taxable_income <= 0:
            return 0
        
        # 起征点5000元/月
        threshold = 5000
        taxable = taxable_income - threshold
        
        if taxable <= 0:
            return 0
        
        # 获取税率表
        brackets = db.execute("""
            SELECT * FROM tax_brackets 
            ORDER BY level ASC
        """).fetchall()
        
        # 查找适用税率
        for bracket in brackets:
            min_income = bracket['min_income']
            max_income = bracket['max_income']
            
            if max_income is None:  # 最高档
                if taxable >= min_income:
                    return round(taxable * bracket['tax_rate'] - bracket['quick_deduction'], 2)
            else:
                if min_income <= taxable < max_income:
                    return round(taxable * bracket['tax_rate'] - bracket['quick_deduction'], 2)
        
        return 0
    
    def get_custom_items(self, category='all'):
        """获取自定义工资项目配置"""
        conn = self._get_connection()
        db = conn.cursor()
        
        try:
            if category == 'all':
                items = db.execute("""
                    SELECT sic.*, sicc.category_name, sicc.category_code
                    FROM salary_items_config sic
                    LEFT JOIN salary_item_categories sicc ON sic.category_id = sicc.id
                    WHERE sic.is_visible = 1
                    ORDER BY sic.sort_order ASC
                """).fetchall()
            else:
                items = db.execute("""
                    SELECT sic.*, sicc.category_name, sicc.category_code
                    FROM salary_items_config sic
                    LEFT JOIN salary_item_categories sicc ON sic.category_id = sicc.id
                    WHERE sic.is_visible = 1 AND sicc.category_code = ?
                    ORDER BY sic.sort_order ASC
                """, (category,)).fetchall()
            
            return [dict(item) for item in items]
            
        finally:
            conn.close()
    
    def add_custom_item(self, item_data):
        """添加自定义工资项目"""
        conn = self._get_connection()
        db = conn.cursor()
        
        try:
            db.execute("""
                INSERT INTO salary_items_config 
                (item_name, item_code, category_id, item_type, calculation_type, 
                 formula, base_value, ratio, is_taxable, is_visible, sort_order, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_data['item_name'],
                item_data['item_code'],
                item_data.get('category_id'),
                item_data.get('item_type', '固定项'),
                item_data.get('calculation_type', '固定值'),
                item_data.get('formula'),
                item_data.get('base_value', 0),
                item_data.get('ratio'),
                item_data.get('is_taxable', 1),
                item_data.get('is_visible', 1),
                item_data.get('sort_order', 0),
                item_data.get('description')
            ))
            
            conn.commit()
            return {'success': True, 'id': db.lastrowid}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
            
        finally:
            conn.close()
    
    def update_custom_item(self, item_id, item_data):
        """更新自定义工资项目"""
        conn = self._get_connection()
        db = conn.cursor()
        
        try:
            db.execute("""
                UPDATE salary_items_config SET
                    item_name = ?,
                    item_code = ?,
                    category_id = ?,
                    item_type = ?,
                    calculation_type = ?,
                    formula = ?,
                    base_value = ?,
                    ratio = ?,
                    is_taxable = ?,
                    is_visible = ?,
                    sort_order = ?,
                    description = ?
                WHERE id = ?
            """, (
                item_data['item_name'],
                item_data['item_code'],
                item_data.get('category_id'),
                item_data.get('item_type'),
                item_data.get('calculation_type'),
                item_data.get('formula'),
                item_data.get('base_value'),
                item_data.get('ratio'),
                item_data.get('is_taxable'),
                item_data.get('is_visible'),
                item_data.get('sort_order'),
                item_data.get('description'),
                item_id
            ))
            
            conn.commit()
            return {'success': True}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
            
        finally:
            conn.close()
    
    def delete_custom_item(self, item_id):
        """删除自定义工资项目(软删除)"""
        conn = self._get_connection()
        db = conn.cursor()
        
        try:
            db.execute("""
                UPDATE salary_items_config SET is_visible = 0 WHERE id = ?
            """, (item_id,))
            
            conn.commit()
            return {'success': True}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
            
        finally:
            conn.close()


# 使用示例
if __name__ == '__main__':
    from config import Config
    
    calculator = SalaryCalculator(Config.DB_PATH)
    
    # 计算某职工工资
    result = calculator.calculate_employee_salary(1)
    if result:
        print(f"职工: {result['name']} ({result['emp_no']})")
        print(f"月份: {result['year_month']}")
        print("\n工资明细:")
        for item in result['items']:
            print(f"  {item['item_name']}: {item['amount']:.2f} ({item['calculation_type']})")
        print(f"\n应发合计: {result['summary']['total_earning']:.2f}")
        print(f"扣款合计: {result['summary']['total_deduction']:.2f}")
        print(f"实发工资: {result['summary']['net_salary']:.2f}")
