# verification/views.py - 验证码和邀请码相关的视图
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
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)

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
        try:
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
        except Exception as e:
            logger.error(f"验证邀请码时发生错误: {str(e)}")
            return JsonResponse({'status': 'error', 'message': '服务器内部错误'}, status=500)
    
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
            logger.error(f"生成邀请码时发生错误: {str(e)}")
            return JsonResponse({'status': 'error', 'message': '生成邀请码失败'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

@csrf_exempt
def get_invitation_status(request, code):
    """获取邀请码状态（公开接口）"""
    try:
        invitation = Invitation.objects.get(code=code)
        return JsonResponse({
            'status': 'success',
            'is_valid': invitation.is_valid(),
            'status_text': invitation.get_status(),
            'remaining_uses': invitation.get_remaining_uses(),
            'expires_at': invitation.expires_at.isoformat()
        })
    except Invitation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '邀请码不存在'}, status=404)
    except Exception as e:
        logger.error(f"获取邀请码状态时发生错误: {str(e)}")
        return JsonResponse({'status': 'error', 'message': '服务器内部错误'}, status=500)