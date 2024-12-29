from rest_framework import serializers
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Bet, UserBalance, WheelFortune
from .serializers import BetSerializer, UserBalanceSerializer, WheelFortuneSerializer
from .roulette_logic import play_roulette

class UserBalanceViewSet(viewsets.ModelViewSet):
    queryset = UserBalance.objects.all()
    serializer_class = UserBalanceSerializer

class RouletteViewSet(viewsets.ModelViewSet):
    """
    ViewSet для ставок в рулетке.
    """
    serializer_class = BetSerializer
    queryset = Bet.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает ставки текущего пользователя.
        """
        return Bet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Логика создания ставки с обработкой баланса и результата.
        """
        user = self.request.user
        balance = UserBalance.objects.get(user=user)
        bet_amount = serializer.validated_data['amount']

        # Проверяем баланс пользователя
        if balance.balance < bet_amount:
            raise serializers.ValidationError("Недостаточно средств на счете.")

        # Списываем средства
        balance.balance -= bet_amount
        balance.save()

        # Создаем объект ставки
        bet = serializer.save(user=user)

        # Играем в рулетку
        rolled_number, rolled_color, payout = play_roulette(bet)

        # Обновляем результат ставки
        bet.result = rolled_color
        bet.payout = payout
        bet.save()

        # Если пользователь выиграл, зачисляем выигрыш
        if payout > 0:
            balance.balance += payout
            balance.save()

class WheelFortuneViewSet(viewsets.ModelViewSet):
    queryset = WheelFortune.objects.all()
    serializer_class = WheelFortuneSerializer