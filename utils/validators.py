"""
数据验证工具
"""
import re


def validate_email(email):
    """验证邮箱格式"""
    if not email:
        return True  # 邮箱可选
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """验证手机号格式"""
    if not phone:
        return True  # 电话可选
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def validate_id_card(id_card):
    """验证身份证号格式(简化版)"""
    if not id_card:
        return True  # 可选
    pattern = r'^\d{17}[\dXx]$'
    return re.match(pattern, id_card) is not None


def validate_password(password):
    """
    验证密码强度
    至少8位，包含大小写字母和数字
    """
    if len(password) < 8:
        return False, '密码长度至少8位'
    
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    if not (has_upper and has_lower and has_digit):
        return False, '密码必须包含大小写字母和数字'
    
    return True, '密码符合要求'


def sanitize_string(text):
    """
    清理字符串，防止XSS攻击
    移除潜在的危险字符
    """
    if not text:
        return text
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 转义特殊字符
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text


def validate_date(date_str):
    """验证日期格式 YYYY-MM-DD"""
    if not date_str:
        return True
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    try:
        year, month, day = map(int, date_str.split('-'))
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        return True
    except:
        return False


def validate_positive_number(value):
    """验证正数"""
    try:
        num = float(value)
        return num >= 0
    except:
        return False
