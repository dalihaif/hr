#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
职工自助服务页面 - 部署测试脚本
功能:
1. 检查并安装前端依赖(echarts)
2. 验证后端API接口
3. 提供使用说明
"""

import subprocess
import sys
import sqlite3
import os

def install_echarts():
    """安装ECharts依赖"""
    print("=" * 60)
    print("步骤 1: 安装 ECharts 依赖")
    print("=" * 60)
    
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    try:
        # 检查是否已安装
        result = subprocess.run(
            ['npm', 'list', 'echarts'],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if 'echarts' in result.stdout:
            print("✅ ECharts 已安装")
            return True
        
        # 安装 echarts
        print("📦 正在安装 ECharts...")
        result = subprocess.run(
            ['npm', 'install', 'echarts'],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ ECharts 安装成功")
            return True
        else:
            print(f"❌ ECharts 安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程出错: {str(e)}")
        return False


def verify_database():
    """验证数据库表结构"""
    print("\n" + "=" * 60)
    print("步骤 2: 验证数据库表结构")
    print("=" * 60)
    
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'hospital_hr.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    required_tables = [
        'employees',
        'position_records',
        'title_records',
        'salary_items_config',
        'perf_assessments',
        'perf_templates',
        'attendance_records',
        'leave_requests',
        'trainings',
        'employee_training'
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ 表 {table} 存在")
            else:
                print(f"⚠️  表 {table} 缺失")
                missing_tables.append(table)
        
        conn.close()
        
        if missing_tables:
            print(f"\n⚠️  缺少 {len(missing_tables)} 个必需表")
            return False
        else:
            print("\n✅ 所有必需表都存在")
            return True
            
    except Exception as e:
        print(f"❌ 数据库验证失败: {str(e)}")
        return False


def check_backend_api():
    """检查后端API是否运行"""
    print("\n" + "=" * 60)
    print("步骤 3: 检查后端服务")
    print("=" * 60)
    
    import urllib.request
    import json
    
    try:
        url = "http://localhost:5000/api/current_user"
        req = urllib.request.Request(url)
        
        try:
            response = urllib.request.urlopen(req, timeout=5)
            print("✅ 后端服务正在运行 (端口 5000)")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("✅ 后端服务正在运行 (需要登录)")
                return True
            else:
                print(f"⚠️  后端服务响应异常: {e.code}")
                return False
        except urllib.error.URLError:
            print("❌ 后端服务未运行")
            print("\n💡 请先启动后端服务:")
            print("   python app.py")
            return False
            
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False


def check_frontend_dev():
    """检查前端开发服务器"""
    print("\n" + "=" * 60)
    print("步骤 4: 检查前端开发服务器")
    print("=" * 60)
    
    import urllib.request
    
    try:
        url = "http://localhost:5174"
        req = urllib.request.Request(url)
        
        try:
            response = urllib.request.urlopen(req, timeout=5)
            print("✅ 前端开发服务器正在运行 (端口 5174)")
            return True
        except urllib.error.URLError:
            print("❌ 前端开发服务器未运行")
            print("\n💡 请启动前端开发服务器:")
            print("   cd frontend")
            print("   npm run dev")
            return False
            
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False


def print_usage_guide():
    """打印使用指南"""
    print("\n" + "=" * 60)
    print("📖 职工自助服务 - 使用指南")
    print("=" * 60)
    
    guide = """
🎯 访问地址:
   http://localhost:5174/self-service

👤 适用角色:
   - 普通职工(查看个人信息、工资、绩效、考勤等)
   - 科室主任/护士长(额外可查看本科室数据)

📋 功能模块:
   1. 个人信息 - 查看基本资料、联系方式、社保银行信息
   2. 工资查询 - 查看月度工资明细、近6个月趋势图
   3. 绩效考核 - 查看历史考核记录、评分详情、绩效金额
   4. 考勤记录 - 查看打卡记录、月度统计、出勤率
   5. 请假申请 - 在线提交请假申请、查看审批进度
   6. 培训记录 - 查看参与培训、学时统计、证书状态

💡 操作提示:
   - 点击顶部快捷卡片可快速跳转到对应模块
   - 工资查询需选择月份后自动加载数据
   - 产假申请支持自动计算天数(顺产158天,剖腹产+15天,多胞胎+15天/胎)
   - 所有数据仅显示本人信息,严格权限控制

🔧 技术栈:
   - 前端: Vue 3 + Element Plus + ECharts
   - 后端: Flask + SQLite
   - 加密: AES加密敏感字段(手机号等)

📞 技术支持:
   - IT支持: ext. 8888
   - HR咨询: ext. 6666
   - 邮箱: hr-support@hospital.com
    """
    
    print(guide)


def main():
    """主函数"""
    print("\n" + "🏥" * 30)
    print("大理大学第一附属医院 - 职工自助服务部署检查")
    print("🏥" * 30 + "\n")
    
    results = []
    
    # 执行检查步骤
    results.append(("ECharts依赖", install_echarts()))
    results.append(("数据库表结构", verify_database()))
    results.append(("后端服务", check_backend_api()))
    results.append(("前端服务", check_frontend_dev()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 检查结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 所有检查通过!系统可以正常使用!")
        print_usage_guide()
    else:
        print("⚠️  部分检查未通过,请根据上述提示进行修复")
        print("\n💡 快速启动命令:")
        print("   # 终端1 - 启动后端")
        print("   python app.py")
        print("\n   # 终端2 - 启动前端")
        print("   cd frontend")
        print("   npm run dev")
    
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
