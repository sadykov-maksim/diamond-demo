from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(WithdrawalMethod)
class WithdrawalMethodAdmin(admin.ModelAdmin):
    pass
@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    pass

@admin.register(BankTransferOption)
class BankTransferOptionAdmin(admin.ModelAdmin):
    pass

@admin.register(CryptoTransferOption)
class CryptoOptionAdmin(admin.ModelAdmin):
    pass