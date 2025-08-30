from django.apps import AppConfig


class InvestmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'investments'
    verbose_name = 'Investment Management'
    
    def ready(self):
        """Initialize app when ready"""
        try:
            import investments.signals
        except ImportError:
            pass
