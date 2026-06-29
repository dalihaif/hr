"""
医院人事系统新功能测试脚本
测试PDF生成、备份管理、招聘/培训/离职模块
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def login(session):
    """登录获取session"""
    print("\n=== 1. 登录系统 ===")
    response = session.post(f'{BASE_URL}/api/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    if response.status_code == 200:
        print("✓ 登录成功")
        return True
    else:
        print(f"✗ 登录失败: {response.text}")
        return False

def test_pdf_generation(session):
    """测试PDF工资条生成"""
    print("\n=== 2. 测试PDF工资条生成 ===")
    
    # 先查询是否有工资记录
    response = session.get(f'{BASE_URL}/api/salary/records?month=2026-06')
    if response.status_code != 200 or not response.json():
        print("⚠ 没有2026-06的工资记录,跳过PDF测试")
        return
    
    # 生成单个工资条
    print("  生成单个工资条...")
    response = session.post(f'{BASE_URL}/api/salary/slips/generate', json={
        'month': '2026-06'
    })
    
    if response.status_code == 200:
        filename = f'test_single_slip_2026-06.pdf'
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✓ 单个工资条生成成功: {filename}")
    else:
        print(f"✗ 生成失败: {response.text}")

def test_backup_management(session):
    """测试数据备份管理"""
    print("\n=== 3. 测试数据备份管理 ===")
    
    # 创建备份
    print("  创建备份...")
    response = session.post(f'{BASE_URL}/api/backup/create', json={'type': 'full'})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 备份创建成功: {data['backup_file']} ({data['size']} bytes)")
        backup_file = data['backup_file']
    else:
        print(f"✗ 备份失败: {response.text}")
        return
    
    # 获取备份列表
    print("  获取备份列表...")
    response = session.get(f'{BASE_URL}/api/backup/list')
    if response.status_code == 200:
        backups = response.json()
        print(f"✓ 共有 {len(backups)} 个备份文件")
        for b in backups[:3]:  # 显示最近3个
            print(f"    - {b['filename']} ({b['size_mb']} MB)")
    else:
        print(f"✗ 获取列表失败: {response.text}")
    
    # 清理过期备份(保留7天)
    print("  清理过期备份...")
    response = session.post(f'{BASE_URL}/api/backup/cleanup', json={'keep_days': 7})
    if response.status_code == 200:
        print(f"✓ 清理完成,删除 {response.json()['deleted_count']} 个过期备份")
    else:
        print(f"✗ 清理失败: {response.text}")

def test_recruitment(session):
    """测试招聘管理"""
    print("\n=== 4. 测试招聘管理 ===")
    
    # 创建招聘岗位
    print("  创建招聘岗位...")
    response = session.post(f'{BASE_URL}/api/recruitment/positions', json={
        'position_name': '内科医师',
        'department': '内科',
        'headcount': 2,
        'requirements': '本科及以上学历,有执业医师证',
        'status': '招聘中',
        'publish_date': '2026-06-01',
        'deadline': '2026-07-31'
    })
    if response.status_code == 200:
        print("✓ 岗位创建成功")
    else:
        print(f"✗ 创建失败: {response.text}")
        return
    
    # 获取岗位列表
    print("  获取岗位列表...")
    response = session.get(f'{BASE_URL}/api/recruitment/positions')
    if response.status_code == 200:
        positions = response.json()
        print(f"✓ 共有 {len(positions)} 个招聘岗位")
        if positions:
            pos_id = positions[0]['id']
            print(f"    示例: {positions[0]['position_name']} (ID:{pos_id})")
    else:
        print(f"✗ 获取失败: {response.text}")
        return
    
    # 录入应聘者
    print("  录入应聘者信息...")
    response = session.post(f'{BASE_URL}/api/recruitment/applicants', json={
        'position_id': pos_id,
        'name': '李明',
        'gender': '男',
        'birth_date': '1995-05-20',
        'phone': '13800138000',
        'email': 'liming@example.com',
        'education': '本科',
        'major': '临床医学',
        'experience_years': 3
    })
    if response.status_code == 200:
        print("✓ 应聘者录入成功")
    else:
        print(f"✗ 录入失败: {response.text}")
        return
    
    # 创建面试记录
    print("  创建面试记录...")
    # 先获取应聘者ID
    response = session.get(f'{BASE_URL}/api/recruitment/applicants?position_id={pos_id}')
    applicants = response.json()
    if applicants:
        app_id = applicants[0]['id']
        response = session.post(f'{BASE_URL}/api/recruitment/interviews', json={
            'applicant_id': app_id,
            'interview_type': '初试',
            'interview_date': '2026-07-01 14:00:00',
            'score': 85.5,
            'comments': '表现良好,专业扎实',
            'result': '通过'
        })
        if response.status_code == 200:
            print("✓ 面试记录创建成功")
        else:
            print(f"✗ 创建失败: {response.text}")
    
    # 获取招聘统计
    print("  获取招聘统计...")
    response = session.get(f'{BASE_URL}/api/recruitment/statistics')
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ 招聘统计:")
        print(f"    岗位状态: {stats['positions']}")
        print(f"    应聘者状态: {stats['applicants']}")
    else:
        print(f"✗ 获取统计失败: {response.text}")

def test_training(session):
    """测试培训管理"""
    print("\n=== 5. 测试培训管理 ===")
    
    # 创建培训计划
    print("  创建培训计划...")
    response = session.post(f'{BASE_URL}/api/training/plans', json={
        'title': '心肺复苏技能培训',
        'training_type': '内部培训',
        'trainer': '王医生',
        'start_date': '2026-07-10',
        'end_date': '2026-07-10',
        'location': '会议室A',
        'max_participants': 30,
        'description': '基础生命支持技能培训'
    })
    if response.status_code == 200:
        print("✓ 培训计划创建成功")
    else:
        print(f"✗ 创建失败: {response.text}")
        return
    
    # 获取培训计划列表
    print("  获取培训计划列表...")
    response = session.get(f'{BASE_URL}/api/training/plans')
    if response.status_code == 200:
        plans = response.json()
        print(f"✓ 共有 {len(plans)} 个培训计划")
        if plans:
            plan_id = plans[0]['id']
            print(f"    示例: {plans[0]['title']} (ID:{plan_id})")
    else:
        print(f"✗ 获取失败: {response.text}")
        return
    
    # 录入培训记录
    print("  录入培训记录...")
    # 先获取一个职工ID
    response = session.get(f'{BASE_URL}/api/employees?limit=1')
    employees = response.json()
    if employees:
        emp_id = employees[0]['id']
        response = session.post(f'{BASE_URL}/api/training/records', json={
            'emp_id': emp_id,
            'training_name': '心肺复苏技能培训',
            'training_type': '内部培训',
            'training_date': '2026-07-10',
            'hours': 4,
            'score': 90,
            'certificate_no': 'CERT20260710001',
            'description': '考核优秀'
        })
        if response.status_code == 200:
            print("✓ 培训记录录入成功")
        else:
            print(f"✗ 录入失败: {response.text}")
    
    # 获取培训统计
    print("  获取培训统计...")
    response = session.get(f'{BASE_URL}/api/training/statistics')
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ 培训统计:")
        print(f"    计划状态: {stats['plans']}")
        print(f"    人均培训时长: {stats['avg_training_hours']} 小时")
    else:
        print(f"✗ 获取统计失败: {response.text}")

def test_resignation(session):
    """测试离职管理"""
    print("\n=== 6. 测试离职管理 ===")
    
    # 获取一个职工ID用于测试
    response = session.get(f'{BASE_URL}/api/employees?limit=1')
    employees = response.json()
    if not employees:
        print("⚠ 没有职工数据,跳过离职测试")
        return
    
    emp_id = employees[0]['id']
    
    # 提交离职申请
    print("  提交离职申请...")
    response = session.post(f'{BASE_URL}/api/resignation/requests', json={
        'emp_id': emp_id,
        'resignation_type': '主动辞职',
        'reason': '个人发展原因',
        'apply_date': '2026-07-01',
        'expected_last_day': '2026-07-31'
    })
    if response.status_code == 200:
        print("✓ 离职申请提交成功")
    else:
        print(f"✗ 提交失败: {response.text}")
        return
    
    # 获取离职申请列表
    print("  获取离职申请列表...")
    response = session.get(f'{BASE_URL}/api/resignation/requests')
    if response.status_code == 200:
        requests_list = response.json()
        print(f"✓ 共有 {len(requests_list)} 个离职申请")
        if requests_list:
            req_id = requests_list[0]['id']
            print(f"    示例: 职工{requests_list[0]['emp_name']} (申请ID:{req_id})")
    else:
        print(f"✗ 获取失败: {response.text}")
        return
    
    # 审批离职申请
    print("  审批离职申请...")
    response = session.post(f'{BASE_URL}/api/resignation/approve', json={
        'request_id': req_id,
        'approved': True
    })
    if response.status_code == 200:
        print("✓ 离职申请已批准")
    else:
        print(f"✗ 审批失败: {response.text}")
    
    # 创建交接清单
    print("  创建交接清单...")
    response = session.post(f'{BASE_URL}/api/resignation/handover', json={
        'resignation_id': req_id,
        'item_name': '工作文档移交',
        'item_type': '工作文档',
        'remarks': '包括病历档案、患者资料等'
    })
    if response.status_code == 200:
        print("✓ 交接项创建成功")
        
        # 获取交接项ID并完成
        response = session.get(f'{BASE_URL}/api/resignation/handover?resignation_id={req_id}')
        handovers = response.json()
        if handovers:
            item_id = handovers[0]['id']
            response = session.put(f'{BASE_URL}/api/resignation/handover/{item_id}')
            if response.status_code == 200:
                print("✓ 交接项已完成")
    else:
        print(f"✗ 创建失败: {response.text}")
    
    # 创建离职档案
    print("  创建离职档案...")
    response = session.post(f'{BASE_URL}/api/resignation/records', json={
        'emp_id': emp_id,
        'resignation_type': '主动辞职',
        'last_working_day': '2026-07-31',
        'final_salary': 8500.00,
        'handover_completed': 1,
        'exit_interview_notes': '员工表示对工作环境满意,因家庭原因离职'
    })
    if response.status_code == 200:
        print("✓ 离职档案创建成功")
    else:
        print(f"✗ 创建失败: {response.text}")
    
    # 获取离职统计
    print("  获取离职统计...")
    response = session.get(f'{BASE_URL}/api/resignation/statistics')
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ 离职统计:")
        print(f"    离职类型: {stats['types']}")
        print(f"    离职率: {stats['turnover_rate']}%")
        print(f"    离职人数: {stats['resigned_count']}, 在职人数: {stats['total_employees']}")
    else:
        print(f"✗ 获取统计失败: {response.text}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("医院人事系统新功能测试")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. 登录
    if not login(session):
        print("\n✗ 登录失败,终止测试")
        return
    
    # 2. 测试PDF生成
    try:
        test_pdf_generation(session)
    except Exception as e:
        print(f"✗ PDF测试异常: {e}")
    
    # 3. 测试备份管理
    try:
        test_backup_management(session)
    except Exception as e:
        print(f"✗ 备份测试异常: {e}")
    
    # 4. 测试招聘管理
    try:
        test_recruitment(session)
    except Exception as e:
        print(f"✗ 招聘测试异常: {e}")
    
    # 5. 测试培训管理
    try:
        test_training(session)
    except Exception as e:
        print(f"✗ 培训测试异常: {e}")
    
    # 6. 测试离职管理
    try:
        test_resignation(session)
    except Exception as e:
        print(f"✗ 离职测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
