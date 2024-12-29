from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    pass

@admin.register(GameHistory)
class GameHistoryAdmin(admin.ModelAdmin):
    pass

@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    pass
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    pass


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    pass

@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass

class ItemInline(admin.TabularInline):
    model = Item
    extra = 1  # Количество пустых строк для добавления новых предметов

class ItemGroupInline(admin.TabularInline):
    model = ItemGroup
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ItemGroupInline]  # Группы показываются прямо в категории

@admin.register(ItemGroup)
class ItemGroupAdmin(admin.ModelAdmin):
    inlines = [ItemInline]  # Предметы показываются внутри группы

