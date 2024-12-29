from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    pass

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'helpful_count', 'not_helpful_count', 'helpful_percentage')
    search_fields = ('question', 'answer')
    readonly_fields = ('helpful_percentage',)  # Чтобы процент был только для чтения

    def helpful_percentage(self, obj):
        """Отображение процента полезности в админке."""
        total = obj.helpful_count + obj.not_helpful_count
        if total == 0:
            return "0%"
        return f"{(obj.helpful_count / total) * 100:.2f}%"
    helpful_percentage.short_description = "Процент полезности"

@admin.register(FAQFeedback)
class FAQFeedbackAdmin(admin.ModelAdmin):
    pass

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    pass