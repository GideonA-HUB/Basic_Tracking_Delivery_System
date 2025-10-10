from django.apps import AppConfig


class VipMembersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vip_members'
    verbose_name = 'VIP Members Management'
    
    def ready(self):
        try:
            import vip_members.signals  # noqa
        except ImportError:
            pass
