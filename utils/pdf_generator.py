"""
PDF工资条生成工具
使用ReportLab生成PDF格式的工资条
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import io
import zipfile
import datetime

def generate_salary_slip(employee_data, salary_data, month):
    """
    生成单个职工工资条PDF
    
    Args:
        employee_data: 职工信息字典
        salary_data: 工资数据字典
        month: 工资月份 (格式: YYYY-MM)
    
    Returns:
        BytesIO对象，包含PDF数据
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # 设置中文字体（使用默认字体）
    c.setFont("Helvetica", 12)
    
    # ========== 标题 ==========
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 2 * cm, "大理大学第一附属医院")
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 3 * cm, f"{month} 工资条")
    
    # ========== 职工基本信息 ==========
    y_pos = height - 5 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y_pos, "职工信息:")
    
    c.setFont("Helvetica", 10)
    y_pos -= 0.8 * cm
    info_lines = [
        f"工号: {employee_data.get('emp_no', '')}",
        f"姓名: {employee_data.get('name', '')}",
        f"科室: {employee_data.get('department', '')}",
        f"岗位: {employee_data.get('position', '')}",
        f"职称: {employee_data.get('title_level', '')}",
    ]
    
    for line in info_lines:
        c.drawString(2 * cm, y_pos, line)
        y_pos -= 0.6 * cm
    
    # ========== 工资明细表格 ==========
    y_pos -= 1 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y_pos, "工资明细:")
    
    y_pos -= 1 * cm
    
    # 准备表格数据
    table_data = [["项目", "金额(元)"]]
    
    # 收入项目
    income_items = [
        ('基本工资', salary_data.get('base_salary', 0)),
        ('岗位津贴', salary_data.get('position_allowance', 0)),
        ('医疗补贴', salary_data.get('medical_allowance', 0)),
        ('住房补贴', salary_data.get('housing_allowance', 0)),
        ('夜班补贴', salary_data.get('night_shift_allowance', 0)),
        ('加班费', salary_data.get('overtime_pay', 0)),
        ('绩效奖金', salary_data.get('performance_bonus', 0)),
    ]
    
    for name, amount in income_items:
        if amount > 0:
            table_data.append([name, f"{amount:.2f}"])
    
    table_data.append(["收入合计", f"{salary_data.get('gross_salary', 0):.2f}"])
    table_data.append(["", ""])  # 空行
    
    # 扣款项目
    deduction_items = [
        ('养老保险', salary_data.get('pension_insurance', 0)),
        ('医疗保险', salary_data.get('medical_insurance', 0)),
        ('失业保险', salary_data.get('unemployment_insurance', 0)),
        ('住房公积金', salary_data.get('housing_fund', 0)),
        ('个人所得税', salary_data.get('income_tax', 0)),
    ]
    
    for name, amount in deduction_items:
        if amount > 0:
            table_data.append([name, f"-{amount:.2f}"])
    
    table_data.append(["扣款合计", f"-{salary_data.get('total_deduction', 0):.2f}"])
    table_data.append(["", ""])  # 空行
    
    # 实发工资
    table_data.append(["实发工资", f"{salary_data.get('net_salary', 0):.2f}"])
    
    # 创建表格
    table = Table(table_data, colWidths=[8*cm, 4*cm])
    
    # 设置表格样式
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ])
    
    table.setStyle(style)
    
    # 绘制表格
    table.wrapOn(c, width, height)
    table.drawOn(c, 2 * cm, y_pos - len(table_data) * 0.5 * cm)
    
    # ========== 签名栏 ==========
    y_pos = 3 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y_pos, f"制表日期: {datetime.datetime.now().strftime('%Y年%m月%d日')}")
    c.drawString(10 * cm, y_pos, "财务部门签章: ________________")
    
    y_pos -= 1.5 * cm
    c.drawString(2 * cm, y_pos, "职工签字: ________________")
    c.drawString(10 * cm, y_pos, "备注: ________________________")
    
    # ========== 页脚 ==========
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 1.5 * cm, "本工资条仅供参考，具体以银行到账为准")
    
    # 保存PDF
    c.save()
    buffer.seek(0)
    return buffer


def generate_batch_salary_slips(salary_records_list):
    """
    批量生成工资条并打包为ZIP
    
    Args:
        salary_records_list: 工资记录列表，每个记录包含employee_data、salary_data、month
    
    Returns:
        BytesIO对象，包含ZIP文件数据
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for record in salary_records_list:
            emp_no = record['employee_data'].get('emp_no', 'unknown')
            month = record.get('month', 'unknown')
            
            # 生成单个工资条PDF
            pdf_buffer = generate_salary_slip(
                record['employee_data'],
                record['salary_data'],
                month
            )
            
            # 添加到ZIP
            filename = f"{emp_no}_{month}_工资条.pdf"
            zip_file.writestr(filename, pdf_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer


def test_pdf_generation():
    """测试PDF生成功能"""
    # 测试数据
    employee_data = {
        'emp_no': '001',
        'name': '张三',
        'department': '内科',
        'position': '主治医师',
        'title_level': '中级',
    }
    
    salary_data = {
        'base_salary': 5000,
        'position_allowance': 1500,
        'medical_allowance': 500,
        'housing_allowance': 800,
        'night_shift_allowance': 300,
        'overtime_pay': 600,
        'performance_bonus': 2000,
        'gross_salary': 10700,
        
        'pension_insurance': 400,
        'medical_insurance': 100,
        'unemployment_insurance': 50,
        'housing_fund': 600,
        'income_tax': 320,
        'total_deduction': 1470,
        
        'net_salary': 9230,
    }
    
    # 生成PDF
    pdf_buffer = generate_salary_slip(employee_data, salary_data, '2026-06')
    
    # 保存到文件
    with open('test_salary_slip.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("✓ PDF工资条生成成功: test_salary_slip.pdf")
    return True


if __name__ == '__main__':
    test_pdf_generation()
