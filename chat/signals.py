from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ChatMessage, ChatConversation


@receiver(post_save, sender=ChatMessage)
def update_conversation_last_message(sender, instance, created, **kwargs):
    """Update conversation's last message timestamp when a new message is created"""
    if created:
        instance.conversation.last_message_at = timezone.now()
        instance.conversation.save(update_fields=['last_message_at'])
        
        # Mark conversation as active if it was waiting
        if instance.conversation.status == 'waiting':
            instance.conversation.status = 'active'
            instance.conversation.save(update_fields=['status'])
