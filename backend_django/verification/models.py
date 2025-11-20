# verification/models.py - 验证码和邀请码相关的模型
from django.db import models
from django.utils import timezone
import datetime

class Invitation(models.Model):
    """邀请码模型"""
    code = models.CharField(max_length=20, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    max_uses = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    
    def is_valid(self):
        """检查邀请码是否有效"""
        now = timezone.now()
        return now <= self.expires_at and self.used_count < self.max_uses
    
    def use(self):
        """使用邀请码"""
        if self.is_valid():
            self.used_count += 1
            self.save()
            return True
        return False
    
    def get_status(self):
        """获取邀请码状态"""
        now = timezone.now()
        if now > self.expires_at:
            return "已过期"
        elif self.used_count >= self.max_uses:
            return "已用完"
        else:
            return "有效"
    
    def get_remaining_uses(self):
        """获取剩余使用次数"""
        return max(0, self.max_uses - self.used_count)
    
    def __str__(self):
        return self.code

class Report(models.Model):
    """报告模型"""
    report_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    invitation_code = models.CharField(max_length=20)
    report_data = models.JSONField()
    
    def __str__(self):
        return f"Report {self.report_id} ({self.invitation_code})"