# survey/serializers.py
from rest_framework import serializers

class SurveySerializer(serializers.Serializer):
    budgetMin = serializers.CharField(required=False, allow_blank=True, default="")
    budgetMax = serializers.CharField(required=False, allow_blank=True, default="")
    billsIncluded = serializers.JSONField(required=False, allow_null=True)   # True/False/"unknown"/null
    furnished = serializers.JSONField(required=False, allow_null=True)       # True/False/"unknown"/null
    weeklyTotal = serializers.CharField(required=False, allow_blank=True, default="")
    propertyType = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    coRent = serializers.ChoiceField(choices=["yes","no","maybe"], required=False, allow_null=True)
    commute = serializers.ChoiceField(choices=["15","30","45","60",">60","none"], required=False, allow_null=True)
    moveIn = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # ISO date string
    leaseMonths = serializers.CharField(required=False, allow_blank=True, default="")
    acceptOverpriced = serializers.ChoiceField(choices=["yes","no","depends"], required=False, allow_null=True)
    acceptSmall = serializers.ChoiceField(choices=["yes","no","depends"], required=False, allow_null=True)
