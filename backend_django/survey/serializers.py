# survey/serializers.py
from rest_framework import serializers

class SurveySerializer(serializers.Serializer):
    # 前端实际提交的键名
    minBudget = serializers.CharField(required=False, allow_blank=True, default="")
    maxBudget = serializers.CharField(required=False, allow_blank=True, default="")
    includeBills = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # "包含"/"不包含"/"不确定"
    university = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    commuteTime = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # "15 分钟"/"30 分钟"等
    roomType = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # "Studio"/"一居室"等
    sharedRoom = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # "愿意"/"不愿意"等
    moveInDate = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    leaseTerm = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # "6 个月"/"12 个月"等
    flexibility = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
