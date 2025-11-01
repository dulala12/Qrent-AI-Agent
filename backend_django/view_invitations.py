#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看所有生成的邀请码脚本
"""
import requests
import json

def view_invitations():
    """调用API查看所有邀请码"""
    try:
        print("正在查询所有邀请码...")
        # 调用后端API
        response = requests.get(
            "http://127.0.0.1:8000/limits/export/invitations/",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"\n成功获取到 {data['count']} 个邀请码")
                print("=" * 80)
                print(f"{'邀请码':<25} {'状态':<10} {'创建时间':<25} {'剩余次数':<10}")
                print("=" * 80)
                
                for invitation in data['invitations']:
                    status = invitation['status']
                    created_date = invitation['created_at'].split('T')[0]
                    print(f"{invitation['code']:<25} {status:<10} {created_date:<25} {invitation['remaining_uses']:<10}")
                
                print("=" * 80)
                print(f"\n详细信息已导出到: {data['export_path']}")
            else:
                print(f"获取失败: {data.get('message', '未知错误')}")
        else:
            print(f"API调用失败，状态码: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误信息: {error_data.get('message', '未知错误')}")
            except:
                print("无法解析错误信息")
    
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务器，请确保Django服务器正在运行")
        print("请先运行: python manage.py runserver")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")

def check_url_config():
    """检查URL配置"""
    print("提示: 已配置的URL路径:")
    print("path('export/invitations/', views.export_invitations, name='export_invitations'),")

if __name__ == "__main__":
    print("======== QRent 邀请码查看工具 ========")
    view_invitations()
    check_url_config()
    print("\n使用说明:")
    print("1. 确保Django服务器正在运行")
    print("2. 直接运行本脚本查看所有邀请码")
    print("3. 测试邀请码格式通常为: QRTEST-XXXXXXXX")