from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Withdrawal, ReferralEarning

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'balance', 'referral_code', 'referral_earnings', 'created_at']

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['id', 'user', 'amount', 'method', 'crypto_type', 'status', 'created_at', 'updated_at']

class ReferralEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralEarning
        fields = ['id', 'referrer', 'referred_user', 'amount', 'created_at']
