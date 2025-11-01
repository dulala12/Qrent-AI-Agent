#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化邀请码系统
- 运行数据库迁移
- 生成测试邀请码
"""

import os
import sys
import django
from django.utils import timezone
import datetime
import random
import string

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from limits.models import Invitation

def run_migrations():
    """运行数据库迁移"""
    print("正在运行数据库迁移...")
    os.system('python manage.py makemigrations')
    os.system('python manage.py migrate')
    print("数据库迁移完成!")

def generate_test_invitations(count=5):
    """生成测试邀请码"""
    print(f"正在生成 {count} 个测试邀请码...")
    
    test_codes = []
    
    for i in range(count):
        # 生成测试邀请码（以QRTEST开头）
        chars = string.ascii_uppercase + string.digits
        random_str = ''.join(random.choices(chars, k=8))
        code = f"QRTEST-{random_str}"
        
        # 确保唯一
        while Invitation.objects.filter(code=code).exists():
            random_str = ''.join(random.choices(chars, k=8))
            code = f"QRTEST-{random_str}"
        
        # 创建测试邀请码，有效期较长，可使用多次
        expires_at = timezone.now() + datetime.timedelta(days=90)
        invitation = Invitation.objects.create(
            code=code,
            expires_at=expires_at,
            max_uses=100,
            used_count=0
        )
        
        test_codes.append(code)
        print(f"生成测试邀请码: {code}")
    
    return test_codes

def check_existing_invitations():
    """检查已存在的邀请码"""
    invitations = Invitation.objects.all()
    
    if invitations.exists():
        print("\n已存在的邀请码:")
        print(f"{'邀请码':<25} {'状态':<10} {'剩余次数':<10} {'过期时间':<25}")
        print("-" * 70)
        
        for inv in invitations:
            status = "有效" if inv.is_valid() else inv.get_status()
            expires_str = inv.expires_at.strftime('%Y-%m-%d %H:%M')
            remaining = inv.get_remaining_uses()
            
            print(f"{inv.code:<25} {status:<10} {remaining:<10} {expires_str:<25}")
        
        # 特别标注测试邀请码
        test_invitations = Invitation.objects.filter(code__startswith='QRTEST')
        if test_invitations.exists():
            print("\n有效测试邀请码:")
            for inv in test_invitations.filter(expires_at__gte=timezone.now(), used_count__lt=100):
                print(f"  - {inv.code} (剩余: {inv.get_remaining_uses()}次)")
    
    return invitations.count()

def main():
    """主函数"""
    print("===== QRent邀请码系统初始化 =====")
    
    # 运行数据库迁移
    run_migrations()
    
    # 检查已存在的邀请码
    existing_count = check_existing_invitations()
    
    # 如果没有测试邀请码，生成一些
    if not Invitation.objects.filter(code__startswith='QRTEST').exists():
        print("\n未找到测试邀请码，正在生成...")
        test_codes = generate_test_invitations()
        print("\n测试邀请码生成完成!")
    else:
        print("\n系统中已存在测试邀请码，无需重复生成。")
    
    print("\n===== 初始化完成 =====")
    print("\n使用说明:")
    print("1. 前端可以通过 /limits/invitation/validate/ 接口验证邀请码")
    print("2. 调用API时需要先验证邀请码，然后使用 /limits/report/create/ 接口创建报告")
    print("3. 管理员可以通过 /limits/invitation/generate/ 生成新的邀请码")
    print("4. 可以通过 /limits/export/invitations/ 导出邀请码数据")

if __name__ == '__main__':
    main()