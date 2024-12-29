from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'subscribed_at')
    list_filter = ('status', 'subscribed_at')
    #search_fields = ('subscriber__user', 'name')
    ordering = ('-subscribed_at',)


@admin.register(TelegramPost)
class TelegramPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'publish_at', 'created_at')
    list_filter = ('status', 'created_at', 'publish_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'status', 'error_message')

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'image', 'status')
        }),
        ('Schedule', {
            'fields': ('publish_at',),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('error_message', 'created_at'),
        }),
    )

    actions = ['publish_posts']

    @admin.action(description='Publish posts')
    def publish_posts(self, request, queryset):
        """
        Действие для публикации выбранных записей.
        """
        for post in queryset.filter(status='pending'):
            try:
                # post.publish_to_telegram()
                self.message_user(request, f'Запись "{post.title}" успешно опубликована.')
            except Exception as e:
                self.message_user(request, f'Ошибка при публикации "{post.title}": {str(e)}', level='error')

    publish_posts.short_description = "Опубликовать выбранные записи"