from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import datetime, timedelta
from .models import (InvestmentPlan, ActiveInvestment, WithdrawHistory, 
                     CopyTradingProfile, CopyTradingFollower, CryptoSwap, 
                     PaymentConfirmation)
from .serializers import (InvestmentPlanSerializer, ActiveInvestmentSerializer, 
                          WithdrawHistorySerializer)

class InvestmentPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InvestmentPlan.objects.filter(is_active=True)
    serializer_class = InvestmentPlanSerializer
    permission_classes = []

class ActiveInvestmentViewSet(viewsets.ModelViewSet):
    queryset = ActiveInvestment.objects.all()
    serializer_class = ActiveInvestmentSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        user_profile = request.user.profile
        plan_id = request.data.get('plan_id')
        amount = request.data.get('amount')
        
        try:
            plan = InvestmentPlan.objects.get(id=plan_id)
        except InvestmentPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if float(amount) < float(plan.min_amount) or float(amount) > float(plan.max_amount):
            return Response({'error': 'Amount not within plan range'}, status=status.HTTP_400_BAD_REQUEST)
        
        if float(user_profile.balance) < float(amount):
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        
        end_date = datetime.now() + timedelta(days=plan.duration_days)
        investment = ActiveInvestment.objects.create(
            user=user_profile,
            plan=plan,
            amount=amount,
            end_date=end_date
        )
        
        user_profile.balance -= float(amount)
        user_profile.save()
        
        return Response({
            'message': 'Investment created successfully',
            'investment': ActiveInvestmentSerializer(investment).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_investments(self, request):
        user_profile = request.user.profile
        investments = ActiveInvestment.objects.filter(user=user_profile)
        serializer = self.get_serializer(investments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def update_earnings(self, request):
        user_profile = request.user.profile
        investments = ActiveInvestment.objects.filter(user=user_profile, status='active')
        
        total_earned = 0
        for investment in investments:
            earned = investment.calculate_earnings()
            total_earned += earned
        
        user_profile.balance += total_earned
        user_profile.save()
        
        return Response({
            'message': 'Earnings updated',
            'total_earned': total_earned
        }, status=status.HTTP_200_OK)

class WithdrawHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WithdrawHistory.objects.all()
    serializer_class = WithdrawHistorySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_history(self, request):
        user_profile = request.user.profile
        history = WithdrawHistory.objects.filter(user=user_profile)
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)


class CopyTradingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def top_traders(self, request):
        """Get list of available top traders"""
        profiles = CopyTradingProfile.objects.filter(is_available=True).select_related('trader')
        traders = []
        for profile in profiles:
            traders.append({
                'id': str(profile.id),
                'trader_name': profile.trader.user.username,
                'copy_fee_percentage': profile.copy_fee_percentage,
                'follower_count': profile.follower_count,
                'total_copied_value': profile.total_copied_value
            })
        return Response(traders)
    
    @action(detail=False, methods=['get'])
    def my_allocations(self, request):
        """Get user's copy trading allocations"""
        user_profile = request.user.profile
        followers = CopyTradingFollower.objects.filter(follower=user_profile, is_active=True)
        allocations = []
        for follower in followers:
            allocations.append({
                'id': str(follower.id),
                'trader_name': follower.copy_trading_profile.trader.user.username,
                'allocated_amount': follower.allocated_amount,
                'fee_percentage': follower.copy_trading_profile.copy_fee_percentage
            })
        return Response(allocations)
    
    @action(detail=False, methods=['post'])
    def follow(self, request):
        """Start copying a trader"""
        try:
            user_profile = request.user.profile
            profile_id = request.data.get('copy_trading_profile_id')
            amount = float(request.data.get('allocated_amount', 0))
            
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
            
            copy_profile = CopyTradingProfile.objects.get(id=profile_id)
            
            if CopyTradingFollower.objects.filter(follower=user_profile, copy_trading_profile=copy_profile, is_active=True).exists():
                return Response({'error': 'Already following this trader'}, status=status.HTTP_400_BAD_REQUEST)
            
            follower = CopyTradingFollower.objects.create(
                follower=user_profile,
                copy_trading_profile=copy_profile,
                allocated_amount=amount
            )
            
            copy_profile.follower_count += 1
            copy_profile.save()
            
            return Response({
                'message': 'Now copying trader',
                'follower_id': str(follower.id)
            }, status=status.HTTP_201_CREATED)
        except CopyTradingProfile.DoesNotExist:
            return Response({'error': 'Trader not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CryptoSwapViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Perform crypto swap"""
        try:
            user_profile = request.user.profile
            from_crypto = request.data.get('from_crypto')
            to_crypto = request.data.get('to_crypto')
            from_amount = float(request.data.get('from_amount', 0))
            
            if from_crypto == to_crypto:
                return Response({'error': 'Cannot swap same currency'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Simple 1:1 rate for demo (in production, use real exchange rates)
            to_amount = from_amount
            fee = to_amount * 0.01  # 1% fee
            final_amount = to_amount - fee
            
            swap = CryptoSwap.objects.create(
                user=user_profile,
                from_crypto=from_crypto,
                to_crypto=to_crypto,
                from_amount=from_amount,
                to_amount=final_amount,
                exchange_rate=1.0
            )
            
            return Response({
                'message': 'Swap completed',
                'swap_id': str(swap.id),
                'to_amount': final_amount
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_swaps(self, request):
        """Get user's swap history"""
        user_profile = request.user.profile
        swaps = CryptoSwap.objects.filter(user=user_profile).order_by('-created_at')
        swap_list = []
        for swap in swaps:
            swap_list.append({
                'id': str(swap.id),
                'from_crypto': swap.from_crypto,
                'to_crypto': swap.to_crypto,
                'from_amount': swap.from_amount,
                'to_amount': swap.to_amount,
                'fee_percentage': swap.fee_percentage,
                'status': swap.status,
                'created_at': swap.created_at.isoformat()
            })
        return Response(swap_list)
