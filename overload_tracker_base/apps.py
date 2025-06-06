from django.apps import AppConfig


class OverloadTrackerBaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'overload_tracker_base'
