from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    pass

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    pass

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass

@admin.register(WheelFortune)
class WheelFortuneAdmin(admin.ModelAdmin):
    list_display = ('user', 'spins_left', 'last_spin_date')
    list_filter = ('last_spin_date',)
    search_fields = ('user__username',)
    ordering = ('-last_spin_date',)

    def get_queryset(self, request):
        """
        Переопределяем queryset, чтобы загружать связанные данные для оптимизации.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')

@admin.register(UserSpinHistory)
class UserSpinHistoryAdmin(admin.ModelAdmin):
    pass