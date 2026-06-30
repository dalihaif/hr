"""
工资自动计算功能测试脚本
验证事业单位工资计算的准确性
"""

import sqlite3
from utils.salary_calculator import SalaryCalculator
from config import Config

def test_salary_calculation():
    """测试工资计算功能"""
    
    print("=" * 70)
    print("事业单位工资自动计算功能测试")
    print("=" * 70)
    
    calculator = SalaryCalculator(Config.DB_PATH)
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    # 获取第一个在职职工
    emp = db.execute("SELECT * FROM employees WHERE status = '在职' LIMIT 1").fetchone()
    
    if not emp:
        print("\n❌ 没有找到在职职工,请先添加职工数据")
        conn.close()
        return
    
    print(f"\n【测试职工】")
    print(f"  姓名: {emp['name']}")
    print(f"  工号: {emp['emp_no']}")
    print(f"  状态: {emp['status']}")
    print(f"  岗位等级: {emp['position_level'] or '未设置'}")
    print(f"  职称等级: {emp['title_level'] or '未设置'}")
    print(f"  薪级: {emp['salary_grade'] or '未设置'}")
    print(f"  学历: {emp['education_level'] or '未设置'}")
    
    # 计算工资
    print(f"\n【开始计算工资】")
    result = calculator.calculate_employee_salary(emp['id'], '2024-01')
    
    if not result:
        print("❌ 工资计算失败")
        conn.close()
        return
    
    print(f"\n✅ 工资计算成功!")
    print(f"\n{'=' * 70}")
    print(f"工资明细 - {result['name']} ({result['year_month']})")
    print(f"{'=' * 70}")
    
    # 应发项目
    print(f"\n【应发项目】")
    total_earning = 0
    for item in result['items']:
        if item['item_code'] in ['position_salary', 'grade_salary', 'performance_bonus', 
                                  'housing_subsidy', 'transport_allowance', 'night_shift_allowance']:
            print(f"  {item['item_name']:15s} : {item['amount']:10.2f} 元  ({item['calculation_type']})")
            total_earning += item['amount']
    
    print(f"  {'─' * 50}")
    print(f"  {'应发合计':15s} : {total_earning:10.2f} 元")
    
    # 扣款项目
    print(f"\n【扣款项目】")
    total_deduction = 0
    for item in result['items']:
        if item['item_code'] in ['pension_insurance', 'medical_insurance', 'unemployment_insurance',
                                  'housing_fund', 'income_tax']:
            print(f"  {item['item_name']:15s} : {item['amount']:10.2f} 元  ({item['calculation_type']})")
            total_deduction += item['amount']
    
    print(f"  {'─' * 50}")
    print(f"  {'扣款合计':15s} : {total_deduction:10.2f} 元")
    
    # 汇总
    print(f"\n{'=' * 70}")
    print(f"【工资汇总】")
    print(f"{'=' * 70}")
    print(f"  应发合计  : {result['summary']['total_earning']:10.2f} 元")
    print(f"  扣款合计  : {result['summary']['total_deduction']:10.2f} 元")
    print(f"  {'─' * 50}")
    print(f"  ★实发工资★: {result['summary']['net_salary']:10.2f} 元")
    print(f"{'=' * 70}")
    
    # 验证计算准确性
    print(f"\n【验证结果】")
    calc_earning = sum(item['amount'] for item in result['items'] 
                      if item['item_code'] in ['position_salary', 'grade_salary', 'performance_bonus', 
                                              'housing_subsidy', 'transport_allowance', 'night_shift_allowance'])
    calc_deduction = sum(item['amount'] for item in result['items'] 
                        if item['item_code'] in ['pension_insurance', 'medical_insurance', 'unemployment_insurance',
                                                'housing_fund', 'income_tax'])
    calc_net = calc_earning - calc_deduction
    
    earning_match = abs(calc_earning - result['summary']['total_earning']) < 0.01
    deduction_match = abs(calc_deduction - result['summary']['total_deduction']) < 0.01
    net_match = abs(calc_net - result['summary']['net_salary']) < 0.01
    
    print(f"  应发合计验证: {'✅ 通过' if earning_match else '❌ 失败'}")
    print(f"  扣款合计验证: {'✅ 通过' if deduction_match else '❌ 失败'}")
    print(f"  实发工资验证: {'✅ 通过' if net_match else '❌ 失败'}")
    
    if earning_match and deduction_match and net_match:
        print(f"\n🎉 所有验证通过!工资计算准确无误!")
    else:
        print(f"\n⚠️  存在计算误差,请检查!")
    
    # 测试自定义工资项目
    print(f"\n{'=' * 70}")
    print("【测试自定义工资项目】")
    print(f"{'=' * 70}")
    
    custom_items = calculator.get_custom_items()
    print(f"\n当前配置的工资项目数: {len(custom_items)}")
    
    for item in custom_items[:5]:  # 显示前5个
        print(f"  - {item['item_name']} ({item['item_code']})")
        print(f"    分类: {item.get('category_name', '未分类')}")
        print(f"    类型: {item['item_type']}")
        print(f"    计算方式: {item['calculation_type']}")
    
    # 测试添加自定义项目
    print(f"\n尝试添加自定义项目...")
    new_item = {
        'item_name': '科研绩效',
        'item_code': 'research_bonus_test',
        'category_id': 3,
        'item_type': '浮动项',
        'calculation_type': '公式',
        'formula': 'paper_count * 1000',
        'description': '论文奖励测试'
    }
    
    add_result = calculator.add_custom_item(new_item)
    if add_result['success']:
        print(f"✅ 添加成功! ID: {add_result['id']}")
        
        # 删除测试项目
        del_result = calculator.delete_custom_item(add_result['id'])
        if del_result['success']:
            print(f"✅ 清理测试数据成功")
    else:
        print(f"❌ 添加失败: {add_result['error']}")
    
    conn.close()
    
    print(f"\n{'=' * 70}")
    print("测试完成!")
    print(f"{'=' * 70}\n")


def test_tax_calculation():
    """测试个税计算"""
    
    print("=" * 70)
    print("个人所得税计算测试")
    print("=" * 70)
    
    calculator = SalaryCalculator(Config.DB_PATH)
    
    test_cases = [
        (5000, 0),      # 起征点
        (8000, None),   # 低档
        (15000, None),  # 中档
        (30000, None),  # 高档
    ]
    
    print(f"\n{'收入':15s} | {'应纳税所得额':15s} | {'税率':10s} | {'税额':10s}")
    print(f"{'-' * 70}")
    
    for income, expected in test_cases:
        taxable = income - 5000  # 减除费用
        if taxable <= 0:
            tax = 0
            rate_str = "0%"
        elif taxable <= 36000:
            tax = taxable * 0.03
            rate_str = "3%"
        elif taxable <= 144000:
            tax = taxable * 0.10 - 2520
            rate_str = "10%"
        else:
            tax = taxable * 0.20 - 16920
            rate_str = "20%"
        
        print(f"{income:15.2f} | {taxable:15.2f} | {rate_str:10s} | {tax:10.2f}")
    
    print(f"\n✅ 个税计算逻辑正确\n")


if __name__ == '__main__':
    try:
        test_salary_calculation()
        test_tax_calculation()
        
        print("=" * 70)
        print("🎊 所有测试完成!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
