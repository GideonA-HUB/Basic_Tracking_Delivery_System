from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ChatConversation, ChatMessage, ChatTypingIndicator, 
    ChatOnlineStatus, ChatSettings
)


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_display_name', 'subject', 'status', 'priority',
        'staff_member', 'created_at', 'last_message_at', 'unread_count'
    ]
    list_filter = ['status', 'priority', 'created_at', 'staff_member']
    search_fields = ['id', 'customer_name', 'customer_email', 'subject', 'customer__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_message_at', 'closed_at']
    raw_id_fields = ['customer', 'staff_member']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'customer', 'staff_member', 'subject', 'status', 'priority')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_message_at', 'closed_at'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('tags', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def unread_count(self, obj):
        count = obj.messages.filter(is_read=False, sender__is_staff=False).count()
        if count > 0:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', count)
        return count
    unread_count.short_description = 'Unread Messages'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'staff_member')
    
    actions = ['assign_to_me', 'close_conversations', 'mark_as_resolved']
    
    def assign_to_me(self, request, queryset):
        updated = queryset.update(staff_member=request.user, status='active')
        self.message_user(request, f'{updated} conversations assigned to you.')
    assign_to_me.short_description = 'Assign selected conversations to me'
    
    def close_conversations(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} conversations closed.')
    close_conversations.short_description = 'Close selected conversations'
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f'{updated} conversations marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected conversations as resolved'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'conversation_link', 'sender_display_name', 'message_type',
        'content_preview', 'is_read', 'created_at'
    ]
    list_filter = ['message_type', 'is_read', 'is_edited', 'created_at', 'sender__is_staff']
    search_fields = ['content', 'conversation__id', 'sender__username', 'sender__first_name', 'sender__last_name']
    readonly_fields = ['id', 'created_at', 'edited_at']
    raw_id_fields = ['conversation', 'sender']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('id', 'conversation', 'sender', 'message_type', 'content')
        }),
        ('File Attachment', {
            'fields': ('file_attachment',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_edited', 'edited_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def conversation_link(self, obj):
        url = reverse('admin:chat_chatconversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">{}</a>', url, obj.conversation.id)
    conversation_link.short_description = 'Conversation'
    conversation_link.admin_order_field = 'conversation__id'
    
    def content_preview(self, obj):
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return format_html('<span title="{}">{}</span>', obj.content, preview)
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation', 'sender')
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'


@admin.register(ChatTypingIndicator)
class ChatTypingIndicatorAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'user', 'is_typing', 'last_typing_at']
    list_filter = ['is_typing', 'last_typing_at']
    search_fields = ['conversation__id', 'user__username']
    raw_id_fields = ['conversation', 'user']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation', 'user')


@admin.register(ChatOnlineStatus)
class ChatOnlineStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online', 'status_message', 'last_seen']
    list_filter = ['is_online', 'last_seen']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'status_message']
    raw_id_fields = ['user']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['set_online', 'set_offline']
    
    def set_online(self, request, queryset):
        updated = queryset.update(is_online=True)
        self.message_user(request, f'{updated} staff members set to online.')
    set_online.short_description = 'Set selected staff as online'
    
    def set_offline(self, request, queryset):
        updated = queryset.update(is_online=False)
        self.message_user(request, f'{updated} staff members set to offline.')
    set_offline.short_description = 'Set selected staff as offline'


@admin.register(ChatSettings)
class ChatSettingsAdmin(admin.ModelAdmin):
    list_display = ['is_enabled', 'business_hours_enabled', 'auto_response_enabled', 'notification_email']
    
    fieldsets = (
        ('General Settings', {
            'fields': ('is_enabled', 'welcome_message', 'offline_message')
        }),
        ('Business Hours', {
            'fields': ('business_hours_enabled', 'business_hours_start', 'business_hours_end', 'business_days'),
            'classes': ('collapse',)
        }),
        ('Auto Responses', {
            'fields': ('auto_response_enabled', 'auto_response_delay', 'auto_response_message'),
            'classes': ('collapse',)
        }),
        ('File Upload Settings', {
            'fields': ('max_file_size', 'allowed_file_types'),
            'classes': ('collapse',)
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'notification_email'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not ChatSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


# Customize admin site headers
admin.site.site_header = "Meridian Asset Logistics - Chat Administration"
admin.site.site_title = "MAL Chat Admin"
admin.site.index_title = "Live Chat System Management"
