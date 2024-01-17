from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Конфигурация приложения АПИ."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Интерфейс программирования приложения'
