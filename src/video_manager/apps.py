from django.apps import AppConfig


class VideoManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_manager'

    def ready(self) -> None:

        from . import signals
        
        return super().ready()