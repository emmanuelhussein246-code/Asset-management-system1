from django.apps import AppConfig

class AssetsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assets_app'
    verbose_name = 'Swahilipot Asset Management'

    def ready(self):
        import assets_app.signals  # noqa: F401 — register signal handlers
