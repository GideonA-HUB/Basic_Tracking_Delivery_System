from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import VIPMember, VIPActivity


@receiver(post_save, sender=VIPMember)
def create_vip_member_activity(sender, instance, created, **kwargs):
    """Create activity log when VIP member is created or updated"""
    if created:
        VIPActivity.objects.create(
            member=instance,
            activity_type='other',
            title='VIP Membership Created',
            description=f'VIP membership created with {instance.get_membership_tier_display()} tier'
        )
    else:
        VIPActivity.objects.create(
            member=instance,
            activity_type='other',
            title='VIP Profile Updated',
            description=f'VIP profile information updated'
        )
