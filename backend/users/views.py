from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout  # ← added login, logout
import random
import string
from .models import UserProfile, Withdrawal, ReferralEarning, ImportedWallet
from .serializers import UserSerializer, UserProfileSerializer, WithdrawalSerializer, ReferralEarningSerializer


class UserRegistrationView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        try:
            username = request.data.get('username', '').strip()
            password = request.data.get('password', '').strip()
            transaction_pin = request.data.get('transaction_pin', '').strip()
            referral_code = request.data.get('referral_code', None)

            # Validate inputs
            if not username or not password or not transaction_pin:
                return Response(
                    {'error': 'Username, password, and PIN are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(transaction_pin) != 4 or not transaction_pin.isdigit():
                return Response(
                    {'error': 'Transaction PIN must be 4 digits'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(password) < 4:
                return Response(
                    {'error': 'Password must be at least 4 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(username=username).exists():
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user
            user = User.objects.create_user(username=username, password=password)

            # Generate unique referral code
            referral_code_unique = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )

            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                transaction_pin=transaction_pin,
                referral_code=referral_code_unique
            )

            # Handle referral
            if referral_code:
                try:
                    referred_profile = UserProfile.objects.get(referral_code=referral_code)
                    profile.referred_by = referred_profile
                    profile.save()
                except UserProfile.DoesNotExist:
                    pass  # Invalid referral code — silently ignore

            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username,
                'referral_code': referral_code_unique
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Registration failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def login(self, request):
        try:
            username = request.data.get('username', '').strip()
            password = request.data.get('password', '').strip()

            if not username or not password:
                return Response(
                    {'error': 'Username and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is None:
                return Response(
                    {'error': 'Invalid username or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # ✅ Create Django session — this is what LoginRequiredMixin checks
            login(request, user)

            # Get profile
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                return Response(
                    {'error': 'User profile not found'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'profile': UserProfileSerializer(profile).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Login failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        ✅ New: Clears the Django session on logout
        Call this from your JS logout button
        """
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify user exists for password reset"""
        try:
            username = request.data.get('username', '').strip()
            email = request.data.get('email', '').strip()
            
            user = User.objects.filter(username=username, email=email).first()
            if user:
                return Response({'message': 'User verified'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Reset user password"""
        try:
            username = request.data.get('username', '').strip()
            email = request.data.get('email', '').strip()
            new_password = request.data.get('new_password', '')
            
            if not new_password or len(new_password) < 4:
                return Response(
                    {'error': 'Password must be at least 4 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = User.objects.filter(username=username, email=email).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        user_profile = request.user.profile
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        withdrawal = serializer.save(user=user_profile)

        return Response({
            'message': 'Withdrawal request submitted. Processing within 10-30 minutes',
            'withdrawal': WithdrawalSerializer(withdrawal).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def history(self, request):
        user_profile = request.user.profile
        withdrawals = Withdrawal.objects.filter(user=user_profile)
        serializer = self.get_serializer(withdrawals, many=True)
        return Response(serializer.data)


class ReferralViewSet(viewsets.ModelViewSet):
    queryset = ReferralEarning.objects.all()
    serializer_class = ReferralEarningSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_referrals(self, request):
        user_profile = request.user.profile
        referrals = ReferralEarning.objects.filter(referrer=user_profile)
        serializer = self.get_serializer(referrals, many=True)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """User profile operations - password and PIN changes"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        try:
            username = request.data.get('username')
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            
            user = authenticate(username=username, password=old_password)
            if user is None:
                return Response({'error': 'Current password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_pin(self, request):
        """Update transaction PIN"""
        try:
            username = request.data.get('username')
            current_pin = request.data.get('current_pin')
            new_pin = request.data.get('new_pin')
            
            user = User.objects.get(username=username)
            profile = user.profile
            
            if profile.transaction_pin != current_pin:
                return Response({'error': 'Current PIN is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if len(new_pin) != 4 or not new_pin.isdigit():
                return Response({'error': 'PIN must be 4 digits'}, status=status.HTTP_400_BAD_REQUEST)
            
            profile.transaction_pin = new_pin
            profile.save()
            
            return Response({'message': 'PIN updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImportedWalletViewSet(viewsets.ModelViewSet):
    """Handle wallet importation"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def import_wallet(self, request):
        """Import external wallet"""
        try:
            user_profile = request.user.profile
            wallet_type = request.data.get('wallet_type')
            wallet_address = request.data.get('wallet_address')
            
            if not wallet_type or not wallet_address:
                return Response({'error': 'Wallet type and address required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if ImportedWallet.objects.filter(user=user_profile, wallet_address=wallet_address).exists():
                return Response({'error': 'Wallet already imported'}, status=status.HTTP_400_BAD_REQUEST)
            
            wallet = ImportedWallet.objects.create(
                user=user_profile,
                wallet_address=wallet_address,
                wallet_type=wallet_type,
                is_verified=False
            )
            
            return Response({
                'message': 'Wallet imported. Pending verification.',
                'wallet_id': str(wallet.id)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_wallets(self, request):
        """Get user's imported wallets"""
        try:
            user_profile = request.user.profile
            wallets = ImportedWallet.objects.filter(user=user_profile)
            wallet_list = []
            for wallet in wallets:
                wallet_list.append({
                    'id': str(wallet.id),
                    'wallet_type': wallet.wallet_type,
                    'wallet_address': wallet.wallet_address,
                    'is_verified': wallet.is_verified,
                    'created_at': wallet.created_at.isoformat()
                })
            return Response(wallet_list)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)