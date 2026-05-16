from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Withdrawal, ReferralEarning, ImportedWallet

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = fields

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    referred_by_code = serializers.CharField(source='referred_by.referral_code', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'balance',
            'referral_code',
            'referral_earnings',
            'referred_by_code',
            'created_at',
        ]

class WithdrawalSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.user.username', read_only=True)

    class Meta:
        model = Withdrawal
        fields = [
            'id',
            'user',
            'username',
            'amount',
            'method',
            'crypto_type',
            'network',
            'bank_details',
            'wallet_address',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'username', 'status', 'created_at', 'updated_at']

class ReferralEarningSerializer(serializers.ModelSerializer):
    referrer_username = serializers.CharField(source='referrer.user.username', read_only=True)
    referred_username = serializers.CharField(source='referred_user.user.username', read_only=True)

    class Meta:
        model = ReferralEarning
        fields = [
            'id',
            'referrer',
            'referrer_username',
            'referred_user',
            'referred_username',
            'amount',
            'created_at',
        ]


class ImportedWalletSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.user.username', read_only=True)

    class Meta:
        model = ImportedWallet
        fields = [
            'id',
            'user',
            'username',
            'wallet_address',
            'wallet_type',
            'is_verified',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'username', 'is_verified', 'created_at']
