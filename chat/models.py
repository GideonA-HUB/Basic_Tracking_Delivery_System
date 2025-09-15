from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatConversation(models.Model):
    """Model for chat conversations between customers and staff"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('waiting', 'Waiting for Staff'),
        ('closed', 'Closed'),
        ('resolved', 'Resolved'),
    ]
    
    # Basic conversation info
    id = models.CharField(max_length=100, primary_key=True)  # UUID for frontend
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_conversations')
    staff_member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_conversations')
    
    # Conversation details
    subject = models.CharField(max_length=200, default='General Inquiry')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Customer info (for non-authenticated users)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Additional info
    tags = models.JSONField(default=list, blank=True)  # For categorizing conversations
    notes = models.TextField(blank=True)  # Staff notes
    
    class Meta:
        ordering = ['-last_message_at', '-created_at']
        verbose_name = 'Chat Conversation'
        verbose_name_plural = 'Chat Conversations'
    
    def __str__(self):
        return f"Chat {self.id} - {self.customer_name or self.customer.username}"
    
    @property
    def is_active(self):
        return self.status in ['active', 'waiting']
    
    @property
    def customer_display_name(self):
        if self.customer_name:
            return self.customer_name
        elif self.customer:
            return self.customer.get_full_name() or self.customer.username
        return 'Anonymous'
    
    def assign_to_staff(self, staff_member):
        """Assign conversation to a staff member"""
        self.staff_member = staff_member
        self.status = 'active'
        self.save()
    
    def close_conversation(self):
        """Close the conversation"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()


class ChatMessage(models.Model):
    """Model for individual chat messages"""
    
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System Message'),
    ]
    
    # Basic message info
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Message content
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    
    # Message metadata
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation.id}"
    
    @property
    def sender_display_name(self):
        if self.sender.is_staff:
            return f"Staff - {self.sender.get_full_name() or self.sender.username}"
        else:
            return self.conversation.customer_display_name
    
    @property
    def is_from_customer(self):
        return not self.sender.is_staff
    
    @property
    def is_from_staff(self):
        return self.sender.is_staff


class ChatTypingIndicator(models.Model):
    """Model to track typing indicators"""
    
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='typing_indicators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)
    last_typing_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['conversation', 'user']
        verbose_name = 'Typing Indicator'
        verbose_name_plural = 'Typing Indicators'
    
    def __str__(self):
        return f"{self.user.username} typing in {self.conversation.id}"


class ChatOnlineStatus(models.Model):
    """Model to track online status of staff members"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_online_status')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    status_message = models.CharField(max_length=100, blank=True, default='Available')
    
    class Meta:
        verbose_name = 'Online Status'
        verbose_name_plural = 'Online Statuses'
    
    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"
    
    @property
    def status_display(self):
        if self.is_online:
            return self.status_message or 'Available'
        return 'Offline'


class ChatSettings(models.Model):
    """Model for chat system settings"""
    
    # General settings
    is_enabled = models.BooleanField(default=True)
    welcome_message = models.TextField(default="Hello! How can we help you today?")
    offline_message = models.TextField(default="We're currently offline. Please leave a message and we'll get back to you soon!")
    
    # Business hours
    business_hours_enabled = models.BooleanField(default=False)
    business_hours_start = models.TimeField(default='09:00')
    business_hours_end = models.TimeField(default='17:00')
    business_days = models.JSONField(default=list)  # List of weekdays (0-6)
    
    # Auto-responses
    auto_response_enabled = models.BooleanField(default=True)
    auto_response_delay = models.IntegerField(default=30)  # seconds
    auto_response_message = models.TextField(default="Thank you for your message. A staff member will be with you shortly.")
    
    # File upload settings
    max_file_size = models.IntegerField(default=10)  # MB
    allowed_file_types = models.JSONField(default=list)  # List of allowed extensions
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    notification_email = models.EmailField(default='support@meridianassetlogistics.com')
    
    class Meta:
        verbose_name = 'Chat Settings'
        verbose_name_plural = 'Chat Settings'
    
    def __str__(self):
        return 'Chat Settings'
    
    @classmethod
    def get_settings(cls):
        """Get or create chat settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
