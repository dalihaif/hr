"""
测试新增功能
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_login():
    """测试登录"""
    print("测试登录...")
    res = requests.post(f'{BASE_URL}/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    print(f"状态码: {res.status_code}")
    print(f"响应: {res.json()}")
    return res.status_code == 200

def test_custom_fields():
    """测试自定义字段"""
    print("\n测试自定义字段...")
    
    # 创建自定义字段
    res = requests.post(f'{BASE_URL}/custom-fields', json={
        'field_name': '执业证书号',
        'field_code': 'license_no',
        'field_type': 'text',
        'department': '内科',
        'is_required': 1
    })
    print(f"创建字段状态码: {res.status_code}")
    
    # 查询自定义字段
    res = requests.get(f'{BASE_URL}/custom-fields')
    print(f"查询字段状态码: {res.status_code}")
    print(f"字段数量: {len(res.json())}")

def test_leave_request():
    """测试请假申请"""
    print("\n测试请假申请...")
    
    # 提交请假申请
    res = requests.post(f'{BASE_URL}/leave/request', json={
        'leave_type': '病假',
        'start_date': '2026-07-01',
        'end_date': '2026-07-03',
        'days': 3,
        'reason': '身体不适'
    })
    print(f"提交请假状态码: {res.status_code}")
    
    # 查询请假记录
    res = requests.get(f'{BASE_URL}/leave/list')
    print(f"查询请假状态码: {res.status_code}")
    print(f"请假记录数: {len(res.json())}")

def test_self_profile():
    """测试职工自助服务"""
    print("\n测试职工自助服务...")
    
    # 获取个人信息
    res = requests.get(f'{BASE_URL}/self/profile')
    print(f"获取个人信息状态码: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"姓名: {data.get('name')}")
        print(f"工号: {data.get('emp_no')}")

def test_export():
    """测试导出功能"""
    print("\n测试导出功能...")
    
    # 导出职工花名册
    res = requests.get(f'{BASE_URL}/employees/export')
    print(f"导出职工状态码: {res.status_code}")
    if res.status_code == 200:
        print(f"文件大小: {len(res.content)} bytes")

if __name__ == '__main__':
    print("=" * 50)
    print("医院人事系统 - 新功能测试")
    print("=" * 50)
    
    # 先登录
    if test_login():
        print("✓ 登录成功\n")
        
        # 测试各项功能
        test_custom_fields()
        test_leave_request()
        test_self_profile()
        test_export()
        
        print("\n" + "=" * 50)
        print("测试完成!")
        print("=" * 50)
    else:
        print("✗ 登录失败,请检查系统是否启动")
