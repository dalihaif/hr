#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试自定义字段、工资项目、绩效管理项目API
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def login():
    """登录获取session"""
    res = requests.post(f'{BASE_URL}/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    if res.status_code == 200:
        print('✓ 登录成功')
        return res.cookies
    else:
        print('✗ 登录失败')
        return None

def test_custom_fields(cookies):
    """测试自定义字段管理"""
    print('\n=== 测试自定义字段管理 ===')
    
    # 创建自定义字段
    data = {
        'field_name': '专业特长',
        'field_code': 'specialty',
        'field_type': 'text',
        'department': None,
        'is_required': 0,
        'sort_order': 1,
        'is_active': 1
    }
    res = requests.post(f'{BASE_URL}/custom-fields', json=data, cookies=cookies)
    print(f'创建自定义字段: {res.status_code} - {res.json()}')
    
    # 获取自定义字段列表
    res = requests.get(f'{BASE_URL}/custom-fields', cookies=cookies)
    if res.status_code == 200:
        fields = res.json()
        print(f'✓ 获取到 {len(fields)} 个自定义字段')
        for f in fields:
            print(f'  - {f["field_name"]} ({f["field_code"]})')
    else:
        print(f'✗ 获取失败: {res.status_code}')

def test_salary_items(cookies):
    """测试工资项目管理"""
    print('\n=== 测试工资项目管理 ===')
    
    # 创建工资项目
    data = {
        'item_name': '基本工资',
        'item_code': 'base_salary',
        'item_type': '固定项',
        'calculation_method': '固定值',
        'formula': None,
        'is_taxable': 1,
        'is_visible': 1,
        'sort_order': 1,
        'is_active': 1,
        'description': '职工基本工资金额'
    }
    res = requests.post(f'{BASE_URL}/salary-items', json=data, cookies=cookies)
    print(f'创建工资项目: {res.status_code} - {res.json()}')
    
    # 获取工资项目列表
    res = requests.get(f'{BASE_URL}/salary-items', cookies=cookies)
    if res.status_code == 200:
        items = res.json()
        print(f'✓ 获取到 {len(items)} 个工资项目')
        for item in items:
            print(f'  - {item["item_name"]} ({item["item_code"]}) - {item["item_type"]}')
    else:
        print(f'✗ 获取失败: {res.status_code}')

def test_perf_categories(cookies):
    """测试绩效管理分类"""
    print('\n=== 测试绩效管理分类 ===')
    
    # 创建绩效分类
    data = {
        'category_name': '工作业绩',
        'category_code': 'work_performance',
        'weight': 40,
        'description': '工作完成情况和质量评估',
        'sort_order': 1,
        'is_active': 1
    }
    res = requests.post(f'{BASE_URL}/perf-categories', json=data, cookies=cookies)
    print(f'创建绩效分类: {res.status_code} - {res.json()}')
    
    # 获取绩效分类列表
    res = requests.get(f'{BASE_URL}/perf-categories', cookies=cookies)
    if res.status_code == 200:
        categories = res.json()
        print(f'✓ 获取到 {len(categories)} 个绩效分类')
        for cat in categories:
            print(f'  - {cat["category_name"]} ({cat["category_code"]}) - 权重:{cat["weight"]}%')
            
            # 为每个分类添加指标
            if cat['category_code'] == 'work_performance':
                indicator_data = {
                    'indicator_name': '门诊量',
                    'indicator_code': 'outpatient_count',
                    'category_id': cat['id'],
                    'scoring_method': '百分制',
                    'max_score': 100,
                    'weight': 30,
                    'description': '月度门诊接诊患者数量',
                    'sort_order': 1,
                    'is_active': 1
                }
                res2 = requests.post(f'{BASE_URL}/perf-indicators', json=indicator_data, cookies=cookies)
                print(f'    创建指标: {res2.status_code} - {res2.json()}')
    else:
        print(f'✗ 获取失败: {res.status_code}')

def main():
    print('=' * 60)
    print('医院人事系统 - 新功能测试')
    print('=' * 60)
    
    # 登录
    cookies = login()
    if not cookies:
        return
    
    # 测试各项功能
    test_custom_fields(cookies)
    test_salary_items(cookies)
    test_perf_categories(cookies)
    
    print('\n' + '=' * 60)
    print('测试完成!')
    print('=' * 60)

if __name__ == '__main__':
    main()
