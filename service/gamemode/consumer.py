import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer
from random import choice
from django.utils.timezone import now
from channels.generic.websocket import AsyncWebsocketConsumer
import random
from .models import Room, Message, WheelFortune, UserSpinHistory

from .serializers import MessageSerializer, RoomSerializer
from account.serializers import UserSerializer

from account.models import Account


class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"

    async def disconnect(self, code):
        if hasattr(self, "room_subscribe"):
            await self.remove_user_from_room(self.room_subscribe)
            await self.notify_users()
        await super().disconnect(code)

    @action()
    async def join_room(self, pk, **kwargs):
        self.room_subscribe = pk
        await self.add_user_to_room(pk)
        await self.notify_users()

    @database_sync_to_async
    def user_in_room(self, user, room_pk):
        return user.current_rooms.filter(pk=room_pk).exists()

    async def notify(self, result, user):
        room: Room = await self.get_room(self.room_subscribe)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    'type': 'roulette_result',
                    'result': result,
                    'user': "avocado",
                }
            )
    @action()
    async def spin_roulette(self, pk, **kwargs):
        # Получаем комнату и пользователя
        room: Room = await self.get_room(pk)
        user: Account = self.scope["user"]

        # Проверка: является ли пользователь участником комнаты
        if not await self.user_in_room(user, pk):
            await self.send_json({"error": "You are not part of this room"})
            return

        # Генерация результата рулетки
        roulette_segments = ['Red', 'Black', 'Green', 'Yellow']
        result = choice(roulette_segments)

        # Сохранение результата в комнате (опционально)
        #await self.save_roulette_result(room, result)
        await self.notify(result, user.username)
        # Рассылка результата участникам комнаты
        await self.channel_layer.group_send(
            f'room__{pk}',
            {
                'type': 'roulette_result',
                'result': result,
                'user': user.username,  # Кто инициировал
            }
        )

    @action()
    async def setBet_inspection(self, wager, bet_type, numbers, odds, pk, **kwargs):
        """
        Проверяет и обрабатывает ставку игрока.
        """
        user: Account = self.scope["user"]

        # Проверяем наличие комнаты
        try:
            room: Room = await self.get_room(pk)
        except Room.DoesNotExist:
            await self.send_json({"error": "Room not found."})
            return

        # Проверка, является ли пользователь участником комнаты
        if not await self.user_in_room(user, pk):
            await self.send_json({"error": "You are not part of this room."})
            return

        # Проверяем, переданы ли все необходимые данные
        if not all([wager, bet_type, numbers, odds]):
            await self.send_json({"error": "Missing required bet data."})
            return

        # Проверяем, достаточно ли средств у пользователя
        if str(user.balance) < wager:
            await self.send_json({"error": "Insufficient funds."})
            return

        # Обновляем баланс пользователя и создаем объект ставки
        balance = float(user.balance)
        balance -= float(wager)
        await database_sync_to_async(user.save)()

        await database_sync_to_async(Message.objects.create)(
            room=room,
            user=user,
            text=f"User {user.username} placed a bet: {wager} on {bet_type} ({numbers})"
        )

        # Возвращаем результат клиенту
        await self.send_json({
            "message": "Bet placed successfully.",
            "bet_details": {
                "wager": str(wager),
                "type": bet_type,
                "numbers": numbers,
                "odds": odds,
            },
            "balance": str(balance),
        })

    @action()
    async def spin_roulette_animate(self, winningSpin, pk, **kwargs):
        # Логика для вычисления победного вращения
        degree = None
        wheelnumbersAC = [0, 26, 3, 35, 12, 28, 7, 29, 18, 22, 9, 31, 14, 20, 1, 33, 16, 24, 5, 10, 23, 8, 30, 11, 36,
                          13, 27, 6, 34, 17, 25, 2, 21, 4, 19, 15, 32]

        for i in range(len(wheelnumbersAC)):
            if wheelnumbersAC[i] == winningSpin:
                degree = (i * 9.73) + 362
                break
                # Отправка события на клиент для выполнения анимации
        await self.send_json({
            'action': 'spin_roulette_result',
            'degree': degree,
        })


    async def roulette_result(self, event: dict):
        # Отправка результата клиентам
        await self.send_json({
            'action': 'roulette_result',
            'result': event['result'],
            'initiated_by': event['user']
        })

    @action()
    async def create_message(self, message, **kwargs):
        room: Room = await self.get_room(pk=self.room_subscribe)
        await database_sync_to_async(Message.objects.create)(
            room=room,
            user=self.scope["user"],
            text=message
        )


    @database_sync_to_async
    def save_roulette_result(self, room: Room, result: str):
        # Пример сохранения результата
        room.last_roulette_result = result
        room.save()

    @action()
    async def subscribe_to_messages_in_room(self, pk, **kwargs):
        await self.message_activity.subscribe(room=pk)

    @model_observer(Message)
    async def message_activity(self, message, observer=None, **kwargs):
        await self.send_json(message)

    @message_activity.groups_for_signal
    def message_activity(self, instance: Message, **kwargs):
        yield f'room__{instance.room_id}'
        yield f'pk__{instance.pk}'

    @message_activity.groups_for_consumer
    def message_activity(self, room=None, **kwargs):
        if room is not None:
            yield f'room__{room}'

    @message_activity.serializer
    def message_activity(self, instance: Message, action, **kwargs):
        return dict(data=MessageSerializer(instance).data, action=action.value, pk=instance.pk)

    async def notify_users(self):
        room: Room = await self.get_room(self.room_subscribe)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    'type': 'update_users',
                    'usuarios': await self.current_users(room)
                }
            )

    async def update_users(self, event: dict):
        await self.send(text_data=json.dumps({'usuarios': event["usuarios"]}))

    @database_sync_to_async
    def get_room(self, pk: int) -> Room:
        return Room.objects.get(pk=pk)

    @database_sync_to_async
    def current_users(self, room: Room):
        return [UserSerializer(user).data for user in room.current_users.all()]

    @database_sync_to_async
    def remove_user_from_room(self, room):
        user: Account = self.scope["user"]
        user.current_rooms.remove(room)

    @database_sync_to_async
    def add_user_to_room(self, pk):
        user: Account = self.scope["user"]
        if not user.current_rooms.filter(pk=self.room_subscribe).exists():
            user.current_rooms.add(Room.objects.get(pk=pk))

class WheelOfFortuneConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "wheel_of_fortune"
        self.room_group_name = f"game_{self.room_name}"
        self.user = self.scope['user']  # Убедитесь, что пользователь аутентифицирован

        # Подключение к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Отключение от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        data = json.loads(text_data)

        # Проверяем, авторизован ли пользователь
        if not self.user.is_authenticated:
            await self.send_error("User is not authenticated.")
            return

        # Проверяем действие
        if data.get('action') == 'spin':
            # Проверяем, есть ли у пользователя доступные спины
            try:
                wheel_fortune = await sync_to_async(WheelFortune.objects.get)(user_id=self.user.id)
                await sync_to_async(wheel_fortune.reset_spins_if_needed)()
            except WheelFortune.DoesNotExist:
                await self.send_error("No wheel fortune data for this user.")
                return

            if wheel_fortune.spins_left <= 0:
                await self.send_error("No spins left.")
                return

            # Используем спин
            if not await sync_to_async(wheel_fortune.use_spin)():
                await self.send_error("Failed to use spin.")
                return

            # Генерируем результат
            result = random.choice(['Prize 1', 'Prize 2', 'Prize 3', 'No Prize'])

            # Сохраняем результат в истории
            await sync_to_async(UserSpinHistory.objects.create)(
                user=self.user,
                result=result
            )

            # Отправляем результат пользователю
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'spin_result',
                    'result': result,
                }
            )

    async def spin_result(self, event):
        result = event['result']
        await self.send(text_data=json.dumps({
            'type': 'result',
            'result': result,
        }))

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

class UserConsumer(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.PatchModelMixin,
        mixins.UpdateModelMixin,
        mixins.CreateModelMixin,
        mixins.DeleteModelMixin,
        GenericAsyncAPIConsumer,
):

    queryset = Account.objects.all()
    serializer_class = UserSerializer
