from rest_framework import serializers
from .models import Bet, UserBalance, Room, Message, WheelFortune, UserSpinHistory
from account.serializers import UserSerializer


class BetSerializer(serializers.ModelSerializer):
    # Дополнительно можно создать вычисляемые поля, например, для отображения коэффициента
    # и состояния ставки, если это нужно.

    class Meta:
        model = Bet
        fields = '__all__'  # Или указываем конкретные поля, которые нужно включить, например:
        # fields = ['id', 'user', 'bet_type', 'numbers', 'amount', 'result', 'payout', 'coefficient', 'created_at']

    def validate_amount(self, value):
        """Проверка ставки (например, она должна быть больше 0)."""
        if value <= 0:
            raise serializers.ValidationError("Ставка должна быть больше 0.")
        return value

    def validate_numbers(self, value):
        """Проверка чисел для ставки (например, их количество в зависимости от типа ставки)."""
        bet_type = self.initial_data.get('bet_type')
        if bet_type == 'straight_up' and len(value) != 1:
            raise serializers.ValidationError("Для Straight Up должно быть одно число.")
        elif bet_type == 'split' and len(value) != 2:
            raise serializers.ValidationError("Для Split должно быть два числа.")
        # Добавьте аналогичные проверки для других типов ставок (street, corner и т.д.)

class UserBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalance
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = Message
        exclude = []
        depth = 1

    def get_created_at_formatted(self, obj:Message):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")

class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ["pk", "name", "host", "messages", "current_users", "last_message"]
        depth = 1
        read_only_fields = ["messages", "last_message"]

    def get_last_message(self, obj:Room):
        return MessageSerializer(obj.messages.order_by('created_at').last()).data


class WheelFortuneSerializer(serializers.ModelSerializer):
    user = UserSerializer

    class Meta:
        model = WheelFortune
        fields = ['id', 'user', 'spins_left', 'last_spin_date']
        read_only_fields = ['id', 'last_spin_date']

class UserSpinHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSpinHistory
        fields = ['user', 'room', 'result', 'created_at']