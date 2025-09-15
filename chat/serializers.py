from rest_framework import serializers
from .models import ChatConversation, ChatMessage, ChatOnlineStatus


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_display_name = serializers.ReadOnlyField()
    is_from_customer = serializers.ReadOnlyField()
    is_from_staff = serializers.ReadOnlyField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'conversation', 'sender', 'message_type', 'content',
            'file_attachment', 'is_read', 'is_edited', 'edited_at',
            'created_at', 'sender_display_name', 'is_from_customer', 'is_from_staff'
        ]
        read_only_fields = ['id', 'created_at', 'sender_display_name', 'is_from_customer', 'is_from_staff']


class ChatConversationSerializer(serializers.ModelSerializer):
    customer_display_name = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatConversation
        fields = [
            'id', 'customer', 'staff_member', 'subject', 'status', 'priority',
            'created_at', 'updated_at', 'last_message_at', 'closed_at',
            'customer_name', 'customer_email', 'customer_phone', 'tags',
            'notes', 'customer_display_name', 'is_active', 'messages'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer_display_name', 'is_active']


class ChatOnlineStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.ReadOnlyField()
    
    class Meta:
        model = ChatOnlineStatus
        fields = ['user', 'is_online', 'last_seen', 'status_message', 'status_display']
        read_only_fields = ['last_seen', 'status_display']
