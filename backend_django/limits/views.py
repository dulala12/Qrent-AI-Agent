import os
import json
import http.client
import random
import string
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Invitation, Report
from django.utils import timezone
import datetime

def generate_invitation_code():
    """生成邀请码"""
    # 前缀部分：QR加上当前年月日的缩写
    date_prefix = timezone.now().strftime("%Y%m%d")[:6]  # 取年月，如202305
    
    # 随机字符串部分：8位字母数字组合
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choices(chars, k=8))
    
    # 校验位：基于前两部分的简单校验
    check_str = date_prefix + random_str
    check_sum = sum(ord(c) for c in check_str) % 36
    check_char = string.ascii_uppercase + string.digits
    check_digit = check_char[check_sum]
    
    # 组合成最终邀请码，格式化为分组合（XXXX-XXXX-XXXX）
    code_parts = [date_prefix[:4], random_str[:4], random_str[4:] + check_digit]
    code = '-'.join(code_parts)
    
    return code

@csrf_exempt
def validate_invitation(request):
    """验证邀请码"""
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({'status': 'error', 'message': '邀请码不能为空'}, status=400)
        
        try:
            invitation = Invitation.objects.get(code=code)
            if invitation.is_valid():
                # 可以选择在这里立即增加使用次数，或者在实际生成报告时再增加
                # invitation.use()
                return JsonResponse({
                    'status': 'success', 
                    'message': '邀请码验证成功',
                    'code': code,
                    'remaining_uses': invitation.get_remaining_uses()
                })
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'邀请码已{invitation.get_status()}',
                    'status_detail': invitation.get_status()
                }, status=403)
        except Invitation.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '邀请码不存在'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

@csrf_exempt
def generate_new_invitation(request):
    """生成新的邀请码（管理接口）"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            max_uses = data.get('max_uses', 1)
            expires_days = data.get('expires_days', 30)
            
            # 生成唯一的邀请码
            while True:
                code = generate_invitation_code()
                if not Invitation.objects.filter(code=code).exists():
                    break
            
            # 创建邀请码记录
            expires_at = timezone.now() + datetime.timedelta(days=expires_days)
            invitation = Invitation.objects.create(
                code=code,
                expires_at=expires_at,
                max_uses=max_uses,
                used_count=0
            )
            
            return JsonResponse({
                'status': 'success',
                'code': code,
                'expires_at': invitation.expires_at.isoformat(),
                'max_uses': max_uses,
                'used_count': 0
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

@csrf_exempt
def create_report(request):
    """创建报告，同时验证和使用邀请码"""
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('invitation_code')
        report_data = data.get('report_data')
        
        if not code or not report_data:
            return JsonResponse({'status': 'error', 'message': '缺少必要参数'}, status=400)
        
        try:
            invitation = Invitation.objects.get(code=code)
            if invitation.use():
                # 创建报告
                report = Report.objects.create(
                    invitation_code=code,
                    report_data=report_data
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': '报告创建成功',
                    'report_id': report.report_id,
                    'remaining_uses': invitation.get_remaining_uses()
                })
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'邀请码已{invitation.get_status()}'
                }, status=403)
        except Invitation.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '邀请码不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

@csrf_exempt
def export_invitations(request):
    """导出邀请码数据"""
    if request.method == 'GET':
        try:
            invitations = Invitation.objects.all().order_by('-created_at')
            
            invitation_list = []
            for inv in invitations:
                invitation_list.append({
                    'code': inv.code,
                    'created_at': inv.created_at.isoformat(),
                    'expires_at': inv.expires_at.isoformat(),
                    'max_uses': inv.max_uses,
                    'used_count': inv.used_count,
                    'remaining_uses': inv.get_remaining_uses(),
                    'status': inv.get_status()
                })
            
            # 导出到文件
            export_path = os.path.join(settings.BASE_DIR, 'data', 'exported_invitations.json')
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(invitation_list, f, ensure_ascii=False, indent=2)
            
            return JsonResponse({
                'status': 'success',
                'count': len(invitation_list),
                'invitations': invitation_list,
                'export_path': export_path
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

@csrf_exempt
def export_reports(request):
    """导出报告数据"""
    if request.method == 'GET':
        try:
            reports = Report.objects.all().order_by('-created_at')
            
            report_list = []
            for report in reports:
                report_list.append({
                    'report_id': report.report_id,
                    'created_at': report.created_at.isoformat(),
                    'invitation_code': report.invitation_code,
                    'report_data': report.report_data
                })
            
            # 导出到文件
            export_path = os.path.join(settings.BASE_DIR, 'data', 'exported_reports.json')
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(report_list, f, ensure_ascii=False, indent=2)
            
            return JsonResponse({
                'status': 'success',
                'count': len(report_list),
                'export_path': export_path
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

@csrf_exempt
def create_test_invitation(request):
    """创建测试邀请码"""
    if request.method == 'POST':
        try:
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
            
            return JsonResponse({
                'status': 'success',
                'code': code,
                'expires_at': invitation.expires_at.isoformat(),
                'max_uses': 100
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

def fetch_and_save_limits_core():
    """核心逻辑，可被视图和定时任务调用"""
    conn = http.client.HTTPSConnection("api.qrent.rent")
    conn.request("GET", "/properties/region-summary?regions=zetland%20waterloo%20syd%20wolli")
    res = conn.getresponse()
    data = res.read()
    decoded = data.decode("utf-8")
    json_data = json.loads(decoded)

    processed_data = []
    for region in json_data.get("regions", []):
        processed_data.append({
            "region": region.get("region"),
            "avg_rent": region.get("averageWeeklyPrice"),
            "count": region.get("averageCommuteTime"),
        })

    save_path = os.path.join(settings.BASE_DIR, "data", "limits.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)

    return processed_data

@csrf_exempt
def fetch_and_save_limits(request):
    """Django 视图接口"""
    try:
        data = fetch_and_save_limits_core()
        return JsonResponse({"status": "success", "count": len(data), "preview": data[:2]})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def test_api(request):
    """测试API接口"""
    return JsonResponse({"status": "success", "message": "API is working"})

